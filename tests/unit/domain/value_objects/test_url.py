from __future__ import annotations

import pytest

from urlshort.domain.value_objects.url import Url


def test_url_valida() -> None:
    u = Url("https://example.com/path?q=1")
    assert u.host == "example.com"


@pytest.mark.parametrize(
    "bad",
    ["", "ftp://ex.com", "javascript:alert(1)", "/sem-scheme", "https://"],
)
def test_url_invalida(bad: str) -> None:
    with pytest.raises(ValueError):
        Url(bad)


def test_url_strip() -> None:
    assert Url("  https://x.com  ").value == "https://x.com"


def test_url_muito_longa() -> None:
    with pytest.raises(ValueError, match="excede"):
        Url("https://x.com/" + ("a" * 3000))
