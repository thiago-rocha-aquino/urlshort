# Arquitetura

## Visao geral

Clean Architecture / Hexagonal — domínio puro no centro, frameworks nas bordas.

Diferencas em relacao ao projeto irmao (api_financa): foco em **performance** e **escala** em vez de logica de negocio rica. Cache (Redis), filas assincronas (Redis Streams) e analytics granulares sao cidadaos de primeira classe.

```mermaid
flowchart TB
    cli([Cliente HTTP]) --> api

    subgraph presentation [Presentation - FastAPI]
        api[Rotas]
        rl[Rate limit middleware]
    end

    subgraph application [Application - Use Cases]
        uc[create / list / redirect / analytics]
    end

    subgraph domain [Domain - Nucleo puro]
        ent[ShortUrl, ClickEvent, UrlStats]
        vo[Slug, Url]
        svc[SlugGenerator, ClickAnalyzer, UrlValidator]
        ports[Ports / Protocols]
    end

    subgraph infrastructure [Infrastructure - Adapters]
        db[(Postgres)]
        cache[(Redis cache)]
        stream[(Redis Streams)]
        geo[MaxMind]
    end

    api --> uc
    rl -.consulta.-> cache
    uc --> svc
    uc -.depende.-> ports
    db -.implementa.-> ports
    cache -.implementa.-> ports
    stream -.implementa.-> ports
    geo -.implementa.-> ports

    worker[Worker async] -.consome.-> stream
    worker --> db
```

## Fluxo de redirect (caminho quente)

1. `GET /{slug}` chega
2. Cache Redis: `slug -> target_url`. Se hit -> 301/302 imediato (target ~5ms)
3. Cache miss -> consulta Postgres -> popula cache -> 301/302
4. Em paralelo (`BackgroundTasks`): publica evento de clique no Redis Stream
5. Worker (processo separado) consome stream, faz lookup geo via MaxMind, persiste em `click_events`
6. Job diario agrega `click_events` em `url_stats_daily`

Esse desenho mantem o redirect rapido e desacopla o registro de analytics, sem perder granularidade.

## Camadas

### Domain
- Entidades: `User`, `ShortUrl`, `ClickEvent`, `UrlStatsDaily`
- Value objects: `Slug`, `Url`, `GeoLocation`, `UserAgentInfo`
- Servicos puros: `SlugGenerator` (Strategy), `UrlValidator`, `ClickAnalyzer`
- Ports: `ShortUrlRepository`, `ClickEventRepository`, `CachePort`, `EventPublisherPort`, `GeoLookupPort`, `RateLimiterPort`

### Application
Use cases finos que orquestram o domínio:
- `CreateShortUrl`, `ListShortUrls`, `DeleteShortUrl`
- `ResolveSlug` (consulta cache, fallback no DB, dispara evento)
- `GetUrlStats`, `GetTimeline`, `GetGeoBreakdown`

### Infrastructure
- SQLAlchemy 2.0 async + asyncpg
- `redis-py` async para cache/streams
- `maxminddb` para lookup geo offline
- `user-agents` para parse de UA

### Presentation
- FastAPI + Pydantic v2
- Middleware de rate limiting (token bucket no Redis)
- Middleware de request_id

## Tradeoffs registrados nos ADRs

- 0001 — Clean Architecture
- 0002 — JWT manual
- 0003 — SQLAlchemy 2.0 async
- 0004 — Redis Streams + worker em vez de Celery
- 0005 — MaxMind local em vez de API externa
- 0006 — Analytics hibrido (eventos + agregacao diaria)
