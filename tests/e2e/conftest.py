from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from urlshort.infrastructure.config import get_settings


def _database_url() -> str:
    return os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://urlshort:urlshort@localhost:5433/urlshort",
    )


def _redis_url() -> str:
    return os.environ.get("TEST_REDIS_URL", "redis://localhost:6379/0")


@pytest.fixture(autouse=True)
def _override_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _database_url())
    monkeypatch.setenv("REDIS_URL", _redis_url())
    monkeypatch.setenv("APP_BASE_URL", "http://test")
    monkeypatch.setenv("RATE_LIMIT_CREATE_PER_MINUTE", "1000")
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
async def _truncate_tables() -> AsyncIterator[None]:
    engine = create_async_engine(_database_url())
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "TRUNCATE TABLE refresh_tokens, click_events, url_stats_daily, "
                "short_urls, users RESTART IDENTITY CASCADE"
            )
        )
    await engine.dispose()

    # limpa redis (cache + streams + rate limiters)
    from redis.asyncio import from_url

    redis = from_url(_redis_url(), decode_responses=False)
    await redis.flushdb()
    await redis.aclose()

    yield


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    import urlshort.infrastructure.cache.redis_client as rc
    import urlshort.infrastructure.database.session as sess

    sess._engine = None
    sess._sessionmaker = None
    rc._redis = None

    from urlshort.main import create_app

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
