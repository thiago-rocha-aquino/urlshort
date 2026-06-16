from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from urlshort.presentation.dependencies import ContainerDep, SessionDep

router = APIRouter(prefix="/health", tags=["meta"])


@router.get("")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/db")
async def health_db(session: SessionDep) -> dict[str, str]:
    try:
        result = await session.execute(text("SELECT 1"))
        if result.scalar() != 1:
            raise SQLAlchemyError("unexpected scalar")
    except SQLAlchemyError as exc:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"db unavailable: {exc}"
        ) from exc
    return {"status": "ok", "db": "ok"}


@router.get("/redis")
async def health_redis(container: ContainerDep) -> dict[str, str]:
    try:
        result = container.redis.ping()
        pong = bool(await result) if hasattr(result, "__await__") else bool(result)
    except Exception as exc:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"redis unavailable: {exc}"
        ) from exc
    if not pong:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail="redis ping failed")
    return {"status": "ok", "redis": "ok"}
