from __future__ import annotations

from datetime import UTC, date, datetime, time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from urlshort.infrastructure.database.models.refresh_token_model import RefreshTokenModel


class SqlRefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def store(self, token: str, user_id: int, expires_at: date) -> None:
        model = RefreshTokenModel(
            token=token,
            user_id=user_id,
            expires_at=datetime.combine(expires_at, time.max, tzinfo=UTC),
        )
        self._session.add(model)
        await self._session.flush()

    async def get_user_id(self, token: str) -> int | None:
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        if model is None or model.revoked_at is not None:
            return None
        if model.expires_at < datetime.now(UTC):
            return None
        return model.user_id

    async def revoke(self, token: str) -> None:
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        if model is not None and model.revoked_at is None:
            model.revoked_at = datetime.now(UTC)
            await self._session.flush()
