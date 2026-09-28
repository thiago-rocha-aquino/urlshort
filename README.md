# api_url_shortener

Encurtador de URLs com **analytics granulares**, **cache Redis**, **fila assincrona via Redis Streams** e **detecao de geolocalizacao via MaxMind**. Projeto de portfolio para demonstrar Clean Architecture com foco em **performance** e **escala**.

Sister project: [api_financa](../) — mesma stack base, mas focado em modelagem de dominio rica.

## Stack

- **Python 3.12+** com **FastAPI** + **Pydantic v2**
- **PostgreSQL** (5433 em dev) + **SQLAlchemy 2.0 async** + **Alembic**
- **Redis 7** para cache de slug, rate limit e fila de eventos (Streams)
- **JWT manual** (access + refresh com rotacao) + bcrypt
- **MaxMind GeoLite2** para geolocalizacao offline
- **uv** para gestao de dependencias
- **structlog** com logging estruturado JSON
- **Pytest** + **httpx** + **Ruff** + **mypy strict**
- Arquitetura **Clean / Hexagonal** com dominio puro no centro

## Arquitetura

```mermaid
flowchart TB
    cli([Cliente HTTP]) --> api

    subgraph presentation [Presentation - FastAPI]
        api[Rotas]
        rl[Rate limit]
    end

    subgraph application [Application]
        uc[create / list / redirect / analytics / auth]
    end

    subgraph domain [Domain puro]
        ent[ShortUrl, ClickEvent, UrlStatsDaily]
        vo[Slug, Url, GeoLocation]
        svc[SlugGenerator, UrlValidator, ClickAnalyzer]
        ports[Ports]
    end

    subgraph infrastructure [Infrastructure]
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

### Fluxo de redirect (caminho quente)

1. `GET /{slug}` — consulta cache Redis (`slug -> URL`)
2. Se cache hit, retorna 302 imediato; senao, busca no DB e popula cache
3. Em paralelo, publica evento de clique no Redis Stream
4. **Worker** (processo separado) consome a stream, faz lookup geo via MaxMind, parseia user-agent e persiste em `click_events`
5. **Job diario** agrega `click_events` em `url_stats_daily` (idempotente)

Endpoints de analytics consultam `url_stats_daily` para series longas e `click_events` para drill-down recente.

## Estrutura

```
src/urlshort/
├── domain/          # entidades, VOs, services, ports (zero deps externas)
├── application/     # use cases (orquestracao)
├── infrastructure/  # SQLAlchemy, Redis, MaxMind, JWT, bcrypt, logging
├── presentation/    # FastAPI: rotas, schemas, middleware
└── jobs/            # worker e agregacao diaria (entrypoints CLI)
```

## Endpoints

| Recurso | Metodos |
|---|---|
| `/health`, `/health/db`, `/health/redis` | GET |
| `/api/auth/*` | register, login, refresh, logout, me |
| `/api/urls` | criar (com rate limit), listar |
| `/api/urls/{id}` | DELETE |
| `/api/urls/{id}/analytics` | timeline + breakdowns por pais/device/referrer |
| `/api/urls/{id}/analytics/recent` | eventos granulares recentes |
| `/{slug}` | redirect 302 (caminho quente) |

OpenAPI completo em http://localhost:8001/docs.

## Setup local

```bash
# 1. Instalar deps
uv sync

# 2. Subir Postgres + Redis
docker compose up -d

# 3. Configurar ambiente
cp .env.example .env
# edite JWT_SECRET_KEY (openssl rand -hex 32)

# 4. Migrations
uv run alembic upgrade head

# 5. API
uv run uvicorn urlshort.main:app --reload --port 8001

# 6. Worker (em outro terminal)
uv run python -m urlshort.jobs.click_event_worker

# 7. Job de agregacao (manual ou via cron)
uv run python -m urlshort.jobs.aggregate_daily_stats         # ontem
uv run python -m urlshort.jobs.aggregate_daily_stats 2026-04-27
```

API em http://localhost:8001 — docs em http://localhost:8001/docs.

## GeoIP (opcional)

Baixe a base **GeoLite2 City** gratuita do MaxMind (precisa de conta) e aponte `GEOIP_DATABASE_PATH` no `.env`. Sem essa configuracao, geo eh apenas omitida — o resto continua funcionando.

## Comandos uteis

```bash
uv run pytest                              # toda a suite (precisa Postgres + Redis)
uv run pytest tests/unit                   # so unit
uv run ruff check .                        # lint
uv run ruff format .                       # auto-format
uv run mypy src tests                      # type-check strict
uv run alembic revision --autogenerate -m "msg"
uv run alembic upgrade head
```

## Deploy

### API
```bash
docker build -t urlshort .
docker run -p 8001:8001 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host/db \
  -e REDIS_URL=redis://host:6379/0 \
  -e JWT_SECRET_KEY=$(openssl rand -hex 32) \
  urlshort
```

### Worker (mesma imagem, entrypoint diferente)
```bash
docker run --entrypoint python urlshort -m urlshort.jobs.click_event_worker
```

## CI

GitHub Actions roda em todo push/PR:
- Ruff lint + format check
- mypy strict
- Pytest contra Postgres 16 e Redis 7 (services do GHA), com migrations aplicadas

Ver [.github/workflows/ci.yml](.github/workflows/ci.yml).

## Decisoes arquiteturais

ADRs em [docs/adr/](docs/adr/):
- 0001 — Clean Architecture
- 0002 — JWT manual
- 0003 — SQLAlchemy 2.0 async
- 0004 — Redis Streams + worker em vez de Celery
- 0005 — MaxMind local em vez de API externa
- 0006 — Analytics hibrido (granular + agregacao diaria)
