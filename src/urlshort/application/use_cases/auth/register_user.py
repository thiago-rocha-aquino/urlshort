from __future__ import annotations

from urlshort.application.dto.auth_dto import RegisterUserInput
from urlshort.domain.entities.user import User
from urlshort.domain.exceptions import DuplicateEntityError
from urlshort.domain.ports.repositories import UserRepository
from urlshort.domain.ports.services import PasswordHasher
from urlshort.domain.value_objects.email import Email


class RegisterUser:
    def __init__(self, users: UserRepository, hasher: PasswordHasher) -> None:
        self._users = users
        self._hasher = hasher

    async def execute(self, data: RegisterUserInput) -> User:
        email = Email(data.email)
        if await self._users.get_by_email(email) is not None:
            raise DuplicateEntityError("User", "email", email.value)
        user = User(
            email=email,
            password_hash=self._hasher.hash(data.password),
            name=data.name.strip(),
        )
        return await self._users.add(user)
