import uuid
from datetime import UTC, datetime, timedelta

import anyio
import bcrypt
from jose import JWTError, jwt

from src.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


async def hash_password(plain: str) -> str:
    """Hash a password using bcrypt, offloaded to a thread to avoid blocking the event loop.

    bcrypt is CPU-intensive; calling it directly in an async route blocks all concurrent
    requests for the duration of the hash (typically 100-300 ms).
    """
    encoded = plain.encode("utf-8")
    return await anyio.to_thread.run_sync(
        lambda: bcrypt.hashpw(encoded, bcrypt.gensalt()).decode("utf-8")
    )


async def verify_password(plain: str, hashed: str) -> bool:
    """Verify a bcrypt password hash, offloaded to a thread (same reason as hash_password)."""
    encoded_plain = plain.encode("utf-8")
    encoded_hash = hashed.encode("utf-8")
    return await anyio.to_thread.run_sync(
        lambda: bcrypt.checkpw(encoded_plain, encoded_hash)
    )


def _make_token(
    subject: str,
    company_id: str,
    token_type: str,
    expires_delta: timedelta,
) -> tuple[str, str]:
    """Return (encoded_token, jti)."""
    jti = str(uuid.uuid4())
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "company_id": company_id,
        "type": token_type,
        "jti": jti,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM), jti


def create_access_token(user_id: str, company_id: str) -> tuple[str, str]:
    """Return (access_token, jti)."""
    return _make_token(
        subject=user_id,
        company_id=company_id,
        token_type=ACCESS_TOKEN_TYPE,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: str, company_id: str) -> tuple[str, str]:
    """Return (refresh_token, jti)."""
    return _make_token(
        subject=user_id,
        company_id=company_id,
        token_type=REFRESH_TOKEN_TYPE,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict | None:
    """Decode and verify a JWT. Returns payload dict or None on failure."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
