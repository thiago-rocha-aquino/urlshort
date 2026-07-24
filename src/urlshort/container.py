"""Composition root: monta as dependencias usadas pelos use cases."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from urlshort.application.use_cases.auth.login import Login
from urlshort.application.use_cases.auth.logout import Logout
from urlshort.application.use_cases.auth.refresh_token import RefreshToken
from urlshort.application.use_cases.auth.register_user import RegisterUser
from urlshort.application.use_cases.redirect.resolve_slug import ResolveSlug
from urlshort.application.use_cases.urls.create_short_url import CreateShortUrl
from urlshort.application.use_cases.urls.delete_short_url import DeleteShortUrl
from urlshort.application.use_cases.urls.list_short_urls import ListShortUrls
from urlshort.domain.services.click_analyzer import ClickAnalyzer
from urlshort.domain.services.slug_generator import RandomBase62SlugGenerator
from urlshort.domain.services.url_validator import UrlValidator
from urlshort.infrastructure.auth.bcrypt_hasher import BcryptHasher
from urlshort.infrastructure.auth.jwt_service import JwtService
from urlshort.infrastructure.cache.redis_cache import RedisUrlCache
from urlshort.infrastructure.cache.redis_client import get_redis
from urlshort.infrastructure.cache.redis_rate_limiter import RedisRateLimiter
from urlshort.infrastructure.config import Settings, get_settings
from urlshort.infrastructure.database.repositories.sql_click_event_repository import (
    SqlClickEventRepository,
)
from urlshort.infrastructure.database.repositories.sql_refresh_token_repository import (
    SqlRefreshTokenRepository,
)
from urlshort.infrastructure.database.repositories.sql_short_url_repository import (
    SqlShortUrlRepository,
)
from urlshort.infrastructure.database.repositories.sql_url_stats_repository import (
    SqlUrlStatsRepository,
)
from urlshort.infrastructure.database.repositories.sql_user_repository import SqlUserRepository
from urlshort.infrastructure.events.redis_publisher import RedisStreamPublisher
from urlshort.infrastructure.geo.maxmind_lookup import MaxMindGeoLookup


@dataclass(frozen=True, slots=True)
class Container:
    settings: Settings
    redis: Redis
    hasher: BcryptHasher
    tokens: JwtService
    slug_generator: RandomBase62SlugGenerator
    url_validator: UrlValidator
    cache: RedisUrlCache
    publisher: RedisStreamPublisher
    rate_limiter: RedisRateLimiter
    geo: MaxMindGeoLookup
    click_analyzer: ClickAnalyzer


def build_container() -> Container:
    settings = get_settings()
    redis = get_redis()
    base_host = urlparse(settings.app_base_url).hostname
    return Container(
        settings=settings,
        redis=redis,
        hasher=BcryptHasher(),
        tokens=JwtService(
            secret_key=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
            access_token_expire_minutes=settings.jwt_access_token_expire_minutes,
        ),
        slug_generator=RandomBase62SlugGenerator(length=settings.slug_length),
        url_validator=UrlValidator(base_url_host=base_host),
        cache=RedisUrlCache(redis),
        publisher=RedisStreamPublisher(redis, stream=settings.redis_stream_name),
        rate_limiter=RedisRateLimiter(redis),
        geo=MaxMindGeoLookup(settings.geoip_database_path or None),
        click_analyzer=ClickAnalyzer(),
    )


# --- auth ---


def make_register_user(c: Container, session: AsyncSession) -> RegisterUser:
    return RegisterUser(SqlUserRepository(session), c.hasher)


def make_login(c: Container, session: AsyncSession) -> Login:
    return Login(
        users=SqlUserRepository(session),
        refresh_tokens=SqlRefreshTokenRepository(session),
        hasher=c.hasher,
        tokens=c.tokens,
        refresh_ttl_days=c.settings.jwt_refresh_token_expire_days,
    )


def make_refresh_token(c: Container, session: AsyncSession) -> RefreshToken:
    return RefreshToken(
        refresh_tokens=SqlRefreshTokenRepository(session),
        tokens=c.tokens,
        refresh_ttl_days=c.settings.jwt_refresh_token_expire_days,
    )


def make_logout(_: Container, session: AsyncSession) -> Logout:
    return Logout(SqlRefreshTokenRepository(session))


# --- urls ---


def make_create_short_url(c: Container, session: AsyncSession) -> CreateShortUrl:
    return CreateShortUrl(
        urls=SqlShortUrlRepository(session),
        slug_generator=c.slug_generator,
        url_validator=c.url_validator,
        hasher=c.hasher,
    )


def make_list_short_urls(_: Container, session: AsyncSession) -> ListShortUrls:
    return ListShortUrls(SqlShortUrlRepository(session))


def make_delete_short_url(c: Container, session: AsyncSession) -> DeleteShortUrl:
    return DeleteShortUrl(SqlShortUrlRepository(session), c.cache)


# --- redirect ---


def make_resolve_slug(c: Container, session: AsyncSession) -> ResolveSlug:
    return ResolveSlug(
        urls=SqlShortUrlRepository(session),
        cache=c.cache,
        events=c.publisher,
        hasher=c.hasher,
    )


# --- helpers para outros componentes acessarem ---


def make_click_event_repo(_: Container, session: AsyncSession) -> SqlClickEventRepository:
    return SqlClickEventRepository(session)


def make_url_stats_repo(_: Container, session: AsyncSession) -> SqlUrlStatsRepository:
    return SqlUrlStatsRepository(session)
