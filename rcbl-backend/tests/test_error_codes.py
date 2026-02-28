"""Tests for error response structures.

These tests verify that all custom error codes return the correct
response structure with error code and detail fields.
"""

import io
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

SMALL_PDF = b"%PDF-1.4 test content"


# ── Error Response Structure Tests ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_error_response_has_code_and_detail(client: AsyncClient) -> None:
    """All errors should have 'error' code and 'detail' fields."""
    response = await client.get(f"/api/invoices/upload/batches/{uuid.uuid4()}")
    assert response.status_code == 401  # No auth
    data = response.json()
    assert "error" in data
    assert "detail" in data


# ── NOT_FOUND Error Tests ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_not_found_error_structure(client: AsyncClient, auth_headers: dict) -> None:
    """NOT_FOUND error should have correct structure."""
    response = await client.get(
        f"/api/invoices/upload/batches/{uuid.uuid4()}",
        headers=auth_headers,
    )
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "NOT_FOUND"
    assert "not found" in data["detail"].lower()
    assert "batch" in data["detail"].lower()


# ── UNAUTHORIZED Error Tests ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_unauthorized_error_structure(client: AsyncClient) -> None:
    """UNAUTHORIZED error should have correct structure."""
    response = await client.get("/api/auth/me")
    assert response.status_code == 401
    data = response.json()
    assert data["error"] == "UNAUTHORIZED"
    assert "detail" in data


# ── CONFLICT Error Tests ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_conflict_error_structure(client: AsyncClient) -> None:
    """CONFLICT error for duplicate email should have correct structure."""
    payload = {
        "company_name": "Test Co",
        "company_email": "test@co.com",
        "user_name": "Test User",
        "user_email": "test@co.com",
        "password": "password123",
        "timezone": "UTC",
    }
    await client.post("/api/auth/register", json=payload)
    
    response = await client.post("/api/auth/register", json=payload)
    assert response.status_code == 409
    data = response.json()
    assert data["error"] == "CONFLICT"
    assert "already registered" in data["detail"].lower()


# ── FILE_VALIDATION_ERROR Tests ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_file_validation_error_empty_file(client: AsyncClient, auth_headers: dict) -> None:
    """Empty file should return FILE_VALIDATION_ERROR with correct structure."""
    response = await client.post(
        "/api/invoices/upload",
        headers=auth_headers,
        files={"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "FILE_VALIDATION_ERROR"
    assert "empty" in data["detail"].lower()


@pytest.mark.asyncio
async def test_file_validation_error_too_large(client: AsyncClient, auth_headers: dict) -> None:
    """File too large should return FILE_VALIDATION_ERROR."""
    large_file = b"x" * (21 * 1024 * 1024)  # 21 MB
    response = await client.post(
        "/api/invoices/upload",
        headers=auth_headers,
        files={"file": ("large.pdf", io.BytesIO(large_file), "application/pdf")},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "FILE_VALIDATION_ERROR"
    assert "exceeds" in data["detail"].lower()


@pytest.mark.asyncio
async def test_file_validation_error_unsupported_type(client: AsyncClient, auth_headers: dict) -> None:
    """Unsupported content type should return FILE_VALIDATION_ERROR."""
    response = await client.post(
        "/api/invoices/upload",
        headers=auth_headers,
        files={"file": ("doc.txt", io.BytesIO(b"text"), "text/plain")},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "FILE_VALIDATION_ERROR"
    assert "unsupported" in data["detail"].lower()


# ── INVALID_ITEM_STATUS Error Tests ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_invalid_item_status_error_structure(
    client: AsyncClient, auth_headers: dict, db_session
) -> None:
    """INVALID_ITEM_STATUS error should have correct structure."""
    from sqlalchemy import select
    from src.modules.invoices.models import UploadItem, ItemStatus

    # Create an item
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        upload_response = await client.post(
            "/api/invoices/upload",
            headers=auth_headers,
            files={"file": ("invoice.pdf", io.BytesIO(SMALL_PDF), "application/pdf")},
        )
    item_id = upload_response.json()["item_id"]

    # Set status to processing (invalid for accept)
    result = await db_session.execute(
        select(UploadItem).where(UploadItem.id == uuid.UUID(item_id))
    )
    item = result.scalar_one()
    item.status = ItemStatus.processing
    await db_session.commit()

    response = await client.patch(
        f"/api/invoices/upload/items/{item_id}/accept",
        headers=auth_headers,
        json={
            "customer_id": str(uuid.uuid4()),
            "invoice_date": "2024-06-01",
            "due_date": "2024-06-30",
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "INVALID_ITEM_STATUS"
    assert "status" in data["detail"].lower()


# ── DATE_VALIDATION_ERROR Tests ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_date_validation_error_structure(client: AsyncClient, auth_headers: dict) -> None:
    """DATE_VALIDATION_ERROR should have correct structure when due_date < invoice_date."""
    response = await client.patch(
        f"/api/invoices/upload/items/{uuid.uuid4()}/accept",
        headers=auth_headers,
        json={
            "customer_id": str(uuid.uuid4()),
            "invoice_date": "2024-06-01",
            "due_date": "2024-05-01",  # Before invoice_date
        },
    )
    # This validation happens at schema level, so it's VALIDATION_ERROR
    assert response.status_code == 422
    data = response.json()
    # Schema validation returns VALIDATION_ERROR
    assert data["error"] in ("VALIDATION_ERROR", "DATE_VALIDATION_ERROR")


# ── VALIDATION_ERROR Tests (Pydantic) ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_pydantic_validation_error_structure(client: AsyncClient) -> None:
    """Pydantic validation errors should have VALIDATION_ERROR code."""
    response = await client.post(
        "/api/auth/register",
        json={
            "company_name": "Test",
            "company_email": "not-an-email",  # Invalid email
            "user_name": "Test",
            "user_email": "test@test.com",
            "password": "short",  # Too short
            "timezone": "UTC",
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "VALIDATION_ERROR"
    assert isinstance(data["detail"], list)


# ── Error Code Consistency Tests ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_all_4xx_errors_have_consistent_structure(client: AsyncClient) -> None:
    """All 4xx errors should have 'error' and 'detail' fields."""
    # Test various endpoints that should return 4xx without auth
    endpoints_401 = [
        ("GET", "/api/auth/me"),
        ("GET", "/api/invoices/upload/batches"),
    ]
    
    for method, endpoint in endpoints_401:
        if method == "GET":
            response = await client.get(endpoint)
        else:
            response = await client.post(endpoint, json={})
        
        assert response.status_code == 401, f"{method} {endpoint} should be 401"
        data = response.json()
        assert "error" in data, f"{method} {endpoint} missing 'error' field"
        assert "detail" in data, f"{method} {endpoint} missing 'detail' field"
