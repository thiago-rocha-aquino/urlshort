from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from urlshort.application.dto.auth_dto import TokenPair
from urlshort.domain.exceptions import InvalidCredentialsError
from urlshort.domain.ports.repositories import RefreshTokenRepository
from urlshort.domain.ports.services import TokenService


class RefreshToken:
    def __init__(
        self,
        refresh_tokens: RefreshTokenRepository,
        tokens: TokenService,
        *,
        refresh_ttl_days: int,
    ) -> None:
        self._refresh_tokens = refresh_tokens
        self._tokens = tokens
        self._refresh_ttl = timedelta(days=refresh_ttl_days)

    async def execute(self, refresh_token: str) -> TokenPair:
        user_id = await self._refresh_tokens.get_user_id(refresh_token)
        if user_id is None:
            raise InvalidCredentialsError()

        await self._refresh_tokens.revoke(refresh_token)

        new_access = self._tokens.create_access_token(str(user_id))
        new_refresh = self._tokens.create_refresh_token()
        expires_at: date = (datetime.now(UTC) + self._refresh_ttl).date()
        await self._refresh_tokens.store(new_refresh, user_id, expires_at)
        return TokenPair(access_token=new_access, refresh_token=new_refresh)
