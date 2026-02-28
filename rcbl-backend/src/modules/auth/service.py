"""Business logic for auth module."""

import uuid

import structlog
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.core.exceptions import ConflictError, UnauthorizedError
from src.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from src.modules.auth import repository
from src.modules.auth.models import Company, User
from src.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse

logger = structlog.get_logger(__name__)


async def register(db: AsyncSession, payload: RegisterRequest) -> tuple[User, Company, TokenResponse]:
    """Create a new company + first admin user. Returns user, company, and token pair."""
    # Ensure email is unique
    if await repository.get_user_by_email(db, payload.user_email):
        raise ConflictError(f"Email '{payload.user_email}' is already registered")

    # Generate unique slug
    base_slug = slugify(payload.company_name, max_length=95)
    slug = base_slug
    counter = 1
    while await repository.get_company_by_slug(db, slug):
        slug = f"{base_slug}-{counter}"
        counter += 1

    company = await repository.create_company(
        db,
        id=uuid.uuid4(),
        name=payload.company_name,
        slug=slug,
        email=payload.company_email,
    )

    user = await repository.create_user(
        db,
        id=uuid.uuid4(),
        company_id=company.id,
        email=payload.user_email,
        password_hash=await hash_password(payload.password),
        name=payload.user_name,
        timezone=payload.timezone,
    )

    access_token, _ = create_access_token(str(user.id), str(company.id))
    token_response = TokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    logger.info("auth.registered", user_id=str(user.id), company_id=str(company.id))
    return user, company, token_response


async def login(db: AsyncSession, payload: LoginRequest) -> tuple[User, TokenResponse, str]:
    """
    Authenticate user. Returns (user, access_token_response, refresh_token).
    Raises UnauthorizedError on bad credentials.
    """
    user = await repository.get_user_by_email(db, payload.email)
    if not user or not await verify_password(payload.password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")

    await repository.update_last_login(db, user)

    access_token, _ = create_access_token(str(user.id), str(user.company_id))
    refresh_token, _ = create_refresh_token(str(user.id), str(user.company_id))

    token_response = TokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    logger.info("auth.login", user_id=str(user.id))
    return user, token_response, refresh_token


async def refresh_access_token(refresh_token: str) -> TokenResponse:
    """Validate refresh token and issue a new access token."""
    from src.core.security import REFRESH_TOKEN_TYPE, decode_token

    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != REFRESH_TOKEN_TYPE:
        raise UnauthorizedError("Invalid or expired refresh token")

    user_id = payload.get("sub")
    company_id = payload.get("company_id")
    if not user_id or not company_id:
        raise UnauthorizedError("Malformed token")

    access_token, _ = create_access_token(user_id, company_id)
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
