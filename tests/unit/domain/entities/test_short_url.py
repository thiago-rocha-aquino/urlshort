from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from urlshort.domain.entities.short_url import ShortUrl
from urlshort.domain.exceptions import UrlExpiredError, UrlMaxClicksReachedError
from urlshort.domain.value_objects.slug import Slug
from urlshort.domain.value_objects.url import Url


def _url(**kw: object) -> ShortUrl:
    base: dict[str, object] = {
        "user_id": 1,
        "slug": Slug("abc123"),
        "target": Url("https://example.com"),
    }
    base.update(kw)
    return ShortUrl(**base)  # type: ignore[arg-type]


def test_password_protection() -> None:
    assert not _url().is_password_protected()
    assert _url(password_hash="bcrypt-x").is_password_protected()


def test_expirada() -> None:
    past = datetime.now(UTC) - timedelta(days=1)
    assert _url(expires_at=past).is_expired()
    future = datetime.now(UTC) + timedelta(days=1)
    assert not _url(expires_at=future).is_expired()


def test_max_clicks() -> None:
    assert not _url(max_clicks=10, click_count=5).has_reached_max_clicks()
    assert _url(max_clicks=10, click_count=10).has_reached_max_clicks()
    assert not _url(max_clicks=None, click_count=999).has_reached_max_clicks()


def test_ensure_resolvable_ok() -> None:
    _url().ensure_resolvable()


def test_ensure_resolvable_inativa() -> None:
    with pytest.raises(UrlExpiredError):
        _url(is_active=False).ensure_resolvable()


def test_ensure_resolvable_expirada() -> None:
    with pytest.raises(UrlExpiredError):
        _url(expires_at=datetime.now(UTC) - timedelta(seconds=1)).ensure_resolvable()


def test_ensure_resolvable_max_clicks() -> None:
    with pytest.raises(UrlMaxClicksReachedError):
        _url(max_clicks=1, click_count=1).ensure_resolvable()
