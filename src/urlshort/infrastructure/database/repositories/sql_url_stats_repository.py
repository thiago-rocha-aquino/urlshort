from __future__ import annotations

from collections.abc import Sequence
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from urlshort.domain.entities.url_stats import UrlStatsDaily
from urlshort.infrastructure.database.models.url_stats_model import UrlStatsDailyModel

_VALID_DIMENSIONS: dict[str, InstrumentedAttribute[str | None]] = {
    "country_code": UrlStatsDailyModel.country_code,
    "device_type": UrlStatsDailyModel.device_type,
    "referrer_host": UrlStatsDailyModel.referrer_host,
}


class SqlUrlStatsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_many(self, stats: Sequence[UrlStatsDaily]) -> None:
        if not stats:
            return
        rows = [
            {
                "short_url_id": s.short_url_id,
                "day": s.day,
                "country_code": s.country_code,
                "device_type": s.device_type,
                "referrer_host": s.referrer_host,
                "clicks": s.clicks,
            }
            for s in stats
        ]
        stmt = insert(UrlStatsDailyModel).values(rows)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_stats_url_day_dim",
            set_={"clicks": stmt.excluded.clicks},
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def get_timeline(
        self, short_url_id: int, *, start: date, end: date
    ) -> Sequence[UrlStatsDaily]:
        stmt = (
            select(
                UrlStatsDailyModel.day,
                func.sum(UrlStatsDailyModel.clicks).label("total"),
            )
            .where(UrlStatsDailyModel.short_url_id == short_url_id)
            .where(UrlStatsDailyModel.day >= start)
            .where(UrlStatsDailyModel.day <= end)
            .group_by(UrlStatsDailyModel.day)
            .order_by(UrlStatsDailyModel.day)
        )
        rows = (await self._session.execute(stmt)).all()
        return [
            UrlStatsDaily(short_url_id=short_url_id, day=row.day, clicks=int(row.total))
            for row in rows
        ]

    async def get_breakdown(
        self, short_url_id: int, *, dimension: str, start: date, end: date
    ) -> Sequence[tuple[str, int]]:
        column = _VALID_DIMENSIONS.get(dimension)
        if column is None:
            raise ValueError(f"dimensao invalida: {dimension}")
        stmt = (
            select(column, func.sum(UrlStatsDailyModel.clicks).label("total"))
            .where(UrlStatsDailyModel.short_url_id == short_url_id)
            .where(UrlStatsDailyModel.day >= start)
            .where(UrlStatsDailyModel.day <= end)
            .group_by(column)
            .order_by(func.sum(UrlStatsDailyModel.clicks).desc())
        )
        rows = (await self._session.execute(stmt)).all()
        return [(str(row[0] or "unknown"), int(row[1])) for row in rows]
