from __future__ import annotations

from urllib.parse import urlparse

from user_agents import parse as parse_user_agent

from urlshort.domain.value_objects.user_agent_info import DeviceType, UserAgentInfo


class ClickAnalyzer:
    """Extrai informacoes estruturadas de um clique cru."""

    def parse_user_agent(self, raw: str | None) -> UserAgentInfo | None:
        if not raw:
            return None
        ua = parse_user_agent(raw)
        device_type = self._classify_device(ua)
        return UserAgentInfo(
            raw=raw,
            device_type=device_type,
            browser=ua.browser.family if ua.browser.family else None,
            os=ua.os.family if ua.os.family else None,
            is_bot=bool(ua.is_bot),
        )

    def referrer_host(self, referrer: str | None) -> str | None:
        if not referrer:
            return None
        try:
            parsed = urlparse(referrer)
        except ValueError:
            return None
        return parsed.netloc.lower() or None

    @staticmethod
    def _classify_device(ua: object) -> DeviceType:
        if getattr(ua, "is_bot", False):
            return DeviceType.BOT
        if getattr(ua, "is_mobile", False):
            return DeviceType.MOBILE
        if getattr(ua, "is_tablet", False):
            return DeviceType.TABLET
        if getattr(ua, "is_pc", False):
            return DeviceType.DESKTOP
        return DeviceType.UNKNOWN
