"""Integration tests for invoice upload endpoints.

S3 is mocked via patch; arq pool is mocked via dependency override in conftest.
"""

import io
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

SMALL_PDF = b"%PDF-1.4 test content"


@pytest.mark.asyncio
async def test_upload_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/api/invoices/upload",
        files={"file": ("invoice.pdf", io.BytesIO(SMALL_PDF), "application/pdf")},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_single_success(client: AsyncClient, auth_headers: dict) -> None:
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        response = await client.post(
            "/api/invoices/upload",
            headers=auth_headers,
            files={"file": ("invoice.pdf", io.BytesIO(SMALL_PDF), "application/pdf")},
        )

    assert response.status_code == 202
    data = response.json()
    assert "batch_id" in data
    assert "item_id" in data
    assert data["status"] == "queued"


@pytest.mark.asyncio
async def test_upload_bulk_success(client: AsyncClient, auth_headers: dict) -> None:
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        response = await client.post(
            "/api/invoices/upload/bulk",
            headers=auth_headers,
            files=[
                ("files", ("inv1.pdf", io.BytesIO(SMALL_PDF), "application/pdf")),
                ("files", ("inv2.pdf", io.BytesIO(SMALL_PDF), "application/pdf")),
            ],
        )

    assert response.status_code == 202
    data = response.json()
    assert data["total_files"] == 2
    assert len(data["items"]) == 2
    # Each item now has a typed shape (BulkUploadItemSummary)
    assert all({"item_id", "file_name", "status"} <= set(item) for item in data["items"])


@pytest.mark.asyncio
async def test_upload_empty_file(client: AsyncClient, auth_headers: dict) -> None:
    response = await client.post(
        "/api/invoices/upload",
        headers=auth_headers,
        files={"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_batches_empty(client: AsyncClient, auth_headers: dict) -> None:
    response = await client.get("/api/invoices/upload/batches", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_batch_not_found(client: AsyncClient, auth_headers: dict) -> None:
    response = await client.get(
        f"/api/invoices/upload/batches/{uuid.uuid4()}", headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_item_not_found(client: AsyncClient, auth_headers: dict) -> None:
    response = await client.get(
        f"/api/invoices/upload/items/{uuid.uuid4()}", headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_accept_item_validates_due_date(client: AsyncClient, auth_headers: dict) -> None:
    """AcceptItemRequest must reject due_date < invoice_date at the schema level."""
    response = await client.patch(
        f"/api/invoices/upload/items/{uuid.uuid4()}/accept",
        headers=auth_headers,
        json={
            "customer_id": str(uuid.uuid4()),
            "invoice_date": "2024-06-01",
            "due_date": "2024-05-01",  # before invoice_date → 422
        },
    )
    assert response.status_code == 422
