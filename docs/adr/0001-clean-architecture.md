# ADR 0001 — Clean Architecture / Hexagonal

**Status:** Aceito
**Data:** 2026-04-28

## Contexto

Mesmo um sistema "simples" como encurtador de URL tem complexidade real escondida: cache, fila de eventos, geolocalizacao, rate limit, analytics. Misturar tudo isso em controllers FastAPI vira bola de neve em pouco tempo.

## Decisao

Adotar Clean Architecture com quatro camadas (`domain`, `application`, `infrastructure`, `presentation`). Dependencias apontam pra dentro. Ports (Protocols) no dominio, adapters na infra.

## Consequencias

**Positivas**
- Trocar Redis por Memcached, ou MaxMind por API externa, mexe so na infra.
- Use cases sao testaveis sem subir nada — o `ResolveSlug` pode ser exercitado com `FakeCache` e `FakeRepository`.
- O dominio fica como documentacao viva das regras (slug eh ASCII, URL precisa ter scheme, etc).

**Negativas**
- Mais arquivos pra um CRUD simples — overhead aceitavel dado os pontos de complexidade ja listados.
