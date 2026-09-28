from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.fixture(autouse=True)
def _low_rate_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_CREATE_PER_MINUTE", "3")


async def _login(client: AsyncClient) -> str:
    await client.post(
        "/api/auth/register",
        json={"email": "rl@x.com", "password": "12345678", "name": "RL"},
    )
    r = await client.post("/api/auth/login", json={"email": "rl@x.com", "password": "12345678"})
    return str(r.json()["access_token"])


async def test_rate_limit_corta_apos_n_requests(client: AsyncClient) -> None:
    token = await _login(client)
    headers = {"Authorization": f"Bearer {token}"}

    statuses = []
    for i in range(5):
        r = await client.post(
            "/api/urls",
            headers=headers,
            json={"target": f"https://example.com/{i}"},
        )
        statuses.append(r.status_code)

    assert statuses[0] == 201
    assert 429 in statuses, f"esperava 429 entre {statuses}"
