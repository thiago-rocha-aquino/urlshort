from __future__ import annotations

from urlshort.domain.entities.short_url import ShortUrl
from urlshort.domain.value_objects.slug import Slug
from urlshort.domain.value_objects.url import Url
from urlshort.infrastructure.database.models.short_url_model import ShortUrlModel


def to_entity(model: ShortUrlModel) -> ShortUrl:
    return ShortUrl(
        id=model.id,
        user_id=model.user_id,
        slug=Slug(model.slug),
        target=Url(model.target),
        expires_at=model.expires_at,
        max_clicks=model.max_clicks,
        click_count=model.click_count,
        password_hash=model.password_hash,
        is_active=model.is_active,
        created_at=model.created_at,
    )


def to_model(entity: ShortUrl) -> ShortUrlModel:
    return ShortUrlModel(
        id=entity.id,
        user_id=entity.user_id,
        slug=entity.slug.value,
        target=entity.target.value,
        expires_at=entity.expires_at,
        max_clicks=entity.max_clicks,
        click_count=entity.click_count,
        password_hash=entity.password_hash,
        is_active=entity.is_active,
    )
