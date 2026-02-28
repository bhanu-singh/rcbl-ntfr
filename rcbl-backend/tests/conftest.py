"""Pytest fixtures for integration tests.

Uses httpx.AsyncClient with ASGITransport to test routes without a live server.
Auth module tests use a real SQLite in-memory DB via aiosqlite (no Postgres needed).
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Ensure all ORM models are registered in Base.metadata before create_all
import src.modules.auth.models
import src.modules.invoices.models  # noqa: F401
from src.core.rate_limit import limiter as _rate_limiter
from src.db.session import Base
from src.main import app

# ── In-memory SQLite for tests ─────────────────────────────────────────────────
# We use aiosqlite for unit/integration tests so no Postgres is needed in CI.
# Note: RLS policies and PostgreSQL-specific types are NOT tested here.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

_test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
_test_session_factory = async_sessionmaker(
    _test_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


@pytest.fixture(scope="session", autouse=True)
def disable_rate_limiting():
    """Disable rate limiting for the entire test session.

    Rate limits are enforced per IP using an in-memory fallback when Redis is absent.
    With rapid-fire test requests from the same host, the limit would be hit after only
    a few tests, causing cascading failures. Production limits (3-5/minute) are
    intentionally low and must not apply during automated tests.
    """
    original = _rate_limiter.enabled
    _rate_limiter.enabled = False
    yield
    _rate_limiter.enabled = original


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables():
    """Create all tables once per test session."""
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    """Yield a test DB session that rolls back after each test."""
    async with _test_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    """
    httpx AsyncClient wired to the FastAPI app.
    Overrides:
      - get_db / get_tenant_db → SQLite in-memory session
      - get_arq_pool → MagicMock with AsyncMock enqueue_job (no Redis needed)
    """
    from src.core.deps import get_arq_pool, get_db, get_tenant_db

    mock_arq_pool = MagicMock()
    mock_arq_pool.enqueue_job = AsyncMock()

    async def override_get_db():
        yield db_session

    async def override_get_tenant_db():
        yield db_session

    def override_get_arq_pool():
        return mock_arq_pool

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_tenant_db] = override_get_tenant_db
    app.dependency_overrides[get_arq_pool] = override_get_arq_pool

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# ── Auth helpers ───────────────────────────────────────────────────────────────

REGISTER_PAYLOAD = {
    "company_name": "Test Company",
    "company_email": "company@test.com",
    "user_name": "Test User",
    "user_email": "user@test.com",
    "password": "password123",
    "timezone": "UTC",
}


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    """Register a test user and return Authorization headers."""
    response = await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 201, f"Registration failed: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
