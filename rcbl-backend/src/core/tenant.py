"""Tenant context propagation via Python contextvars.

The current company_id is stored in a ContextVar so it is
available throughout the request lifecycle (log binding,
RLS injection, etc.) without threading through every function call.
"""

from contextvars import ContextVar
from uuid import UUID

_current_company_id: ContextVar[UUID | None] = ContextVar(
    "current_company_id", default=None
)


def set_company_id(company_id: UUID) -> None:
    _current_company_id.set(company_id)


def get_company_id() -> UUID | None:
    return _current_company_id.get()


def require_company_id() -> UUID:
    cid = _current_company_id.get()
    if cid is None:
        raise RuntimeError("Company context not set — call set_company_id() first")
    return cid
