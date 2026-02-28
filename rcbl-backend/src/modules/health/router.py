from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.deps import get_db

router = APIRouter(tags=["health"])
logger = structlog.get_logger(__name__)


@router.get("/health", status_code=status.HTTP_200_OK)
async def liveness() -> dict:
    """Liveness probe — returns 200 if the process is running."""
    return {"status": "ok"}


@router.get("/ready")
async def readiness(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    """
    Readiness probe — verifies all external dependencies.
    Returns 200 when healthy, 503 when a dependency is unavailable.
    """
    checks: dict[str, str | dict] = {}
    healthy = True

    # Database check
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = f"error: {exc}"
        healthy = False
        logger.error("health.database_failed", error=str(exc))

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
        logger.error("health.redis_failed", error=str(exc))

    # S3/MinIO check
    try:
        from src.clients import s3_client
        from src.config import settings
        
        # Check if bucket exists and is accessible
        await s3_client.head_bucket(settings.S3_BUCKET)
        checks["s3"] = "ok"
    except Exception as exc:
        checks["s3"] = f"error: {exc}"
        healthy = False
        logger.error("health.s3_failed", error=str(exc))

    # OpenAI API check (lightweight - just check if key is configured)
    # Note: We don't make an actual API call to avoid costs and rate limits
    try:
        from src.config import settings
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sk-placeholder":
            checks["openai"] = "configured"
        else:
            checks["openai"] = "not_configured"
            # Not marking as unhealthy since OCR can gracefully degrade
            logger.warning("health.openai_not_configured")
    except Exception as exc:
        checks["openai"] = f"error: {exc}"
        logger.error("health.openai_check_failed", error=str(exc))

    status_text = "ok" if healthy else "degraded"
    if not healthy:
        logger.warning("health.degraded", checks=checks)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": status_text, "checks": checks},
    )
