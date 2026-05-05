from __future__ import annotations

from redis.asyncio import Redis


class RedisRateLimiter:
    """Rate limiter por janela fixa usando INCR + EXPIRE.

    Simples e efetivo para o caso de uso; nao eh exatamente token bucket,
    mas para criacao de URLs (operacao rara por usuario) basta.
    """

    def __init__(self, client: Redis, *, prefix: str = "urlshort:rl:") -> None:
        self._client = client
        self._prefix = prefix

    async def hit(self, key: str, *, limit: int, window_seconds: int) -> bool:
        full_key = f"{self._prefix}{key}"
        pipe = self._client.pipeline()
        pipe.incr(full_key, 1)
        pipe.expire(full_key, window_seconds)
        result = await pipe.execute()
        count = int(result[0])
        return count <= limit
