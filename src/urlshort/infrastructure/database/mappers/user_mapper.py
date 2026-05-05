from __future__ import annotations

from urlshort.domain.entities.user import User
from urlshort.domain.value_objects.email import Email
from urlshort.infrastructure.database.models.user_model import UserModel


def to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        email=Email(model.email),
        password_hash=model.password_hash,
        name=model.name,
        is_active=model.is_active,
        created_at=model.created_at,
    )


def to_model(entity: User) -> UserModel:
    return UserModel(
        id=entity.id,
        email=entity.email.value,
        password_hash=entity.password_hash,
        name=entity.name,
        is_active=entity.is_active,
    )
