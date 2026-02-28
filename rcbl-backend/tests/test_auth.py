"""Integration tests for auth endpoints.

Tests use in-memory SQLite (no Postgres, no Redis needed).
These tests verify routes, schemas, and service logic end-to-end.
"""

import pytest
from httpx import AsyncClient

REGISTER_PAYLOAD = {
    "company_name": "Acme Corp",
    "company_email": "hello@acme.com",
    "user_name": "Alice Smith",
    "user_email": "alice@acme.com",
    "password": "securepass123",
    "timezone": "Europe/Berlin",
}


# ── Register Tests ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient) -> None:
    response = await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
    response = await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 409
    assert response.json()["error"] == "CONFLICT"


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient) -> None:
    payload = {**REGISTER_PAYLOAD, "user_email": "bob@acme.com", "password": "short"}
    response = await client.post("/api/auth/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient) -> None:
    payload = {**REGISTER_PAYLOAD, "user_email": "not-an-email"}
    response = await client.post("/api/auth/register", json=payload)
    assert response.status_code == 422


# ── Login Tests ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
    response = await client.post(
        "/api/auth/login",
        json={"email": REGISTER_PAYLOAD["user_email"], "password": REGISTER_PAYLOAD["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient) -> None:
    await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
    response = await client.post(
        "/api/auth/login",
        json={"email": REGISTER_PAYLOAD["user_email"], "password": "wrongpass"},
    )
    assert response.status_code == 401
    assert response.json()["error"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/login",
        json={"email": "nonexistent@example.com", "password": "anypassword"},
    )
    assert response.status_code == 401
    assert response.json()["error"] == "UNAUTHORIZED"


# ── Refresh Token Tests ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_refresh_token_success(client: AsyncClient) -> None:
    """Login and use the refresh_token cookie to get a new access token."""
    await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
    login_response = await client.post(
        "/api/auth/login",
        json={"email": REGISTER_PAYLOAD["user_email"], "password": REGISTER_PAYLOAD["password"]},
    )
    assert login_response.status_code == 200
    
    # Extract refresh_token from cookies
    cookies = login_response.cookies
    refresh_token = cookies.get("refresh_token")
    assert refresh_token is not None
    
    # Use refresh token to get new access token
    response = await client.post(
        "/api/auth/refresh",
        cookies={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_token_missing_cookie(client: AsyncClient) -> None:
    """Refresh without cookie should return 401."""
    response = await client.post("/api/auth/refresh")
    assert response.status_code == 401
    assert response.json()["error"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_refresh_token_invalid(client: AsyncClient) -> None:
    """Refresh with invalid token should return 401."""
    response = await client.post(
        "/api/auth/refresh",
        cookies={"refresh_token": "invalid.token.here"},
    )
    assert response.status_code == 401
    assert response.json()["error"] == "UNAUTHORIZED"


# ── Protected Route Tests ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_me_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_token(client: AsyncClient, auth_headers: dict) -> None:
    response = await client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "company" in data
    assert data["user"]["email"].endswith("@test.com")


@pytest.mark.asyncio
async def test_me_with_invalid_token(client: AsyncClient) -> None:
    response = await client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_expired_token(client: AsyncClient) -> None:
    """Test with a token that has an expired signature."""
    # This is a JWT with expired exp claim
    expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiY29tcGFueV9pZCI6IjEyMzQ1Njc4LTkwMTItMzQ1Ni03ODkwLTEyMzQ1Njc4OTAxMiIsInR5cGUiOiJhY2Nlc3MiLCJqdGkiOiIxMjM0NTY3ODkwIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.4Adcj3UFYzP5ZI9zH7y3E8pV6dU_0K6U6iI3PzVN6Qk"
    response = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401


# ── Logout Tests ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, auth_headers: dict) -> None:
    response = await client.post("/api/auth/logout", headers=auth_headers)
    assert response.status_code == 204
