from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from urlshort.domain.exceptions import DomainError


class InvalidTokenError(DomainError):
    def __init__(self, reason: str = "token invalido") -> None:
        super().__init__(reason)


class JwtService:
    def __init__(
        self,
        *,
        secret_key: str,
        algorithm: str,
        access_token_expire_minutes: int,
    ) -> None:
        self._secret = secret_key
        self._algorithm = algorithm
        self._access_ttl = timedelta(minutes=access_token_expire_minutes)

    def create_access_token(self, subject: str) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": subject,
            "iat": int(now.timestamp()),
            "exp": int((now + self._access_ttl).timestamp()),
            "jti": secrets.token_urlsafe(8),
            "type": "access",
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_access_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except JWTError as exc:
            raise InvalidTokenError(str(exc)) from exc
        if payload.get("type") != "access":
            raise InvalidTokenError("tipo de token invalido")
        sub = payload.get("sub")
        if not isinstance(sub, str):
            raise InvalidTokenError("subject ausente")
        return sub

    def create_refresh_token(self) -> str:
        return secrets.token_urlsafe(48)
