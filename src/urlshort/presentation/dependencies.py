from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from urlshort.application.use_cases.auth.login import Login
from urlshort.application.use_cases.auth.logout import Logout
from urlshort.application.use_cases.auth.refresh_token import RefreshToken
from urlshort.application.use_cases.auth.register_user import RegisterUser
from urlshort.application.use_cases.redirect.resolve_slug import ResolveSlug
from urlshort.application.use_cases.urls.create_short_url import CreateShortUrl
from urlshort.application.use_cases.urls.delete_short_url import DeleteShortUrl
from urlshort.application.use_cases.urls.list_short_urls import ListShortUrls
from urlshort.container import (
    Container,
    build_container,
    make_create_short_url,
    make_delete_short_url,
    make_list_short_urls,
    make_login,
    make_logout,
    make_refresh_token,
    make_register_user,
    make_resolve_slug,
)
from urlshort.domain.entities.user import User
from urlshort.domain.exceptions import EntityNotFoundError
from urlshort.infrastructure.auth.jwt_service import InvalidTokenError
from urlshort.infrastructure.database.repositories.sql_user_repository import SqlUserRepository
from urlshort.infrastructure.database.session import session_scope


async def get_session() -> AsyncIterator[AsyncSession]:
    async with session_scope() as session:
        yield session


def get_container() -> Container:
    return build_container()


SessionDep = Annotated[AsyncSession, Depends(get_session)]
ContainerDep = Annotated[Container, Depends(get_container)]


def get_register_user(c: ContainerDep, s: SessionDep) -> RegisterUser:
    return make_register_user(c, s)


def get_login(c: ContainerDep, s: SessionDep) -> Login:
    return make_login(c, s)


def get_refresh_token(c: ContainerDep, s: SessionDep) -> RefreshToken:
    return make_refresh_token(c, s)


def get_logout(c: ContainerDep, s: SessionDep) -> Logout:
    return make_logout(c, s)


def get_create_short_url(c: ContainerDep, s: SessionDep) -> CreateShortUrl:
    return make_create_short_url(c, s)


def get_list_short_urls(c: ContainerDep, s: SessionDep) -> ListShortUrls:
    return make_list_short_urls(c, s)


def get_delete_short_url(c: ContainerDep, s: SessionDep) -> DeleteShortUrl:
    return make_delete_short_url(c, s)


def get_resolve_slug(c: ContainerDep, s: SessionDep) -> ResolveSlug:
    return make_resolve_slug(c, s)


async def get_current_user(
    container: ContainerDep,
    session: SessionDep,
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        subject = container.tokens.decode_access_token(token)
    except InvalidTokenError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc
    user = await SqlUserRepository(session).get_by_id(int(subject))
    if user is None or not user.is_active:
        raise EntityNotFoundError("User", subject)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
