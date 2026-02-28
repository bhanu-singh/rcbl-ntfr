"""Auth router: register, login, refresh, logout, me."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Cookie, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.core.deps import get_current_user, get_db
from src.core.rate_limit import limiter
from src.modules.auth import service
from src.modules.auth.models import User
from src.modules.auth.schemas import (
    CompanyResponse,
    LoginRequest,
    MeResponse,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

_REFRESH_COOKIE = "refresh_token"
_ACCESS_COOKIE = "access_token"
_COOKIE_OPTS = {
    "httponly": True,
    "samesite": "lax",
    "secure": settings.ENVIRONMENT != "development",
}


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def register(
    request: Request,
    payload: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    _user, _company, token_response = await service.register(db, payload)
    _set_auth_cookies(response, token_response.access_token, "")
    return token_response


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    payload: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    _user, token_response, refresh_token = await service.login(db, payload)
    _set_auth_cookies(response, token_response.access_token, refresh_token)
    return token_response


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> TokenResponse:
    if not refresh_token:
        from src.core.exceptions import UnauthorizedError
        raise UnauthorizedError("Refresh token cookie missing")

    token_response = await service.refresh_access_token(refresh_token)
    response.set_cookie(
        key=_ACCESS_COOKIE,
        value=token_response.access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **_COOKIE_OPTS,
    )
    return token_response


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
) -> None:
    """Clear auth cookies. In production, also blocklist the jti in Redis."""
    response.delete_cookie(_ACCESS_COOKIE)
    response.delete_cookie(_REFRESH_COOKIE)
    logger.info("auth.logout", user_id=str(current_user.id))


@router.get("/me", response_model=MeResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MeResponse:
    from src.modules.auth.repository import get_company_by_id

    company = await get_company_by_id(db, current_user.company_id)
    return MeResponse(
        user=UserResponse.model_validate(current_user),
        company=CompanyResponse.model_validate(company),
    )


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key=_ACCESS_COOKIE,
        value=access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **_COOKIE_OPTS,
    )
    if refresh_token:
        response.set_cookie(
            key=_REFRESH_COOKIE,
            value=refresh_token,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
            **_COOKIE_OPTS,
        )
