# ADR 0006 — Analytics hibrido: eventos + agregacao diaria

**Status:** Aceito
**Data:** 2026-04-28

## Contexto

Endpoints de analytics precisam responder rapido ("cliques nos ultimos 30 dias por pais") mesmo com URLs de alto trafego. Duas abordagens:

1. **Tabela de eventos pura**: 1 linha por clique. Flexivel pra qualquer query nova, mas escaneia tudo.
2. **Contadores agregados**: 1 linha por dia/dimensao. Rapido, mas perde granularidade.

## Decisao

Hibrido:
- `click_events` granular (1 linha por clique) — suporta drill-down e queries ad-hoc.
- `url_stats_daily` agregado por dia/pais/referrer — alimenta dashboards.
- Job noturno agrega o dia anterior, idempotente (re-rodar nao duplica).

## Consequencias

- Dashboards de longo prazo nao escaneiam milhoes de eventos.
- Drill-down em um pico de trafego ainda funciona (vai na tabela granular).
- Mostra que penso em escala mesmo num projeto pequeno.
- Custo: precisa manter o job de agregacao + uma tabela a mais.
