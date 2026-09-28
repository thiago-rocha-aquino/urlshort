# ADR 0004 — Redis Streams + worker em vez de Celery

**Status:** Aceito
**Data:** 2026-04-28

## Contexto

Cada redirect gera um evento de clique que precisa ser registrado de forma assincrona (geo lookup, parse de UA, persistencia) sem bloquear o redirect. Opcoes:

1. `BackgroundTasks` do FastAPI — simples, mas in-process; perde eventos no restart.
2. Celery — robusto, mas traz broker, result backend, scheduler — overhead pesado pra um projeto que ja usa Redis.
3. Redis Streams + worker custom em Python.

## Decisao

Redis Streams com consumer group + worker async em script Python separado. Reusa o mesmo Redis ja usado para cache e rate limit — zero infra extra.

## Consequencias

**Positivas**
- Persistencia: eventos sobrevivem a restart do worker (consumer group + ACK).
- Throughput suficiente para o caso de uso (centenas a milhares de cliques/segundo).
- Codigo proprio do worker eh simples e didatico, mostra entendimento de fila.

**Negativas**
- Sem retry policy/backoff sofisticado — se quisermos algo industrial, eventualmente vale ir pro Celery/RQ.
