from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from urlshort.application.use_cases.analytics.get_url_stats import GetUrlStats
from urlshort.application.use_cases.analytics.list_recent_clicks import ListRecentClicks
from urlshort.presentation.dependencies import (
    ContainerDep,
    CurrentUser,
    SessionDep,
)
from urlshort.presentation.schemas.analytics_schema import (
    BreakdownItem,
    ClickEventResponse,
    StatsResponse,
    TimelinePoint,
)

router = APIRouter(prefix="/api/urls/{url_id}/analytics", tags=["analytics"])


def _make_get_stats(_: ContainerDep, session: SessionDep) -> GetUrlStats:
    from urlshort.infrastructure.database.repositories.sql_click_event_repository import (
        SqlClickEventRepository,
    )
    from urlshort.infrastructure.database.repositories.sql_short_url_repository import (
        SqlShortUrlRepository,
    )
    from urlshort.infrastructure.database.repositories.sql_url_stats_repository import (
        SqlUrlStatsRepository,
    )

    return GetUrlStats(
        SqlShortUrlRepository(session),
        SqlClickEventRepository(session),
        SqlUrlStatsRepository(session),
    )


def _make_list_clicks(_: ContainerDep, session: SessionDep) -> ListRecentClicks:
    from urlshort.infrastructure.database.repositories.sql_click_event_repository import (
        SqlClickEventRepository,
    )
    from urlshort.infrastructure.database.repositories.sql_short_url_repository import (
        SqlShortUrlRepository,
    )

    return ListRecentClicks(SqlShortUrlRepository(session), SqlClickEventRepository(session))


@router.get("", response_model=StatsResponse)
async def get_stats(
    url_id: int,
    current_user: CurrentUser,
    use_case: Annotated[GetUrlStats, Depends(_make_get_stats)],
    days: Annotated[int, Query(ge=1, le=365)] = 30,
) -> StatsResponse:
    assert current_user.id is not None
    end = datetime.now(UTC).date()
    start = end - timedelta(days=days)
    summary = await use_case.execute(user_id=current_user.id, url_id=url_id, start=start, end=end)
    return StatsResponse(
        url_id=url_id,
        period_start=start,
        period_end=end,
        total_clicks=summary.total_clicks,
        timeline=[TimelinePoint(day=p.day, clicks=p.clicks) for p in summary.timeline],
        countries=[
            BreakdownItem(label=label, clicks=clicks) for label, clicks in summary.countries
        ],
        devices=[BreakdownItem(label=label, clicks=clicks) for label, clicks in summary.devices],
        referrers=[
            BreakdownItem(label=label, clicks=clicks) for label, clicks in summary.referrers
        ],
    )


@router.get("/recent", response_model=list[ClickEventResponse])
async def get_recent(
    url_id: int,
    current_user: CurrentUser,
    use_case: Annotated[ListRecentClicks, Depends(_make_list_clicks)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[ClickEventResponse]:
    assert current_user.id is not None
    events = await use_case.execute(
        user_id=current_user.id, url_id=url_id, limit=limit, offset=offset
    )
    return [
        ClickEventResponse(
            id=e.id or 0,
            occurred_at=e.occurred_at,
            ip=e.ip,
            country_code=e.country_code,
            city=e.geo.city,
            device_type=e.device_type.value,
            browser=e.user_agent.browser if e.user_agent else None,
            os=e.user_agent.os if e.user_agent else None,
            is_bot=e.is_bot,
            referrer=e.referrer,
        )
        for e in events
    ]
