from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Self

# slug: ASCII alfanumerico + hifen/underscore, 3-50 chars
_SLUG_RE = re.compile(r"^[A-Za-z0-9_-]{3,50}$")


@dataclass(frozen=True, slots=True)
class Slug:
    value: str

    def __post_init__(self) -> None:
        if not _SLUG_RE.match(self.value):
            raise ValueError(
                f"slug invalido: {self.value!r} (deve ter 3-50 chars, A-Z a-z 0-9 _ -)"
            )

    @classmethod
    def of(cls, value: str) -> Self:
        return cls(value)

    def __str__(self) -> str:
        return self.value
