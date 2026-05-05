from __future__ import annotations

from pathlib import Path
from typing import Any

import maxminddb

from urlshort.domain.value_objects.geo_location import GeoLocation


class MaxMindGeoLookup:
    """Lookup de IP usando base GeoLite2 local.

    Se o path nao existir, opera no modo no-op (retorna GeoLocation vazio).
    """

    def __init__(self, database_path: str | None) -> None:
        self._reader: Any = None
        if database_path and Path(database_path).is_file():
            self._reader = maxminddb.open_database(database_path)

    def lookup(self, ip: str) -> GeoLocation:
        if self._reader is None or not ip:
            return GeoLocation()
        try:
            data = self._reader.get(ip)
        except (ValueError, OSError):
            return GeoLocation()
        if not isinstance(data, dict):
            return GeoLocation()
        country = data.get("country", {}) or {}
        city = data.get("city", {}) or {}
        return GeoLocation(
            country_code=country.get("iso_code"),
            country_name=(country.get("names") or {}).get("en"),
            city=(city.get("names") or {}).get("en"),
        )

    def close(self) -> None:
        if self._reader is not None:
            self._reader.close()


class NullGeoLookup:
    def lookup(self, ip: str) -> GeoLocation:
        return GeoLocation()
