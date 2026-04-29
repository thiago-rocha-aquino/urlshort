from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DeviceType(StrEnum):
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"
    BOT = "bot"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class UserAgentInfo:
    raw: str
    device_type: DeviceType
    browser: str | None = None
    os: str | None = None
    is_bot: bool = False
