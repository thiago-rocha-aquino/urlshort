from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from urlshort.domain.value_objects.email import Email


@dataclass(slots=True)
class User:
    email: Email
    password_hash: str
    name: str
    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True
