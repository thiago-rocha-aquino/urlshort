from __future__ import annotations

from httpx import AsyncClient


async def test_health(client: AsyncClient) -> None:
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


async def test_health_db(client: AsyncClient) -> None:
    r = await client.get("/health/db")
    assert r.status_code == 200


async def test_health_redis(client: AsyncClient) -> None:
    r = await client.get("/health/redis")
    assert r.status_code == 200


async def test_register_login_me_refresh_logout(client: AsyncClient) -> None:
    r = await client.post(
        "/api/auth/register",
        json={"email": "alice@example.com", "password": "minha-senha-1", "name": "Alice"},
    )
    assert r.status_code == 201, r.text

    r = await client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "minha-senha-1"},
    )
    assert r.status_code == 200
    tokens = r.json()
    access = tokens["access_token"]
    refresh = tokens["refresh_token"]

    r = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200
    assert r.json()["email"] == "alice@example.com"

    r = await client.post("/api/auth/refresh", json={"refresh_token": refresh})
    assert r.status_code == 200
    new = r.json()
    assert new["access_token"] != access
    assert new["refresh_token"] != refresh

    # rotacao: antigo nao funciona mais
    r = await client.post("/api/auth/refresh", json={"refresh_token": refresh})
    assert r.status_code == 401

    r = await client.post("/api/auth/logout", json={"refresh_token": new["refresh_token"]})
    assert r.status_code == 204
