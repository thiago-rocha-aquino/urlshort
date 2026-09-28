from __future__ import annotations

import pytest

from urlshort.domain.services.url_validator import InvalidTargetUrlError, UrlValidator
from urlshort.domain.value_objects.url import Url


def test_aceita_url_valida() -> None:
    UrlValidator().validate(Url("https://example.com"))


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost/x",
        "http://127.0.0.1",
        "http://0.0.0.0/x",
        "http://169.254.169.254/meta",  # AWS metadata
    ],
)
def test_bloqueia_hosts_internos(url: str) -> None:
    with pytest.raises(InvalidTargetUrlError):
        UrlValidator().validate(Url(url))


def test_bloqueia_self_host() -> None:
    v = UrlValidator(base_url_host="urlshort.app")
    with pytest.raises(InvalidTargetUrlError):
        v.validate(Url("https://urlshort.app/abc"))
