from __future__ import annotations

from urlshort.application.dto.url_dto import CreateShortUrlInput
from urlshort.domain.entities.short_url import ShortUrl
from urlshort.domain.exceptions import SlugAlreadyTakenError
from urlshort.domain.ports.repositories import ShortUrlRepository
from urlshort.domain.ports.services import PasswordHasher
from urlshort.domain.services.slug_generator import SlugGenerator
from urlshort.domain.services.url_validator import UrlValidator
from urlshort.domain.value_objects.slug import Slug
from urlshort.domain.value_objects.url import Url

_MAX_SLUG_RETRY = 5


class CreateShortUrl:
    def __init__(
        self,
        urls: ShortUrlRepository,
        slug_generator: SlugGenerator,
        url_validator: UrlValidator,
        hasher: PasswordHasher,
    ) -> None:
        self._urls = urls
        self._slugs = slug_generator
        self._validator = url_validator
        self._hasher = hasher

    async def execute(self, data: CreateShortUrlInput) -> ShortUrl:
        target = Url(data.target)
        self._validator.validate(target)

        slug = await self._resolve_slug(data.custom_slug)

        password_hash = self._hasher.hash(data.password) if data.password else None

        entity = ShortUrl(
            user_id=data.user_id,
            slug=slug,
            target=target,
            expires_at=data.expires_at,
            max_clicks=data.max_clicks,
            password_hash=password_hash,
        )
        return await self._urls.add(entity)

    async def _resolve_slug(self, custom: str | None) -> Slug:
        if custom:
            slug = Slug(custom)
            if await self._urls.get_by_slug(slug) is not None:
                raise SlugAlreadyTakenError(slug.value)
            return slug

        for _ in range(_MAX_SLUG_RETRY):
            slug = self._slugs.generate()
            if await self._urls.get_by_slug(slug) is None:
                return slug
        # se chegamos aqui, algo muito errado
        raise SlugAlreadyTakenError("colisoes consecutivas ao gerar slug")
