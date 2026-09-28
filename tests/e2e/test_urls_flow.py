from __future__ import annotations

from httpx import AsyncClient


async def _login(client: AsyncClient, email: str = "u@x.com") -> str:
    await client.post(
        "/api/auth/register",
        json={"email": email, "password": "12345678", "name": "U"},
    )
    r = await client.post("/api/auth/login", json={"email": email, "password": "12345678"})
    return str(r.json()["access_token"])


async def test_criar_e_listar_url(client: AsyncClient) -> None:
    token = await _login(client)
    headers = {"Authorization": f"Bearer {token}"}

    r = await client.post("/api/urls", headers=headers, json={"target": "https://example.com/a/b"})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["target"] == "https://example.com/a/b"
    assert len(body["slug"]) >= 3
    assert body["short_url"].endswith(body["slug"])
    assert body["click_count"] == 0
    assert body["is_password_protected"] is False

    r = await client.get("/api/urls", headers=headers)
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1


async def test_slug_customizado(client: AsyncClient) -> None:
    token = await _login(client, "cs@x.com")
    headers = {"Authorization": f"Bearer {token}"}

    r = await client.post(
        "/api/urls",
        headers=headers,
        json={"target": "https://example.com", "custom_slug": "meu-link"},
    )
    assert r.status_code == 201
    assert r.json()["slug"] == "meu-link"

    # mesmo slug -> 409
    r = await client.post(
        "/api/urls",
        headers=headers,
        json={"target": "https://outra.com", "custom_slug": "meu-link"},
    )
    assert r.status_code == 409


async def test_redirect_basico(client: AsyncClient) -> None:
    token = await _login(client, "rd@x.com")
    headers = {"Authorization": f"Bearer {token}"}
    r = await client.post(
        "/api/urls",
        headers=headers,
        json={"target": "https://example.com/destino", "custom_slug": "abc-go"},
    )
    assert r.status_code == 201

    # primeiro redirect (cache miss)
    r = await client.get("/abc-go", follow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] == "https://example.com/destino"

    # segundo redirect (cache hit)
    r = await client.get("/abc-go", follow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] == "https://example.com/destino"


async def test_redirect_slug_inexistente(client: AsyncClient) -> None:
    r = await client.get("/nada-aqui", follow_redirects=False)
    assert r.status_code == 404


async def test_url_com_senha(client: AsyncClient) -> None:
    token = await _login(client, "pwd@x.com")
    headers = {"Authorization": f"Bearer {token}"}
    r = await client.post(
        "/api/urls",
        headers=headers,
        json={
            "target": "https://example.com/secret",
            "custom_slug": "lock-1",
            "password": "1234",
        },
    )
    assert r.status_code == 201

    # sem senha
    r = await client.get("/lock-1", follow_redirects=False)
    assert r.status_code == 401

    # senha errada
    r = await client.get("/lock-1?password=errada", follow_redirects=False)
    assert r.status_code == 401

    # senha certa
    r = await client.get("/lock-1?password=1234", follow_redirects=False)
    assert r.status_code == 302


async def test_max_clicks_e_410_apos(client: AsyncClient) -> None:
    token = await _login(client, "mc@x.com")
    headers = {"Authorization": f"Bearer {token}"}
    r = await client.post(
        "/api/urls",
        headers=headers,
        json={
            "target": "https://example.com",
            "custom_slug": "mc-1",
            "max_clicks": 1,
        },
    )
    assert r.status_code == 201

    r = await client.get("/mc-1", follow_redirects=False)
    assert r.status_code == 302
    r = await client.get("/mc-1", follow_redirects=False)
    assert r.status_code == 410
    assert r.json()["error"] == "url_max_clicks"


async def test_delete_url(client: AsyncClient) -> None:
    token = await _login(client, "del@x.com")
    headers = {"Authorization": f"Bearer {token}"}
    r = await client.post(
        "/api/urls",
        headers=headers,
        json={"target": "https://example.com", "custom_slug": "to-del"},
    )
    url_id = r.json()["id"]
    # popula cache
    await client.get("/to-del", follow_redirects=False)

    r = await client.delete(f"/api/urls/{url_id}", headers=headers)
    assert r.status_code == 204

    r = await client.get("/to-del", follow_redirects=False)
    assert r.status_code == 404


async def test_delete_de_outro_usuario_eh_403(client: AsyncClient) -> None:
    t1 = await _login(client, "a1@x.com")
    r = await client.post(
        "/api/urls",
        headers={"Authorization": f"Bearer {t1}"},
        json={"target": "https://example.com", "custom_slug": "alheio"},
    )
    url_id = r.json()["id"]

    t2 = await _login(client, "a2@x.com")
    r = await client.delete(f"/api/urls/{url_id}", headers={"Authorization": f"Bearer {t2}"})
    assert r.status_code == 403


async def test_endpoints_protegidos_sem_token(client: AsyncClient) -> None:
    r = await client.get("/api/urls")
    assert r.status_code == 401
    r = await client.post("/api/urls", json={"target": "https://x.com"})
    assert r.status_code == 401
