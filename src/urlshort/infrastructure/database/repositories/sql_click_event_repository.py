from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from urlshort.domain.entities.click_event import ClickEvent
from urlshort.infrastructure.database.mappers import click_event_mapper
from urlshort.infrastructure.database.models.click_event_model import ClickEventModel


class SqlClickEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, event: ClickEvent) -> ClickEvent:
        model = click_event_mapper.to_model(event)
        self._session.add(model)
        await self._session.flush()
        return click_event_mapper.to_entity(model)

    async def count_by_url(self, short_url_id: int) -> int:
        stmt = select(func.count(ClickEventModel.id)).where(
            ClickEventModel.short_url_id == short_url_id
        )
        return int((await self._session.execute(stmt)).scalar() or 0)

    async def list_by_url(
        self, short_url_id: int, *, limit: int = 100, offset: int = 0
    ) -> Sequence[ClickEvent]:
        stmt = (
            select(ClickEventModel)
            .where(ClickEventModel.short_url_id == short_url_id)
            .order_by(ClickEventModel.occurred_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [click_event_mapper.to_entity(m) for m in rows]
