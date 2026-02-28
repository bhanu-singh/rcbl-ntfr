"""Tests for health check endpoints."""

from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from httpx import AsyncClient


# ── Liveness Tests ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_liveness(client: AsyncClient) -> None:
    """Liveness probe should always return 200 if process is running."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ── Readiness Tests ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_readiness_database_check(client: AsyncClient) -> None:
    """Readiness probe checks database connectivity."""
    # Patch at source modules since imports happen inside the function
    with (
        patch("src.clients.s3_client.head_bucket", new_callable=AsyncMock) as mock_s3,
        patch("redis.asyncio.Redis") as mock_redis,
    ):
        mock_s3.return_value = True
        mock_redis_instance = AsyncMock()
        mock_redis_instance.ping = AsyncMock(return_value=True)
        mock_redis_instance.__aenter__ = AsyncMock(return_value=mock_redis_instance)
        mock_redis_instance.__aexit__ = AsyncMock(return_value=None)
        mock_redis.from_url.return_value = mock_redis_instance
        
        response = await client.get("/ready")
        
        # Database should be healthy in test environment
        assert response.status_code == 200
        data = response.json()
        assert "checks" in data
        assert data["checks"]["database"] == "ok"
