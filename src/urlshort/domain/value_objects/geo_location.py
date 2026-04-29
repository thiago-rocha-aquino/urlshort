from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GeoLocation:
    country_code: str | None = None
    country_name: str | None = None
    city: str | None = None

    @property
    def is_known(self) -> bool:
        return self.country_code is not None
