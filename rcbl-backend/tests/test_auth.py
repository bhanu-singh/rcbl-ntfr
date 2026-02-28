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


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
    response = await client.post(
        "/api/auth/login",
        json={"email": REGISTER_PAYLOAD["user_email"], "password": REGISTER_PAYLOAD["password"]},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient) -> None:
    await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
    response = await client.post(
        "/api/auth/login",
        json={"email": REGISTER_PAYLOAD["user_email"], "password": "wrongpass"},
    )
    assert response.status_code == 401


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
    assert data["user"]["email"] == "user@test.com"


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, auth_headers: dict) -> None:
    response = await client.post("/api/auth/logout", headers=auth_headers)
    assert response.status_code == 204
