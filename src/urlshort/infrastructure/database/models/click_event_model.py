from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from urlshort.infrastructure.database.models.base import Base


class ClickEventModel(Base):
    __tablename__ = "click_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    short_url_id: Mapped[int] = mapped_column(
        ForeignKey("short_urls.id", ondelete="CASCADE"), index=True, nullable=False
    )
    slug: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    ip: Mapped[str] = mapped_column(String(45), nullable=False)
    referrer: Mapped[str | None] = mapped_column(String(500), nullable=True)
    referrer_host: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    browser: Mapped[str | None] = mapped_column(String(64), nullable=True)
    os: Mapped[str | None] = mapped_column(String(64), nullable=True)
    device_type: Mapped[str] = mapped_column(String(16), nullable=False, default="unknown")
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    country_code: Mapped[str | None] = mapped_column(String(2), nullable=True, index=True)
    country_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
