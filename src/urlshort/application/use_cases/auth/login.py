from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from urlshort.application.dto.auth_dto import LoginInput, TokenPair
from urlshort.domain.exceptions import InvalidCredentialsError
from urlshort.domain.ports.repositories import RefreshTokenRepository, UserRepository
from urlshort.domain.ports.services import PasswordHasher, TokenService
from urlshort.domain.value_objects.email import Email


class Login:
    def __init__(
        self,
        users: UserRepository,
        refresh_tokens: RefreshTokenRepository,
        hasher: PasswordHasher,
        tokens: TokenService,
        *,
        refresh_ttl_days: int,
    ) -> None:
        self._users = users
        self._refresh_tokens = refresh_tokens
        self._hasher = hasher
        self._tokens = tokens
        self._refresh_ttl = timedelta(days=refresh_ttl_days)

    async def execute(self, data: LoginInput) -> TokenPair:
        try:
            email = Email(data.email)
        except ValueError as exc:
            raise InvalidCredentialsError() from exc

        user = await self._users.get_by_email(email)
        if user is None or not user.is_active:
            raise InvalidCredentialsError()
        if not self._hasher.verify(data.password, user.password_hash):
            raise InvalidCredentialsError()
        if user.id is None:
            raise InvalidCredentialsError()

        access = self._tokens.create_access_token(str(user.id))
        refresh = self._tokens.create_refresh_token()
        expires_at: date = (datetime.now(UTC) + self._refresh_ttl).date()
        await self._refresh_tokens.store(refresh, user.id, expires_at)
        return TokenPair(access_token=access, refresh_token=refresh)
