from __future__ import annotations

from redis.asyncio import Redis

from urlshort.domain.entities.click_event import ClickEvent


class RedisStreamPublisher:
    """Publica eventos de clique num Redis Stream.

    O worker (consumer group) le e persiste em click_events.
    """

    def __init__(self, client: Redis, *, stream: str) -> None:
        self._client = client
        self._stream = stream

    async def publish_click(self, event: ClickEvent) -> None:
        payload = {
            "short_url_id": str(event.short_url_id),
            "slug": event.slug,
            "ip": event.ip,
            "occurred_at": event.occurred_at.isoformat(),
            "referrer": event.referrer or "",
            "user_agent": event.user_agent.raw if event.user_agent else "",
        }
        await self._client.xadd(self._stream, payload)  # type: ignore[arg-type]
