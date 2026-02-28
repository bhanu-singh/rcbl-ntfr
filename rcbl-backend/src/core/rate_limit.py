"""Per-route rate limiting via slowapi.

Usage on a route:
    @router.post("/login")
    @limiter.limit("5/minute")
    async def login(request: Request, ...): ...

The limiter uses Redis as the primary storage backend. When Redis is unavailable
(e.g. tests, dev without Redis), it automatically falls back to in-memory storage
via `in_memory_fallback_enabled=True`. This ensures `request.state.view_rate_limit`
is always set by the decorator, preventing AttributeError on header injection.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    # When Redis is down, fall back to in-memory rather than skipping limit checks.
    # This guarantees view_rate_limit is always set (no AttributeError on inject_headers).
    in_memory_fallback_enabled=True,
    swallow_errors=True,
)
