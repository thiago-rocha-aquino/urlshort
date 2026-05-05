from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from urlshort.domain.entities.short_url import ShortUrl
from urlshort.domain.value_objects.slug import Slug
from urlshort.infrastructure.database.mappers import short_url_mapper
from urlshort.infrastructure.database.models.short_url_model import ShortUrlModel


class SqlShortUrlRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, short_url: ShortUrl) -> ShortUrl:
        model = short_url_mapper.to_model(short_url)
        self._session.add(model)
        await self._session.flush()
        return short_url_mapper.to_entity(model)

    async def get_by_slug(self, slug: Slug) -> ShortUrl | None:
        stmt = select(ShortUrlModel).where(ShortUrlModel.slug == slug.value)
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        return short_url_mapper.to_entity(model) if model else None

    async def get_by_id(self, url_id: int) -> ShortUrl | None:
        model = await self._session.get(ShortUrlModel, url_id)
        return short_url_mapper.to_entity(model) if model else None

    async def list_by_user(
        self, user_id: int, *, limit: int = 100, offset: int = 0
    ) -> Sequence[ShortUrl]:
        stmt = (
            select(ShortUrlModel)
            .where(ShortUrlModel.user_id == user_id)
            .order_by(ShortUrlModel.id.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [short_url_mapper.to_entity(m) for m in rows]

    async def delete(self, url_id: int) -> None:
        await self._session.execute(delete(ShortUrlModel).where(ShortUrlModel.id == url_id))
        await self._session.flush()

    async def increment_click_count(self, url_id: int) -> None:
        await self._session.execute(
            update(ShortUrlModel)
            .where(ShortUrlModel.id == url_id)
            .values(click_count=ShortUrlModel.click_count + 1)
        )
        await self._session.flush()
