from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query, Request, status
from fastapi.responses import RedirectResponse

from urlshort.application.dto.url_dto import ResolveSlugInput
from urlshort.application.use_cases.redirect.resolve_slug import ResolveSlug
from urlshort.presentation.dependencies import get_resolve_slug

router = APIRouter(tags=["redirect"])


@router.get(
    "/{slug}",
    status_code=status.HTTP_302_FOUND,
    response_class=RedirectResponse,
    summary="Resolve um slug e redireciona para a URL alvo",
)
async def redirect(
    slug: str,
    request: Request,
    use_case: Annotated[ResolveSlug, Depends(get_resolve_slug)],
    user_agent: Annotated[str | None, Header(alias="User-Agent")] = None,
    referer: Annotated[str | None, Header(alias="Referer")] = None,
    password: Annotated[str | None, Query()] = None,
) -> RedirectResponse:
    client_ip = request.client.host if request.client else "unknown"
    target = await use_case.execute(
        ResolveSlugInput(
            slug=slug,
            ip=client_ip,
            user_agent=user_agent,
            referrer=referer,
            password=password,
        )
    )
    return RedirectResponse(target.value, status_code=status.HTTP_302_FOUND)
