from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(HTTPException):
    """Base application error — maps directly to an HTTP status code."""

    def __init__(self, status_code: int, detail: str, code: str | None = None) -> None:
        super().__init__(status_code=status_code, detail=detail)
        self.code = code or f"E{status_code}"


class NotFoundError(AppError):
    def __init__(self, resource: str, resource_id: str | None = None) -> None:
        msg = f"{resource} not found" if not resource_id else f"{resource} '{resource_id}' not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=msg, code="NOT_FOUND")


class ConflictError(AppError):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail, code="CONFLICT")


class UnauthorizedError(AppError):
    def __init__(self, detail: str = "Authentication required") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            code="UNAUTHORIZED",
        )


class ForbiddenError(AppError):
    def __init__(self, detail: str = "Access denied") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail, code="FORBIDDEN")


class UnprocessableError(AppError):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            code="UNPROCESSABLE",
        )


# ── Global exception handlers ─────────────────────────────────────────────────

async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.code, "detail": exc.detail},
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # Pydantic v2 may include non-JSON-serializable objects in error ctx
    # (e.g. the original ValueError from a model_validator). Stringify them.
    serializable_errors = []
    for error in exc.errors():
        error_copy = dict(error)
        if "ctx" in error_copy and isinstance(error_copy["ctx"], dict):
            error_copy["ctx"] = {k: str(v) for k, v in error_copy["ctx"].items()}
        error_copy.pop("url", None)  # remove verbose pydantic doc URLs
        serializable_errors.append(error_copy)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "VALIDATION_ERROR", "detail": serializable_errors},
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": f"HTTP_{exc.status_code}", "detail": exc.detail},
    )
