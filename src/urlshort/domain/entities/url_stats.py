from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class UrlStatsDaily:
    """Agregacao diaria de cliques por url x dia x dimensao opcional.

    A combinacao (short_url_id, day, country_code, device_type, referrer_host)
    eh unica — null nas dimensoes ate decidir granularidade no insert.
    """

    short_url_id: int
    day: date
    clicks: int
    country_code: str | None = None
    device_type: str | None = None
    referrer_host: str | None = None
    id: int | None = None
