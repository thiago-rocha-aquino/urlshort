from __future__ import annotations

from urlshort.application.dto.url_dto import ResolveSlugInput
from urlshort.domain.entities.click_event import ClickEvent
from urlshort.domain.exceptions import EntityNotFoundError, WrongPasswordError
from urlshort.domain.ports.repositories import ShortUrlRepository
from urlshort.domain.ports.services import (
    EventPublisherPort,
    PasswordHasher,
    UrlCachePort,
)
from urlshort.domain.value_objects.slug import Slug
from urlshort.domain.value_objects.url import Url


class ResolveSlug:
    """Resolve um slug em URL alvo. Caminho hot path do servico.

    Estrategia:
    1. Tenta cache (slug -> Url). Se hit e a URL nao tem senha/restricoes,
       retorna direto sem tocar no DB.
    2. Senao, busca no DB, valida (expirado, max clicks, senha), atualiza cache.
    3. Publica evento de clique no Redis Stream em background.
    """

    def __init__(
        self,
        urls: ShortUrlRepository,
        cache: UrlCachePort,
        events: EventPublisherPort,
        hasher: PasswordHasher,
    ) -> None:
        self._urls = urls
        self._cache = cache
        self._events = events
        self._hasher = hasher

    async def execute(self, data: ResolveSlugInput) -> Url:
        slug = Slug(data.slug)

        cached = await self._cache.get(slug)
        if cached is not None:
            # Mesmo no caminho rapido, ainda precisamos buscar o ID/restricoes
            # para registrar o clique e fazer dedupe de increment.
            short_url = await self._urls.get_by_slug(slug)
            if short_url is None:
                # cache stale: alguem deletou. limpa.
                await self._cache.invalidate(slug)
                raise EntityNotFoundError("ShortUrl", data.slug)
        else:
            short_url = await self._urls.get_by_slug(slug)
            if short_url is None:
                raise EntityNotFoundError("ShortUrl", data.slug)

        short_url.ensure_resolvable()

        if short_url.is_password_protected() and (
            not data.password
            or not self._hasher.verify(data.password, short_url.password_hash or "")
        ):
            raise WrongPasswordError()

        # popula cache so se nao tiver senha (resposta direta nas proximas)
        if not short_url.is_password_protected() and cached is None:
            await self._cache.set(slug, short_url.target)

        # registra evento (assincrono via stream)
        assert short_url.id is not None
        event = ClickEvent(
            short_url_id=short_url.id,
            slug=short_url.slug.value,
            ip=data.ip,
            referrer=data.referrer,
        )
        # carrega user agent raw para o worker parsear
        if data.user_agent:
            from urlshort.domain.value_objects.user_agent_info import (
                DeviceType,
                UserAgentInfo,
            )

            event.user_agent = UserAgentInfo(raw=data.user_agent, device_type=DeviceType.UNKNOWN)

        await self._events.publish_click(event)
        await self._urls.increment_click_count(short_url.id)

        return short_url.target
