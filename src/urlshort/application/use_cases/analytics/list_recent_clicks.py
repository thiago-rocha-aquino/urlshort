from __future__ import annotations

from collections.abc import Sequence

from urlshort.domain.entities.click_event import ClickEvent
from urlshort.domain.exceptions import EntityNotFoundError, ForbiddenError
from urlshort.domain.ports.repositories import ClickEventRepository, ShortUrlRepository


class ListRecentClicks:
    def __init__(self, urls: ShortUrlRepository, clicks: ClickEventRepository) -> None:
        self._urls = urls
        self._clicks = clicks

    async def execute(
        self, *, user_id: int, url_id: int, limit: int = 50, offset: int = 0
    ) -> Sequence[ClickEvent]:
        url = await self._urls.get_by_id(url_id)
        if url is None:
            raise EntityNotFoundError("ShortUrl", url_id)
        if url.user_id != user_id:
            raise ForbiddenError()
        return await self._clicks.list_by_url(url_id, limit=limit, offset=offset)
