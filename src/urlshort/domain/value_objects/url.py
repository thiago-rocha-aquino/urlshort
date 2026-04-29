from __future__ import annotations

from dataclasses import dataclass
from typing import Self
from urllib.parse import urlparse

_ALLOWED_SCHEMES = frozenset({"http", "https"})
_MAX_URL_LENGTH = 2048


@dataclass(frozen=True, slots=True)
class Url:
    value: str

    def __post_init__(self) -> None:
        v = self.value.strip()
        if not v:
            raise ValueError("URL vazia")
        if len(v) > _MAX_URL_LENGTH:
            raise ValueError(f"URL excede {_MAX_URL_LENGTH} caracteres")
        parsed = urlparse(v)
        if parsed.scheme.lower() not in _ALLOWED_SCHEMES:
            raise ValueError(f"scheme nao permitido: {parsed.scheme!r}")
        if not parsed.netloc:
            raise ValueError("URL sem host")
        object.__setattr__(self, "value", v)

    @classmethod
    def of(cls, value: str) -> Self:
        return cls(value)

    @property
    def host(self) -> str:
        return urlparse(self.value).netloc.lower()

    def __str__(self) -> str:
        return self.value
