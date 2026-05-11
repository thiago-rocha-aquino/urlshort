"""Agrega click_events do dia (ou periodo informado) em url_stats_daily.

Uso:

    uv run python -m urlshort.jobs.aggregate_daily_stats               # ontem
    uv run python -m urlshort.jobs.aggregate_daily_stats 2026-04-27    # data especifica

Idempotente: re-rodar regrava as mesmas linhas (UPSERT por chave unica).
"""

from __future__ import annotations

import asyncio
import sys
from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy import func, select

from urlshort.domain.entities.url_stats import UrlStatsDaily
from urlshort.infrastructure.database.models.click_event_model import ClickEventModel
from urlshort.infrastructure.database.repositories.sql_url_stats_repository import (
    SqlUrlStatsRepository,
)
from urlshort.infrastructure.database.session import session_scope


async def aggregate_day(target_day: date) -> int:
    """Agrega o dia informado, retorna numero de linhas upsertadas."""
    start = datetime.combine(target_day, time.min, tzinfo=UTC)
    end = start + timedelta(days=1)

    async with session_scope() as session:
        stmt = (
            select(
                ClickEventModel.short_url_id,
                ClickEventModel.country_code,
                ClickEventModel.device_type,
                ClickEventModel.referrer_host,
                func.count(ClickEventModel.id).label("clicks"),
            )
            .where(ClickEventModel.occurred_at >= start)
            .where(ClickEventModel.occurred_at < end)
            .group_by(
                ClickEventModel.short_url_id,
                ClickEventModel.country_code,
                ClickEventModel.device_type,
                ClickEventModel.referrer_host,
            )
        )
        rows = (await session.execute(stmt)).all()
        stats = [
            UrlStatsDaily(
                short_url_id=row.short_url_id,
                day=target_day,
                country_code=row.country_code,
                device_type=row.device_type,
                referrer_host=row.referrer_host,
                clicks=int(row.clicks),
            )
            for row in rows
        ]
        await SqlUrlStatsRepository(session).upsert_many(stats)
        return len(stats)


def _parse_arg(arg: str | None) -> date:
    if arg is None:
        return (datetime.now(UTC) - timedelta(days=1)).date()
    return date.fromisoformat(arg)


def main() -> None:  # pragma: no cover
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    day = _parse_arg(arg)
    n = asyncio.run(aggregate_day(day))
    print(f"agregadas {n} linhas para {day.isoformat()}")


if __name__ == "__main__":  # pragma: no cover
    main()
