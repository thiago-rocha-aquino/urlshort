from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from urlshort.application.dto.url_dto import CreateShortUrlInput
from urlshort.application.use_cases.urls.create_short_url import CreateShortUrl
from urlshort.application.use_cases.urls.delete_short_url import DeleteShortUrl
from urlshort.application.use_cases.urls.list_short_urls import ListShortUrls
from urlshort.domain.entities.short_url import ShortUrl
from urlshort.presentation.dependencies import (
    ContainerDep,
    CurrentUser,
    get_create_short_url,
    get_delete_short_url,
    get_list_short_urls,
)
from urlshort.presentation.schemas.url_schema import CreateUrlRequest, ShortUrlResponse

router = APIRouter(prefix="/api/urls", tags=["urls"])


def _to_response(c: ContainerDep, url: ShortUrl) -> ShortUrlResponse:
    assert url.id is not None
    return ShortUrlResponse(
        id=url.id,
        slug=url.slug.value,
        short_url=f"{c.settings.app_base_url.rstrip('/')}/{url.slug.value}",
        target=url.target.value,
        expires_at=url.expires_at,
        max_clicks=url.max_clicks,
        click_count=url.click_count,
        is_password_protected=url.is_password_protected(),
        is_active=url.is_active,
        created_at=url.created_at,
    )


@router.post("", response_model=ShortUrlResponse, status_code=status.HTTP_201_CREATED)
async def create(
    body: CreateUrlRequest,
    container: ContainerDep,
    current_user: CurrentUser,
    use_case: Annotated[CreateShortUrl, Depends(get_create_short_url)],
) -> ShortUrlResponse:
    assert current_user.id is not None
    rl_ok = await container.rate_limiter.hit(
        f"create:{current_user.id}",
        limit=container.settings.rate_limit_create_per_minute,
        window_seconds=60,
    )
    if not rl_ok:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, detail="rate limit exceeded")
    url = await use_case.execute(
        CreateShortUrlInput(
            user_id=current_user.id,
            target=str(body.target),
            custom_slug=body.custom_slug,
            expires_at=body.expires_at,
            max_clicks=body.max_clicks,
            password=body.password,
        )
    )
    return _to_response(container, url)


@router.get("", response_model=list[ShortUrlResponse])
async def list_urls(
    container: ContainerDep,
    current_user: CurrentUser,
    use_case: Annotated[ListShortUrls, Depends(get_list_short_urls)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[ShortUrlResponse]:
    assert current_user.id is not None
    items = await use_case.execute(current_user.id, limit=limit, offset=offset)
    return [_to_response(container, u) for u in items]


@router.delete("/{url_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_url(
    url_id: int,
    current_user: CurrentUser,
    use_case: Annotated[DeleteShortUrl, Depends(get_delete_short_url)],
) -> None:
    assert current_user.id is not None
    await use_case.execute(user_id=current_user.id, url_id=url_id)
