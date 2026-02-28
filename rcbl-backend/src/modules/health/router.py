from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.deps import get_db

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def liveness() -> dict:
    """Liveness probe — returns 200 if the process is running."""
    return {"status": "ok"}


@router.get("/ready")
async def readiness(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    """
    Readiness probe — verifies DB connectivity.
    Returns 200 when healthy, 503 when a dependency is unavailable.
    """
    checks: dict[str, str] = {}
    healthy = True

    # Database check
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = f"error: {exc}"
        healthy = False

    # Redis check
    try:
        from redis.asyncio import Redis

        from src.config import settings

        async with Redis.from_url(settings.REDIS_URL, socket_connect_timeout=2) as r:
            await r.ping()
        checks["redis"] = "ok"
    except Exception as exc:
        checks["redis"] = f"error: {exc}"
        healthy = False

    return JSONResponse(
        status_code=status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "ok" if healthy else "degraded", "checks": checks},
    )
