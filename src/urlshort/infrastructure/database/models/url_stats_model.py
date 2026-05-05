from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from urlshort.infrastructure.database.models.base import Base


class UrlStatsDailyModel(Base):
    __tablename__ = "url_stats_daily"
    __table_args__ = (
        UniqueConstraint(
            "short_url_id",
            "day",
            "country_code",
            "device_type",
            "referrer_host",
            name="uq_stats_url_day_dim",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    short_url_id: Mapped[int] = mapped_column(
        ForeignKey("short_urls.id", ondelete="CASCADE"), index=True, nullable=False
    )
    day: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    country_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    device_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    referrer_host: Mapped[str | None] = mapped_column(String(255), nullable=True)
    clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
