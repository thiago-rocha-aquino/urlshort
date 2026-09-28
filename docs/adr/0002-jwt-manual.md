# ADR 0002 — JWT manual

**Status:** Aceito
**Data:** 2026-04-28

## Contexto

API multi-usuario: cada usuario gerencia suas URLs e ve seus analytics. Preciso de auth.

## Decisao

JWT manual com `python-jose` + `bcrypt`. Mesma estrategia do projeto irmao (api_financa): access (15min) + refresh (7 dias com rotacao). Refresh tokens armazenados no banco para permitir revogacao.

## Consequencias

- Demonstra dominio do protocolo OAuth2/JWT, sem caixa-preta.
- Codigo extra para manter, mas com testes solidos os bugs ficam contidos.
- Vantagem em portfolio: mostra que sei o que rolando por baixo das libs prontas.
