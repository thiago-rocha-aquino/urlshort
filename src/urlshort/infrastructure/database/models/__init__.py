"""Importa todos os models para registra-los na Base.metadata."""

from urlshort.infrastructure.database.models.base import Base
from urlshort.infrastructure.database.models.click_event_model import ClickEventModel
from urlshort.infrastructure.database.models.refresh_token_model import RefreshTokenModel
from urlshort.infrastructure.database.models.short_url_model import ShortUrlModel
from urlshort.infrastructure.database.models.url_stats_model import UrlStatsDailyModel
from urlshort.infrastructure.database.models.user_model import UserModel

__all__ = [
    "Base",
    "ClickEventModel",
    "RefreshTokenModel",
    "ShortUrlModel",
    "UrlStatsDailyModel",
    "UserModel",
]
