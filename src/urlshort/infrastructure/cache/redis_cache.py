from __future__ import annotations

from redis.asyncio import Redis

from urlshort.domain.value_objects.slug import Slug
from urlshort.domain.value_objects.url import Url


class RedisUrlCache:
    """Cache slug -> target URL no Redis.

    Mantemos chave-valor simples; URLs com senha NAO sao cacheadas
    (a verificacao precisa acontecer no DB todo redirect).
    """

    def __init__(self, client: Redis, *, prefix: str = "urlshort:slug:") -> None:
        self._client = client
        self._prefix = prefix

    def _key(self, slug: Slug) -> str:
        return f"{self._prefix}{slug.value}"

    async def get(self, slug: Slug) -> Url | None:
        raw = await self._client.get(self._key(slug))
        if raw is None:
            return None
        decoded = raw.decode() if isinstance(raw, bytes) else raw
        try:
            return Url(decoded)
        except ValueError:
            return None

    async def set(self, slug: Slug, url: Url, *, ttl_seconds: int = 3600) -> None:
        await self._client.set(self._key(slug), url.value, ex=ttl_seconds)

    async def invalidate(self, slug: Slug) -> None:
        await self._client.delete(self._key(slug))
