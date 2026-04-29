from __future__ import annotations

import secrets
import string
from typing import Protocol

from urlshort.domain.value_objects.slug import Slug

_ALPHABET = string.ascii_letters + string.digits  # base62


class SlugGenerator(Protocol):
    def generate(self) -> Slug: ...


class RandomBase62SlugGenerator:
    """Slug aleatorio base62 com retry em colisao no nivel do repositorio."""

    def __init__(self, length: int = 7) -> None:
        if length < 3:
            raise ValueError("length minimo eh 3")
        self._length = length

    def generate(self) -> Slug:
        return Slug("".join(secrets.choice(_ALPHABET) for _ in range(self._length)))
