from __future__ import annotations

from urlshort.domain.services.click_analyzer import ClickAnalyzer
from urlshort.domain.value_objects.user_agent_info import DeviceType


def test_parse_ua_mobile() -> None:
    a = ClickAnalyzer()
    ua = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    )
    info = a.parse_user_agent(ua)
    assert info is not None
    assert info.device_type == DeviceType.MOBILE
    assert info.browser is not None


def test_parse_ua_bot() -> None:
    a = ClickAnalyzer()
    info = a.parse_user_agent("Googlebot/2.1 (+http://www.google.com/bot.html)")
    assert info is not None
    assert info.is_bot
    assert info.device_type == DeviceType.BOT


def test_parse_ua_vazio() -> None:
    assert ClickAnalyzer().parse_user_agent(None) is None
    assert ClickAnalyzer().parse_user_agent("") is None


def test_referrer_host() -> None:
    a = ClickAnalyzer()
    assert a.referrer_host("https://twitter.com/some/path") == "twitter.com"
    assert a.referrer_host(None) is None
    assert a.referrer_host("") is None
