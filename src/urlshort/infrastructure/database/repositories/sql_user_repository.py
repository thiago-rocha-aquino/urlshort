from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from urlshort.domain.entities.user import User
from urlshort.domain.value_objects.email import Email
from urlshort.infrastructure.database.mappers import user_mapper
from urlshort.infrastructure.database.models.user_model import UserModel


class SqlUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user: User) -> User:
        model = user_mapper.to_model(user)
        self._session.add(model)
        await self._session.flush()
        return user_mapper.to_entity(model)

    async def get_by_id(self, user_id: int) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return user_mapper.to_entity(model) if model else None

    async def get_by_email(self, email: Email) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email.value)
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        return user_mapper.to_entity(model) if model else None
