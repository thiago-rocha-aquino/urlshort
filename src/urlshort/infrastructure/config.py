from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "api_url_shortener"
    app_env: str = "development"
    app_debug: bool = False
    app_host: str = "0.0.0.0"
    app_port: int = 8001
    app_base_url: str = "http://localhost:8001"

    database_url: str = Field(
        default="postgresql+asyncpg://urlshort:urlshort@localhost:5433/urlshort",
    )

    redis_url: str = "redis://localhost:6379/0"
    redis_stream_name: str = "urlshort:click_events"
    redis_consumer_group: str = "urlshort-workers"

    jwt_secret_key: str = Field(default="change-me")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    slug_length: int = 7

    geoip_database_path: str = ""

    rate_limit_create_per_minute: int = 20


@lru_cache
def get_settings() -> Settings:
    return Settings()
