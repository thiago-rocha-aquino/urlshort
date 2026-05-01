from __future__ import annotations

from urlshort.domain.ports.repositories import RefreshTokenRepository


class Logout:
    def __init__(self, refresh_tokens: RefreshTokenRepository) -> None:
        self._refresh_tokens = refresh_tokens

    async def execute(self, refresh_token: str) -> None:
        await self._refresh_tokens.revoke(refresh_token)
