from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import structlog

logger = structlog.get_logger(__name__)


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
    def __init__(self, detail: str, code: str = "CONFLICT") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail, code=code)


class UnauthorizedError(AppError):
    def __init__(self, detail: str = "Authentication required", code: str = "UNAUTHORIZED") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            code=code,
        )


class ForbiddenError(AppError):
    def __init__(self, detail: str = "Access denied", code: str = "FORBIDDEN") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail, code=code)


class UnprocessableError(AppError):
    """Business logic validation error."""
    
    def __init__(
        self, 
        detail: str, 
        code: str = "UNPROCESSABLE",
        fields: list[str] | None = None,
    ) -> None:
        self.fields = fields or []
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            code=code,
        )


# ── Business-Specific Error Codes ────────────────────────────────────────────────

class IncompleteOCRDataError(UnprocessableError):
    """OCR extraction missing required fields."""
    def __init__(self, missing_fields: list[str]) -> None:
        self.fields = missing_fields
        super().__init__(
            detail=f"Cannot create invoice — missing required fields: {', '.join(missing_fields)}. "
                   "Provide them in the request body to override OCR results.",
            code="INCOMPLETE_OCR_DATA",
            fields=missing_fields,
        )


class InvalidItemStatusError(UnprocessableError):
    """Item is not in a valid state for the requested operation."""
    def __init__(self, current_status: str, allowed_statuses: list[str]) -> None:
        super().__init__(
            detail=f"Item status is '{current_status}' — only {', '.join(allowed_statuses)} items can be processed",
            code="INVALID_ITEM_STATUS",
        )


class DateValidationError(UnprocessableError):
    """Date fields fail cross-field validation."""
    def __init__(self, detail: str) -> None:
        super().__init__(detail=detail, code="DATE_VALIDATION_ERROR")


class FileValidationError(UnprocessableError):
    """Uploaded file fails validation."""
    def __init__(self, detail: str) -> None:
        super().__init__(detail=detail, code="FILE_VALIDATION_ERROR")


class DuplicateResourceError(ConflictError):
    """Resource already exists."""
    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(
            detail=f"{resource} '{identifier}' already exists",
            code="DUPLICATE_RESOURCE",
        )


# ── Global exception handlers ─────────────────────────────────────────────────

async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle all AppError exceptions with structured JSON response."""
    # Log business errors at appropriate level
    log_data = {
        "error_code": exc.code,
        "detail": exc.detail,
        "path": str(request.url.path),
        "method": request.method,
    }
    
    # Include fields if present (for IncompleteOCRDataError etc.)
    if hasattr(exc, "fields") and exc.fields:
        log_data["fields"] = exc.fields
    
    if exc.status_code >= 500:
        logger.error("app.error", **log_data)
    elif exc.status_code >= 400:
        logger.info("app.client_error", **log_data)
    
    response_content = {"error": exc.code, "detail": exc.detail}
    if hasattr(exc, "fields") and exc.fields:
        response_content["fields"] = exc.fields
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_content,
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors with structured response."""
    serializable_errors = []
    for error in exc.errors():
        error_copy = dict(error)
        if "ctx" in error_copy and isinstance(error_copy["ctx"], dict):
            error_copy["ctx"] = {k: str(v) for k, v in error_copy["ctx"].items()}
        error_copy.pop("url", None)
        serializable_errors.append(error_copy)
    
    # Log validation errors for debugging
    logger.info(
        "validation.error",
        path=str(request.url.path),
        method=request.method,
        errors=serializable_errors,
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "VALIDATION_ERROR", "detail": serializable_errors},
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": f"HTTP_{exc.status_code}", "detail": exc.detail},
    )
