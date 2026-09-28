# ADR 0003 — SQLAlchemy 2.0 async + asyncpg

**Status:** Aceito
**Data:** 2026-04-28

## Contexto

FastAPI eh nativamente async. O caminho quente desse servico (redirect de slug) precisa ser rapido — qualquer I/O bloqueante no event loop arruina throughput.

## Decisao

- SQLAlchemy 2.0 async com `Mapped[...]`, `mapped_column`, `DeclarativeBase`.
- `asyncpg` como driver Postgres.
- Alembic para migrations (CLI sincrono, mas le os models async sem problema).
- Repositorios recebem `AsyncSession` injetada.

## Consequencias

- Endpoints I/O-bound escalam bem.
- Tipagem moderna ajuda mypy a pegar erros.
- Curva de aprendizado: lazy loading nao funciona em async — `selectinload`/`joinedload` explicitos.
