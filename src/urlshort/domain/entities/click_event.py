from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from urlshort.domain.value_objects.geo_location import GeoLocation
from urlshort.domain.value_objects.user_agent_info import DeviceType, UserAgentInfo


@dataclass(slots=True)
class ClickEvent:
    short_url_id: int
    slug: str
    ip: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    referrer: str | None = None
    user_agent: UserAgentInfo | None = None
    geo: GeoLocation = field(default_factory=GeoLocation)
    id: int | None = None

    @property
    def country_code(self) -> str | None:
        return self.geo.country_code

    @property
    def device_type(self) -> DeviceType:
        return self.user_agent.device_type if self.user_agent else DeviceType.UNKNOWN

    @property
    def is_bot(self) -> bool:
        return bool(self.user_agent and self.user_agent.is_bot)
