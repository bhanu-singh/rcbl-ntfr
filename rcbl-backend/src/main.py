"""FastAPI application factory.

Middleware order (outermost → innermost):
  1. CORSMiddleware      — handles preflight + CORS headers
  2. RequestIDMiddleware — injects X-Request-ID + binds structlog context
  3. slowapi state       — rate limiter (registered via app.state)

Exception handlers registered for: AppError, RequestValidationError, HTTPException.
"""

import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.config import settings
from src.core.exceptions import (
    AppError,
    app_error_handler,
    http_exception_handler,
    validation_error_handler,
)
from src.core.observability import configure_logging, configure_tracing
from src.core.rate_limit import limiter
from src.db.session import engine

configure_logging()
logger = structlog.get_logger(__name__)


def _rate_limit_exceeded_handler_with_logging(request: Request, exc: RateLimitExceeded):
    """Rate limit handler that logs before delegating to slowapi's default handler."""
    logger.warning(
        "rate_limit.exceeded",
        path=str(request.url.path),
        method=request.method,
        client_ip=request.client.host if request.client else None,
        detail=str(exc.detail),
    )
    return _rate_limit_exceeded_handler(request, exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: configure tracing, create shared arq pool, ensure S3 bucket. Shutdown: cleanup."""
    logger.info("app.starting", environment=settings.ENVIRONMENT)

    configure_tracing(app=app, engine=engine)

    # ── Shared arq Redis pool (one pool for the lifetime of the process) ────────
    from arq import create_pool
    from arq.connections import RedisSettings

    app.state.arq_pool = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
    logger.info("arq.pool_created")

    if settings.ENVIRONMENT == "development":
        try:
            from src.clients.s3_client import ensure_bucket_exists
            await ensure_bucket_exists()
        except Exception as exc:
            logger.warning("startup.s3_bucket_check_failed", error=str(exc))

    logger.info("app.ready")
    yield

    await app.state.arq_pool.aclose()
    await engine.dispose()
    logger.info("app.shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title="RCBL Backend",
        description="Receivables management — invoice upload + OCR",
        version="0.1.0",
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan,
    )

    # ── Rate limiter ────────────────────────────────────────────────────────────
    # The @limiter.limit() decorator enforces limits per-route by raising RateLimitExceeded.
    # SlowAPIMiddleware is intentionally omitted: this version has a bug where it accesses
    # request.state.view_rate_limit unconditionally even when Redis is unavailable, which
    # causes AttributeError on every request. The decorator alone is sufficient for enforcement;
    # response header injection (X-RateLimit-*) is a nice-to-have, not a requirement.
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler_with_logging)

    # ── Middleware stack (registered bottom-up, executed top-down) ─────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Request ID + structured log context ────────────────────────────────────
    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id, path=str(request.url.path))
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    # ── Global exception handlers ───────────────────────────────────────────────
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
    from starlette.exceptions import HTTPException as StarletteHTTPException
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]

    # ── Prometheus metrics ──────────────────────────────────────────────────────
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator().instrument(app).expose(app)

    # ── Routers ─────────────────────────────────────────────────────────────────
    from src.modules.auth.router import router as auth_router
    from src.modules.health.router import router as health_router
    from src.modules.invoices.router import router as invoices_router

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(invoices_router)

    return app


app = create_app()
