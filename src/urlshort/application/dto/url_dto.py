from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class CreateShortUrlInput:
    user_id: int
    target: str
    custom_slug: str | None = None
    expires_at: datetime | None = None
    max_clicks: int | None = None
    password: str | None = None


@dataclass(frozen=True, slots=True)
class ResolveSlugInput:
    slug: str
    ip: str
    user_agent: str | None
    referrer: str | None
    password: str | None = None
