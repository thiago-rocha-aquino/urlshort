from __future__ import annotations

from collections.abc import Sequence

from urlshort.domain.entities.short_url import ShortUrl
from urlshort.domain.ports.repositories import ShortUrlRepository


class ListShortUrls:
    def __init__(self, urls: ShortUrlRepository) -> None:
        self._urls = urls

    async def execute(
        self, user_id: int, *, limit: int = 100, offset: int = 0
    ) -> Sequence[ShortUrl]:
        return await self._urls.list_by_user(user_id, limit=limit, offset=offset)
