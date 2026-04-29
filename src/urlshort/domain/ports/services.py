from __future__ import annotations

from typing import Protocol

from urlshort.domain.entities.click_event import ClickEvent
from urlshort.domain.value_objects.geo_location import GeoLocation
from urlshort.domain.value_objects.slug import Slug
from urlshort.domain.value_objects.url import Url


class PasswordHasher(Protocol):
    def hash(self, plain: str) -> str: ...
    def verify(self, plain: str, hashed: str) -> bool: ...


class TokenService(Protocol):
    def create_access_token(self, subject: str) -> str: ...
    def decode_access_token(self, token: str) -> str: ...
    def create_refresh_token(self) -> str: ...


class UrlCachePort(Protocol):
    async def get(self, slug: Slug) -> Url | None: ...
    async def set(self, slug: Slug, url: Url, *, ttl_seconds: int = 3600) -> None: ...
    async def invalidate(self, slug: Slug) -> None: ...


class EventPublisherPort(Protocol):
    async def publish_click(self, event: ClickEvent) -> None: ...


class GeoLookupPort(Protocol):
    def lookup(self, ip: str) -> GeoLocation: ...


class RateLimiterPort(Protocol):
    async def hit(self, key: str, *, limit: int, window_seconds: int) -> bool:
        """Retorna True se a chave esta dentro do limite (ainda pode prosseguir)."""
        ...
