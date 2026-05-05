from __future__ import annotations

from urlshort.domain.exceptions import EntityNotFoundError, ForbiddenError
from urlshort.domain.ports.repositories import ShortUrlRepository
from urlshort.domain.ports.services import UrlCachePort


class DeleteShortUrl:
    def __init__(self, urls: ShortUrlRepository, cache: UrlCachePort) -> None:
        self._urls = urls
        self._cache = cache

    async def execute(self, *, user_id: int, url_id: int) -> None:
        url = await self._urls.get_by_id(url_id)
        if url is None:
            raise EntityNotFoundError("ShortUrl", url_id)
        if url.user_id != user_id:
            raise ForbiddenError()
        await self._cache.invalidate(url.slug)
        await self._urls.delete(url_id)
