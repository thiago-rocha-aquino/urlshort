"""Worker que consome eventos de clique do Redis Stream e persiste em click_events.

Roda como processo separado:

    uv run python -m urlshort.jobs.click_event_worker

Cada mensagem tem campos: short_url_id, slug, ip, occurred_at, referrer, user_agent.
O worker enriquece com geo + UA parsing e grava no banco.
"""

from __future__ import annotations

import asyncio
import contextlib
import signal
from datetime import datetime
from typing import Any

import structlog
from redis.asyncio import Redis
from redis.exceptions import ResponseError

from urlshort.domain.entities.click_event import ClickEvent
from urlshort.domain.services.click_analyzer import ClickAnalyzer
from urlshort.infrastructure.cache.redis_client import close_redis, get_redis
from urlshort.infrastructure.config import get_settings
from urlshort.infrastructure.database.repositories.sql_click_event_repository import (
    SqlClickEventRepository,
)
from urlshort.infrastructure.database.session import session_scope
from urlshort.infrastructure.geo.maxmind_lookup import MaxMindGeoLookup
from urlshort.infrastructure.logging import configure_logging

_logger = structlog.get_logger("urlshort.worker")


async def _ensure_consumer_group(redis: Redis, stream: str, group: str) -> None:
    try:
        await redis.xgroup_create(stream, group, id="0", mkstream=True)
    except ResponseError as exc:
        if "BUSYGROUP" not in str(exc):
            raise


def _decode(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


async def _process_message(
    fields: dict[Any, Any],
    *,
    analyzer: ClickAnalyzer,
    geo: MaxMindGeoLookup,
) -> None:
    data = {_decode(k): _decode(v) for k, v in fields.items()}
    occurred_at = datetime.fromisoformat(data["occurred_at"])
    user_agent = analyzer.parse_user_agent(data.get("user_agent") or None)
    geo_loc = geo.lookup(data.get("ip", ""))

    event = ClickEvent(
        short_url_id=int(data["short_url_id"]),
        slug=data["slug"],
        ip=data.get("ip", ""),
        occurred_at=occurred_at,
        referrer=data.get("referrer") or None,
        user_agent=user_agent,
        geo=geo_loc,
    )
    async with session_scope() as session:
        await SqlClickEventRepository(session).add(event)


async def run(*, max_iterations: int | None = None, block_ms: int = 5000) -> None:
    """Loop principal. Se max_iterations setado, encerra apos N leituras (testes)."""
    configure_logging(debug=False)
    settings = get_settings()
    redis = get_redis()
    analyzer = ClickAnalyzer()
    geo = MaxMindGeoLookup(settings.geoip_database_path or None)

    consumer = "consumer-1"
    await _ensure_consumer_group(redis, settings.redis_stream_name, settings.redis_consumer_group)

    _logger.info("worker_started", stream=settings.redis_stream_name)

    iteration = 0
    stop = asyncio.Event()

    def _handle_signal(*_: Any) -> None:
        stop.set()

    with contextlib.suppress(NotImplementedError):
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, _handle_signal)

    while not stop.is_set():
        if max_iterations is not None and iteration >= max_iterations:
            break
        iteration += 1
        try:
            messages = await redis.xreadgroup(
                groupname=settings.redis_consumer_group,
                consumername=consumer,
                streams={settings.redis_stream_name: ">"},
                count=50,
                block=block_ms,
            )
        except Exception:
            _logger.exception("worker_read_failed")
            await asyncio.sleep(1)
            continue

        if not messages:
            continue

        for _stream_name, batch in messages:
            for msg_id, fields in batch:
                try:
                    await _process_message(fields, analyzer=analyzer, geo=geo)
                    await redis.xack(
                        settings.redis_stream_name,
                        settings.redis_consumer_group,
                        msg_id,
                    )
                except Exception:
                    _logger.exception("worker_process_failed", msg_id=msg_id)

    geo.close()
    await close_redis()
    _logger.info("worker_stopped")


def main() -> None:  # pragma: no cover
    asyncio.run(run())


if __name__ == "__main__":  # pragma: no cover
    main()
