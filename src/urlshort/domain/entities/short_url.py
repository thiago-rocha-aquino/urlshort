from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from urlshort.domain.exceptions import UrlExpiredError, UrlMaxClicksReachedError
from urlshort.domain.value_objects.slug import Slug
from urlshort.domain.value_objects.url import Url


@dataclass(slots=True)
class ShortUrl:
    user_id: int
    slug: Slug
    target: Url
    id: int | None = None
    expires_at: datetime | None = None
    max_clicks: int | None = None
    click_count: int = 0
    password_hash: str | None = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def is_password_protected(self) -> bool:
        return self.password_hash is not None

    def is_expired(self, *, now: datetime | None = None) -> bool:
        if self.expires_at is None:
            return False
        return (now or datetime.now(UTC)) >= self.expires_at

    def has_reached_max_clicks(self) -> bool:
        if self.max_clicks is None:
            return False
        return self.click_count >= self.max_clicks

    def ensure_resolvable(self, *, now: datetime | None = None) -> None:
        """Levanta excecao de dominio se a URL nao pode ser resolvida agora."""
        if not self.is_active:
            raise UrlExpiredError()
        if self.is_expired(now=now):
            raise UrlExpiredError()
        if self.has_reached_max_clicks():
            raise UrlMaxClicksReachedError()
