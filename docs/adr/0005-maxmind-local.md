# ADR 0005 — MaxMind GeoLite2 local em vez de API externa

**Status:** Aceito
**Data:** 2026-04-28

## Contexto

Para compor analytics geograficos (cliques por pais/cidade), precisamos converter IP em localizacao. Opcoes:

1. API externa (ipapi.co, ipinfo.io). Simples mas adiciona ~150ms de latencia e ponto de falha.
2. Base MaxMind GeoLite2 baixada localmente (~70MB, gratuita).

## Decisao

MaxMind GeoLite2 City lido com `maxminddb`. Lookup em memoria, ~microssegundos. A geolocalizacao acontece no **worker**, nao no caminho do redirect — entao mesmo a hipotetica latencia de uma API externa nao seria fatal, mas a base local elimina dependencia externa e simplifica testes.

Configuravel por env (`GEOIP_DATABASE_PATH`); se vazio, geo fica desabilitada (degrada gracefully).

## Consequencias

- Analytics geo funciona offline e em CI.
- Atualizacao da base eh manual (job mensal seria o ideal).
- Em testes, basta nao setar o path — geo eh ignorada.
