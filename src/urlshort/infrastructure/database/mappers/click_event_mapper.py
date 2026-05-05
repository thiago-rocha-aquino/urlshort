from __future__ import annotations

from urlshort.domain.entities.click_event import ClickEvent
from urlshort.domain.services.click_analyzer import ClickAnalyzer
from urlshort.domain.value_objects.geo_location import GeoLocation
from urlshort.domain.value_objects.user_agent_info import DeviceType, UserAgentInfo
from urlshort.infrastructure.database.models.click_event_model import ClickEventModel

_analyzer = ClickAnalyzer()


def to_entity(model: ClickEventModel) -> ClickEvent:
    ua_info: UserAgentInfo | None = None
    if model.user_agent:
        ua_info = UserAgentInfo(
            raw=model.user_agent,
            device_type=DeviceType(model.device_type),
            browser=model.browser,
            os=model.os,
            is_bot=model.is_bot,
        )
    return ClickEvent(
        id=model.id,
        short_url_id=model.short_url_id,
        slug=model.slug,
        ip=model.ip,
        occurred_at=model.occurred_at,
        referrer=model.referrer,
        user_agent=ua_info,
        geo=GeoLocation(
            country_code=model.country_code,
            country_name=model.country_name,
            city=model.city,
        ),
    )


def to_model(entity: ClickEvent) -> ClickEventModel:
    return ClickEventModel(
        id=entity.id,
        short_url_id=entity.short_url_id,
        slug=entity.slug,
        occurred_at=entity.occurred_at,
        ip=entity.ip,
        referrer=entity.referrer,
        referrer_host=_analyzer.referrer_host(entity.referrer),
        user_agent=entity.user_agent.raw if entity.user_agent else None,
        browser=entity.user_agent.browser if entity.user_agent else None,
        os=entity.user_agent.os if entity.user_agent else None,
        device_type=entity.device_type.value,
        is_bot=entity.is_bot,
        country_code=entity.geo.country_code,
        country_name=entity.geo.country_name,
        city=entity.geo.city,
    )
