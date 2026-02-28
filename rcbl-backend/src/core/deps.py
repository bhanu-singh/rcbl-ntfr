"""FastAPI dependency functions shared across all modules."""

import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

import structlog
from fastapi import Cookie, Depends, Header, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.core.exceptions import ForbiddenError, UnauthorizedError
from src.core.security import ACCESS_TOKEN_TYPE, decode_token
from src.core.tenant import require_company_id, set_company_id
from src.db.session import get_session, set_tenant_context
from src.modules.auth.models import User

logger = structlog.get_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


# ── Database ──────────────────────────────────────────────────────────────────


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a plain (non-tenant-scoped) async DB session."""
    async for session in get_session():
        yield session


# ── arq pool ─────────────────────────────────────────────────────────────────


def get_arq_pool(request: Request):
    """Return the shared arq Redis pool stored on app.state at startup."""
    return request.app.state.arq_pool


# ── Auth + Tenant ─────────────────────────────────────────────────────────────


async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
    access_token: Annotated[str | None, Cookie()] = None,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Resolve the authenticated user from a Bearer token (header) or
    access_token httpOnly cookie. Sets company context ContextVar.
    """
    raw_token = token or access_token
    if not raw_token:
        raise UnauthorizedError("No authentication token provided")

    payload = decode_token(raw_token)
    if payload is None or payload.get("type") != ACCESS_TOKEN_TYPE:
        raise UnauthorizedError("Invalid or expired access token")

    user_id_str: str | None = payload.get("sub")
    company_id_str: str | None = payload.get("company_id")

    if not user_id_str or not company_id_str:
        raise UnauthorizedError("Malformed token payload")

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError as exc:
        raise UnauthorizedError("Invalid user ID in token") from exc

    result = await db.execute(
        select(User).where(
            User.id == user_uuid,
            User.deleted_at.is_(None),
        )
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise UnauthorizedError("User not found")

    set_company_id(uuid.UUID(company_id_str))
    return user


async def get_tenant_db(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[AsyncSession, None]:
    """
    Yield a tenant-scoped session: RLS context variable is set at the
    PostgreSQL transaction level before yielding.
    """
    company_id = require_company_id()
    await set_tenant_context(db, company_id)
    yield db


# ── Cron secret ───────────────────────────────────────────────────────────────


async def verify_cron_secret(
    x_cron_secret: Annotated[str | None, Header()] = None,
) -> None:
    """Protect internal cron endpoints with a shared secret header."""
    cron_secret = getattr(settings, "CRON_SECRET", None)
    if not cron_secret:
        raise ForbiddenError("Cron secret not configured")
    if x_cron_secret != cron_secret:
        raise ForbiddenError("Invalid cron secret")
