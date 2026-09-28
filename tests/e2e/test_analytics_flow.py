from __future__ import annotations

from datetime import UTC, datetime

from httpx import AsyncClient

from urlshort.jobs.aggregate_daily_stats import aggregate_day
from urlshort.jobs.click_event_worker import run as worker_run


async def _login(client: AsyncClient, email: str = "an@x.com") -> str:
    await client.post(
        "/api/auth/register",
        json={"email": email, "password": "12345678", "name": "An"},
    )
    r = await client.post("/api/auth/login", json={"email": email, "password": "12345678"})
    return str(r.json()["access_token"])


async def test_pipeline_analytics_completo(client: AsyncClient) -> None:
    token = await _login(client)
    headers = {"Authorization": f"Bearer {token}"}

    # cria URL
    r = await client.post(
        "/api/urls",
        headers=headers,
        json={"target": "https://example.com/x", "custom_slug": "ana-1"},
    )
    assert r.status_code == 201
    url_id = r.json()["id"]

    # 3 cliques com user-agents diferentes
    for ua in [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0)",  # mobile
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120",  # desktop
        "Googlebot/2.1 (+http://www.google.com/bot.html)",  # bot
    ]:
        r = await client.get(
            "/ana-1",
            headers={"User-Agent": ua, "Referer": "https://twitter.com/post"},
            follow_redirects=False,
        )
        assert r.status_code == 302

    # roda o worker o suficiente para drenar a stream (max_iterations=2 com block curto)
    await worker_run(max_iterations=3, block_ms=200)

    # agrega "hoje"
    today = datetime.now(UTC).date()
    n = await aggregate_day(today)
    assert n >= 1

    # endpoint de stats
    r = await client.get(f"/api/urls/{url_id}/analytics?days=2", headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total_clicks"] == 3
    devices = {item["label"]: item["clicks"] for item in body["devices"]}
    # esperamos pelo menos mobile e desktop e bot
    assert sum(devices.values()) == 3
    referrers = {item["label"]: item["clicks"] for item in body["referrers"]}
    assert referrers.get("twitter.com") == 3

    # endpoint de eventos recentes (le direto da granular)
    r = await client.get(f"/api/urls/{url_id}/analytics/recent", headers=headers)
    assert r.status_code == 200
    events = r.json()
    assert len(events) == 3
    assert {e["device_type"] for e in events} >= {"mobile", "desktop", "bot"}


async def test_analytics_de_outro_user_eh_403(client: AsyncClient) -> None:
    t1 = await _login(client, "o1@x.com")
    r = await client.post(
        "/api/urls",
        headers={"Authorization": f"Bearer {t1}"},
        json={"target": "https://example.com", "custom_slug": "z-z"},
    )
    url_id = r.json()["id"]

    t2 = await _login(client, "o2@x.com")
    r = await client.get(f"/api/urls/{url_id}/analytics", headers={"Authorization": f"Bearer {t2}"})
    assert r.status_code == 403
