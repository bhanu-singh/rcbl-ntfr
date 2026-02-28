"""Multi-tenant isolation tests.

These tests verify that a user from one company cannot access resources
from another company. This is critical for security and compliance.
"""

import io
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.invoices.models import ItemStatus, UploadItem

SMALL_PDF = b"%PDF-1.4 test content"


# ── Helper to create another company/user ────────────────────────────────────────


async def _create_other_user(client: AsyncClient) -> dict[str, str]:
    """Register a different user/company and return auth headers."""
    payload = {
        "company_name": "Other Corp",
        "company_email": "other@corp.com",
        "user_name": "Other User",
        "user_email": "other@corp.com",
        "password": "password123",
        "timezone": "UTC",
    }
    response = await client.post("/api/auth/register", json=payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ── Cross-Company Batch Access Tests ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_cannot_access_other_company_batch(client: AsyncClient, auth_headers: dict) -> None:
    """User cannot view batches from another company."""
    # Create a batch as the main user
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        upload_response = await client.post(
            "/api/invoices/upload",
            headers=auth_headers,
            files={"file": ("invoice.pdf", io.BytesIO(SMALL_PDF), "application/pdf")},
        )
    batch_id = upload_response.json()["batch_id"]

    # Create another user
    other_headers = await _create_other_user(client)

    # Try to access the first user's batch
    response = await client.get(
        f"/api/invoices/upload/batches/{batch_id}",
        headers=other_headers,
    )
    assert response.status_code == 404
    assert response.json()["error"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_cannot_list_other_company_batches(client: AsyncClient, auth_headers: dict) -> None:
    """User's batch list should not include other companies' batches."""
    # Create a batch as the main user
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        await client.post(
            "/api/invoices/upload",
            headers=auth_headers,
            files={"file": ("invoice.pdf", io.BytesIO(SMALL_PDF), "application/pdf")},
        )

    # Create another user and check their batch list
    other_headers = await _create_other_user(client)
    response = await client.get("/api/invoices/upload/batches", headers=other_headers)
    assert response.status_code == 200
    batches = response.json()
    assert len(batches) == 0  # Should see no batches from other company


# ── Cross-Company Item Access Tests ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_cannot_access_other_company_item(client: AsyncClient, auth_headers: dict) -> None:
    """User cannot view items from another company."""
    # Create an item as the main user
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        upload_response = await client.post(
            "/api/invoices/upload",
            headers=auth_headers,
            files={"file": ("invoice.pdf", io.BytesIO(SMALL_PDF), "application/pdf")},
        )
    item_id = upload_response.json()["item_id"]

    # Create another user
    other_headers = await _create_other_user(client)

    # Try to access the first user's item
    response = await client.get(
        f"/api/invoices/upload/items/{item_id}",
        headers=other_headers,
    )
    assert response.status_code == 404
    assert response.json()["error"] == "NOT_FOUND"


# ── Cross-Company Item Accept Tests ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_cannot_accept_other_company_item(client: AsyncClient, auth_headers: dict) -> None:
    """User cannot accept items from another company."""
    # Create an item as the main user
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        upload_response = await client.post(
            "/api/invoices/upload",
            headers=auth_headers,
            files={"file": ("invoice.pdf", io.BytesIO(SMALL_PDF), "application/pdf")},
        )
    item_id = upload_response.json()["item_id"]

    # Create another user
    other_headers = await _create_other_user(client)

    # Try to accept the first user's item
    response = await client.patch(
        f"/api/invoices/upload/items/{item_id}/accept",
        headers=other_headers,
        json={
            "customer_id": str(uuid.uuid4()),
            "invoice_date": "2024-06-01",
            "due_date": "2024-06-30",
        },
    )
    assert response.status_code == 404
    assert response.json()["error"] == "NOT_FOUND"


# ── Cross-Company Item Reject Tests ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_cannot_reject_other_company_item(client: AsyncClient, auth_headers: dict) -> None:
    """User cannot reject items from another company."""
    # Create an item as the main user
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        upload_response = await client.post(
            "/api/invoices/upload",
            headers=auth_headers,
            files={"file": ("invoice.pdf", io.BytesIO(SMALL_PDF), "application/pdf")},
        )
    item_id = upload_response.json()["item_id"]

    # Create another user
    other_headers = await _create_other_user(client)

    # Try to reject the first user's item
    response = await client.patch(
        f"/api/invoices/upload/items/{item_id}/reject",
        headers=other_headers,
    )
    assert response.status_code == 404
    assert response.json()["error"] == "NOT_FOUND"


# ── Cross-Company SSE Progress Tests ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_cannot_access_other_company_progress(client: AsyncClient, auth_headers: dict) -> None:
    """User cannot access SSE progress stream for another company's batch."""
    # Create a batch as the main user
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        upload_response = await client.post(
            "/api/invoices/upload",
            headers=auth_headers,
            files={"file": ("invoice.pdf", io.BytesIO(SMALL_PDF), "application/pdf")},
        )
    batch_id = upload_response.json()["batch_id"]

    # Create another user
    other_headers = await _create_other_user(client)

    # Try to access the progress stream
    response = await client.get(
        f"/api/invoices/upload/batches/{batch_id}/progress",
        headers=other_headers,
    )
    # SSE endpoint should return error event
    assert response.status_code == 200
    content = response.text
    assert "error" in content or "not found" in content.lower()
