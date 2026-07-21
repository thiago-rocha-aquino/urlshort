from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class TimelinePoint(BaseModel):
    day: date
    clicks: int


class BreakdownItem(BaseModel):
    label: str
    clicks: int


class StatsResponse(BaseModel):
    url_id: int
    period_start: date
    period_end: date
    total_clicks: int
    timeline: list[TimelinePoint]
    countries: list[BreakdownItem]
    devices: list[BreakdownItem]
    referrers: list[BreakdownItem]


class ClickEventResponse(BaseModel):
    id: int
    occurred_at: datetime
    ip: str
    country_code: str | None
    city: str | None
    device_type: str
    browser: str | None
    os: str | None
    is_bot: bool
    referrer: str | None
