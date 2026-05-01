from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

from urlshort.domain.entities.url_stats import UrlStatsDaily
from urlshort.domain.exceptions import EntityNotFoundError, ForbiddenError
from urlshort.domain.ports.repositories import (
    ClickEventRepository,
    ShortUrlRepository,
    UrlStatsRepository,
)


@dataclass(frozen=True, slots=True)
class UrlStatsSummary:
    total_clicks: int
    timeline: Sequence[UrlStatsDaily]
    countries: Sequence[tuple[str, int]]
    devices: Sequence[tuple[str, int]]
    referrers: Sequence[tuple[str, int]]


class GetUrlStats:
    def __init__(
        self,
        urls: ShortUrlRepository,
        clicks: ClickEventRepository,
        stats: UrlStatsRepository,
    ) -> None:
        self._urls = urls
        self._clicks = clicks
        self._stats = stats

    async def execute(
        self, *, user_id: int, url_id: int, start: date, end: date
    ) -> UrlStatsSummary:
        url = await self._urls.get_by_id(url_id)
        if url is None:
            raise EntityNotFoundError("ShortUrl", url_id)
        if url.user_id != user_id:
            raise ForbiddenError()

        timeline = await self._stats.get_timeline(url_id, start=start, end=end)
        countries = await self._stats.get_breakdown(
            url_id, dimension="country_code", start=start, end=end
        )
        devices = await self._stats.get_breakdown(
            url_id, dimension="device_type", start=start, end=end
        )
        referrers = await self._stats.get_breakdown(
            url_id, dimension="referrer_host", start=start, end=end
        )
        # somatorio do timeline (cobertura agregada). Para "tempo real",
        # podemos somar com clicks que ainda nao foram agregados.
        total = sum(point.clicks for point in timeline)
        return UrlStatsSummary(
            total_clicks=total,
            timeline=timeline,
            countries=countries,
            devices=devices,
            referrers=referrers,
        )
