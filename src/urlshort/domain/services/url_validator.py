from __future__ import annotations

from urllib.parse import urlparse

from urlshort.domain.exceptions import DomainError
from urlshort.domain.value_objects.url import Url

# evita auto-loop e abuso obvio. Nao eh uma blacklist completa.
_BLOCKED_HOST_FRAGMENTS = frozenset({"localhost", "127.0.0.1", "0.0.0.0", "::1", "169.254.169.254"})


class InvalidTargetUrlError(DomainError):
    pass


class UrlValidator:
    def __init__(self, *, base_url_host: str | None = None) -> None:
        # se setado, impede encurtar URLs apontando para o proprio servico
        self._self_host = base_url_host.lower() if base_url_host else None

    def validate(self, url: Url) -> None:
        host = urlparse(url.value).hostname or ""
        host = host.lower()
        if host in _BLOCKED_HOST_FRAGMENTS:
            raise InvalidTargetUrlError(f"host nao permitido: {host}")
        if self._self_host and host == self._self_host:
            raise InvalidTargetUrlError("URL nao pode apontar para o proprio servico")
