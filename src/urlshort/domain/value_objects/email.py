from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Self

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not _EMAIL_RE.match(normalized):
            raise ValueError(f"Email invalido: {self.value!r}")
        object.__setattr__(self, "value", normalized)

    @classmethod
    def of(cls, value: str) -> Self:
        return cls(value)

    def __str__(self) -> str:
        return self.value
