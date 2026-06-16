from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from urlshort.application.dto.auth_dto import LoginInput, RegisterUserInput
from urlshort.application.use_cases.auth.login import Login
from urlshort.application.use_cases.auth.logout import Logout
from urlshort.application.use_cases.auth.refresh_token import RefreshToken
from urlshort.application.use_cases.auth.register_user import RegisterUser
from urlshort.presentation.dependencies import (
    CurrentUser,
    get_login,
    get_logout,
    get_refresh_token,
    get_register_user,
)
from urlshort.presentation.schemas.auth_schema import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    use_case: Annotated[RegisterUser, Depends(get_register_user)],
) -> UserResponse:
    user = await use_case.execute(
        RegisterUserInput(email=body.email, password=body.password, name=body.name)
    )
    assert user.id is not None
    return UserResponse(
        id=user.id, email=user.email.value, name=user.name, is_active=user.is_active
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    use_case: Annotated[Login, Depends(get_login)],
) -> TokenResponse:
    pair = await use_case.execute(LoginInput(email=body.email, password=body.password))
    return TokenResponse(access_token=pair.access_token, refresh_token=pair.refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    use_case: Annotated[RefreshToken, Depends(get_refresh_token)],
) -> TokenResponse:
    pair = await use_case.execute(body.refresh_token)
    return TokenResponse(access_token=pair.access_token, refresh_token=pair.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    body: RefreshRequest,
    use_case: Annotated[Logout, Depends(get_logout)],
) -> None:
    await use_case.execute(body.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser) -> UserResponse:
    assert current_user.id is not None
    return UserResponse(
        id=current_user.id,
        email=current_user.email.value,
        name=current_user.name,
        is_active=current_user.is_active,
    )
