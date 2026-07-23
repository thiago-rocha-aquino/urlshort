from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from urlshort.domain.exceptions import (
    DomainError,
    DuplicateEntityError,
    EntityNotFoundError,
    ForbiddenError,
    InvalidCredentialsError,
    SlugAlreadyTakenError,
    UrlExpiredError,
    UrlMaxClicksReachedError,
    WrongPasswordError,
)
from urlshort.infrastructure.auth.jwt_service import InvalidTokenError


def _json(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": code, "message": message})


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(InvalidCredentialsError)
    async def _ic(_: Request, exc: InvalidCredentialsError) -> JSONResponse:
        return _json(status.HTTP_401_UNAUTHORIZED, "invalid_credentials", str(exc))

    @app.exception_handler(InvalidTokenError)
    async def _it(_: Request, exc: InvalidTokenError) -> JSONResponse:
        return _json(status.HTTP_401_UNAUTHORIZED, "invalid_token", str(exc))

    @app.exception_handler(EntityNotFoundError)
    async def _nf(_: Request, exc: EntityNotFoundError) -> JSONResponse:
        return _json(status.HTTP_404_NOT_FOUND, "not_found", str(exc))

    @app.exception_handler(DuplicateEntityError)
    async def _dup(_: Request, exc: DuplicateEntityError) -> JSONResponse:
        return _json(status.HTTP_409_CONFLICT, "duplicate", str(exc))

    @app.exception_handler(SlugAlreadyTakenError)
    async def _slug(_: Request, exc: SlugAlreadyTakenError) -> JSONResponse:
        return _json(status.HTTP_409_CONFLICT, "slug_taken", str(exc))

    @app.exception_handler(ForbiddenError)
    async def _fb(_: Request, exc: ForbiddenError) -> JSONResponse:
        return _json(status.HTTP_403_FORBIDDEN, "forbidden", str(exc))

    @app.exception_handler(UrlExpiredError)
    async def _exp(_: Request, exc: UrlExpiredError) -> JSONResponse:
        return _json(status.HTTP_410_GONE, "url_expired", str(exc))

    @app.exception_handler(UrlMaxClicksReachedError)
    async def _mc(_: Request, exc: UrlMaxClicksReachedError) -> JSONResponse:
        return _json(status.HTTP_410_GONE, "url_max_clicks", str(exc))

    @app.exception_handler(WrongPasswordError)
    async def _wp(_: Request, exc: WrongPasswordError) -> JSONResponse:
        return _json(status.HTTP_401_UNAUTHORIZED, "wrong_password", str(exc))

    @app.exception_handler(DomainError)
    async def _de(_: Request, exc: DomainError) -> JSONResponse:
        return _json(status.HTTP_400_BAD_REQUEST, "domain_error", str(exc))
