"""Integration tests for invoice upload endpoints.

S3 is mocked via patch; arq pool is mocked via dependency override in conftest.
"""

import io
import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.invoices.models import ItemStatus, UploadBatch, UploadItem

SMALL_PDF = b"%PDF-1.4 test content"
LARGE_FILE = b"x" * (21 * 1024 * 1024)  # 21 MB - exceeds limit


# ── Auth Required Tests ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_upload_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/api/invoices/upload",
        files={"file": ("invoice.pdf", io.BytesIO(SMALL_PDF), "application/pdf")},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_batches_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/invoices/upload/batches")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_batch_requires_auth(client: AsyncClient) -> None:
    response = await client.get(f"/api/invoices/upload/batches/{uuid.uuid4()}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_item_requires_auth(client: AsyncClient) -> None:
    response = await client.get(f"/api/invoices/upload/items/{uuid.uuid4()}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_accept_item_requires_auth(client: AsyncClient) -> None:
    response = await client.patch(
        f"/api/invoices/upload/items/{uuid.uuid4()}/accept",
        json={"customer_id": str(uuid.uuid4())},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_reject_item_requires_auth(client: AsyncClient) -> None:
    response = await client.patch(f"/api/invoices/upload/items/{uuid.uuid4()}/reject")
    assert response.status_code == 401


# ── Upload Single Tests ─────────────────────────────────────────────────────────


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
async def test_upload_single_pdf(client: AsyncClient, auth_headers: dict) -> None:
    """Test PDF upload works."""
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        response = await client.post(
            "/api/invoices/upload",
            headers=auth_headers,
            files={"file": ("invoice.pdf", io.BytesIO(SMALL_PDF), "application/pdf")},
        )
    assert response.status_code == 202


@pytest.mark.asyncio
async def test_upload_single_jpeg(client: AsyncClient, auth_headers: dict) -> None:
    """Test JPEG upload works."""
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        response = await client.post(
            "/api/invoices/upload",
            headers=auth_headers,
            files={"file": ("invoice.jpg", io.BytesIO(b"fake jpeg"), "image/jpeg")},
        )
    assert response.status_code == 202


@pytest.mark.asyncio
async def test_upload_single_png(client: AsyncClient, auth_headers: dict) -> None:
    """Test PNG upload works."""
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        response = await client.post(
            "/api/invoices/upload",
            headers=auth_headers,
            files={"file": ("invoice.png", io.BytesIO(b"fake png"), "image/png")},
        )
    assert response.status_code == 202


@pytest.mark.asyncio
async def test_upload_single_tiff(client: AsyncClient, auth_headers: dict) -> None:
    """Test TIFF upload works."""
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        response = await client.post(
            "/api/invoices/upload",
            headers=auth_headers,
            files={"file": ("invoice.tiff", io.BytesIO(b"fake tiff"), "image/tiff")},
        )
    assert response.status_code == 202


@pytest.mark.asyncio
async def test_upload_empty_file(client: AsyncClient, auth_headers: dict) -> None:
    """Empty file should return FILE_VALIDATION_ERROR."""
    response = await client.post(
        "/api/invoices/upload",
        headers=auth_headers,
        files={"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "FILE_VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_upload_file_too_large(client: AsyncClient, auth_headers: dict) -> None:
    """File exceeding 20MB should return FILE_VALIDATION_ERROR."""
    response = await client.post(
        "/api/invoices/upload",
        headers=auth_headers,
        files={"file": ("large.pdf", io.BytesIO(LARGE_FILE), "application/pdf")},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "FILE_VALIDATION_ERROR"
    assert "exceeds" in data["detail"].lower()


@pytest.mark.asyncio
async def test_upload_unsupported_content_type(client: AsyncClient, auth_headers: dict) -> None:
    """Unsupported content type should return FILE_VALIDATION_ERROR."""
    response = await client.post(
        "/api/invoices/upload",
        headers=auth_headers,
        files={"file": ("document.txt", io.BytesIO(b"text content"), "text/plain")},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "FILE_VALIDATION_ERROR"
    assert "unsupported" in data["detail"].lower()


# ── Upload Bulk Tests ───────────────────────────────────────────────────────────


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
async def test_upload_bulk_multiple_files(client: AsyncClient, auth_headers: dict) -> None:
    """Test bulk upload with 5 files."""
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        response = await client.post(
            "/api/invoices/upload/bulk",
            headers=auth_headers,
            files=[
                ("files", (f"inv{i}.pdf", io.BytesIO(SMALL_PDF), "application/pdf"))
                for i in range(5)
            ],
        )

    assert response.status_code == 202
    data = response.json()
    assert data["total_files"] == 5
    assert len(data["items"]) == 5


# ── List Batches Tests ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_batches_empty(client: AsyncClient, auth_headers: dict) -> None:
    response = await client.get("/api/invoices/upload/batches", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_list_batches_with_data(client: AsyncClient, auth_headers: dict) -> None:
    """List batches should return created batches."""
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        # Create two batches
        await client.post(
            "/api/invoices/upload",
            headers=auth_headers,
            files={"file": ("invoice1.pdf", io.BytesIO(SMALL_PDF), "application/pdf")},
        )
        await client.post(
            "/api/invoices/upload",
            headers=auth_headers,
            files={"file": ("invoice2.pdf", io.BytesIO(SMALL_PDF), "application/pdf")},
        )

    response = await client.get("/api/invoices/upload/batches", headers=auth_headers)
    assert response.status_code == 200
    batches = response.json()
    assert len(batches) == 2


@pytest.mark.asyncio
async def test_list_batches_pagination(client: AsyncClient, auth_headers: dict) -> None:
    """Test pagination parameters work."""
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        # Create 5 batches
        for i in range(5):
            await client.post(
                "/api/invoices/upload",
                headers=auth_headers,
                files={"file": (f"invoice{i}.pdf", io.BytesIO(SMALL_PDF), "application/pdf")},
            )

    # Get first 2
    response = await client.get("/api/invoices/upload/batches?offset=0&limit=2", headers=auth_headers)
    assert response.status_code == 200
    batches = response.json()
    assert len(batches) == 2

    # Get next 2
    response = await client.get("/api/invoices/upload/batches?offset=2&limit=2", headers=auth_headers)
    assert response.status_code == 200
    batches = response.json()
    assert len(batches) == 2

    # Get last 1
    response = await client.get("/api/invoices/upload/batches?offset=4&limit=2", headers=auth_headers)
    assert response.status_code == 200
    batches = response.json()
    assert len(batches) == 1


# ── Get Batch Tests ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_batch_not_found(client: AsyncClient, auth_headers: dict) -> None:
    response = await client.get(
        f"/api/invoices/upload/batches/{uuid.uuid4()}", headers=auth_headers
    )
    assert response.status_code == 404
    assert response.json()["error"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_get_batch_success(client: AsyncClient, auth_headers: dict) -> None:
    """Get batch detail with items."""
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        upload_response = await client.post(
            "/api/invoices/upload",
            headers=auth_headers,
            files={"file": ("invoice.pdf", io.BytesIO(SMALL_PDF), "application/pdf")},
        )
    batch_id = upload_response.json()["batch_id"]

    response = await client.get(f"/api/invoices/upload/batches/{batch_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == batch_id
    assert "items" in data
    assert len(data["items"]) == 1


# ── Get Item Tests ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_item_not_found(client: AsyncClient, auth_headers: dict) -> None:
    response = await client.get(
        f"/api/invoices/upload/items/{uuid.uuid4()}", headers=auth_headers
    )
    assert response.status_code == 404
    assert response.json()["error"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_get_item_success(client: AsyncClient, auth_headers: dict) -> None:
    """Get item detail with OCR data."""
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        upload_response = await client.post(
            "/api/invoices/upload",
            headers=auth_headers,
            files={"file": ("invoice.pdf", io.BytesIO(SMALL_PDF), "application/pdf")},
        )
    item_id = upload_response.json()["item_id"]

    response = await client.get(f"/api/invoices/upload/items/{item_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["status"] == "queued"
    assert data["file_name"] == "invoice.pdf"


# ── Accept Item Tests ────────────────────────────────────────────────────────────


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


@pytest.mark.asyncio
async def test_accept_item_not_found(client: AsyncClient, auth_headers: dict) -> None:
    """Accepting non-existent item should return 404."""
    response = await client.patch(
        f"/api/invoices/upload/items/{uuid.uuid4()}/accept",
        headers=auth_headers,
        json={
            "customer_id": str(uuid.uuid4()),
            "invoice_date": "2024-06-01",
            "due_date": "2024-06-30",
        },
    )
    assert response.status_code == 404
    assert response.json()["error"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_accept_item_invalid_status(
    client: AsyncClient, auth_headers: dict, db_session: AsyncSession
) -> None:
    """Accepting an item with wrong status should return INVALID_ITEM_STATUS."""
    # Create an item
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        upload_response = await client.post(
            "/api/invoices/upload",
            headers=auth_headers,
            files={"file": ("invoice.pdf", io.BytesIO(SMALL_PDF), "application/pdf")},
        )
    item_id = upload_response.json()["item_id"]

    # Manually set status to 'processing' (not ready/review_pending)
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


@pytest.mark.asyncio
async def test_accept_item_success_with_ocr_data(
    client: AsyncClient, auth_headers: dict, db_session: AsyncSession
) -> None:
    """Accept item with OCR data should create invoice."""
    # Create an item
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        upload_response = await client.post(
            "/api/invoices/upload",
            headers=auth_headers,
            files={"file": ("invoice.pdf", io.BytesIO(SMALL_PDF), "application/pdf")},
        )
    item_id = upload_response.json()["item_id"]

    # Simulate OCR processing with complete data
    result = await db_session.execute(
        select(UploadItem).where(UploadItem.id == uuid.UUID(item_id))
    )
    item = result.scalar_one()
    item.status = ItemStatus.ready
    item.ocr_extracted_data = {
        "invoice_number": "INV-001",
        "amount": "1500.00",
        "currency": "USD",
        "invoice_date": "2024-06-01",
        "due_date": "2024-06-30",
        "vendor_name": "Acme Corp",
    }
    item.ocr_confidence_score = Decimal("0.95")
    await db_session.commit()

    # Create a customer first using the ORM model
    from src.modules.invoices.models import Customer
    
    # Get company_id from the upload item
    result = await db_session.execute(
        select(UploadItem).where(UploadItem.id == uuid.UUID(item_id))
    )
    item = result.scalar_one()
    company_id = item.company_id
    
    customer = Customer(
        id=uuid.uuid4(),
        company_id=company_id,
        name="Test Customer",
    )
    db_session.add(customer)
    await db_session.commit()

    response = await client.patch(
        f"/api/invoices/upload/items/{item_id}/accept",
        headers=auth_headers,
        json={"customer_id": str(customer.id)},
    )
    assert response.status_code == 201
    data = response.json()
    assert "invoice_id" in data
    assert "item_id" in data
    assert data["message"] == "Invoice created successfully."


# ── Reject Item Tests ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_reject_item_not_found(client: AsyncClient, auth_headers: dict) -> None:
    """Rejecting non-existent item should return 404."""
    response = await client.patch(
        f"/api/invoices/upload/items/{uuid.uuid4()}/reject",
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert response.json()["error"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_reject_item_success(
    client: AsyncClient, auth_headers: dict, db_session: AsyncSession
) -> None:
    """Reject item should set status to rejected."""
    # Create an item
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        upload_response = await client.post(
            "/api/invoices/upload",
            headers=auth_headers,
            files={"file": ("invoice.pdf", io.BytesIO(SMALL_PDF), "application/pdf")},
        )
    item_id = upload_response.json()["item_id"]

    # Set status to ready
    result = await db_session.execute(
        select(UploadItem).where(UploadItem.id == uuid.UUID(item_id))
    )
    item = result.scalar_one()
    item.status = ItemStatus.ready
    await db_session.commit()

    response = await client.patch(
        f"/api/invoices/upload/items/{item_id}/reject",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"


@pytest.mark.asyncio
async def test_reject_item_invalid_status(
    client: AsyncClient, auth_headers: dict, db_session: AsyncSession
) -> None:
    """Rejecting an already accepted item should return INVALID_ITEM_STATUS."""
    # Create an item
    with patch("src.modules.invoices.service.s3_client.upload_file", new_callable=AsyncMock):
        upload_response = await client.post(
            "/api/invoices/upload",
            headers=auth_headers,
            files={"file": ("invoice.pdf", io.BytesIO(SMALL_PDF), "application/pdf")},
        )
    item_id = upload_response.json()["item_id"]

    # Set status to accepted
    result = await db_session.execute(
        select(UploadItem).where(UploadItem.id == uuid.UUID(item_id))
    )
    item = result.scalar_one()
    item.status = ItemStatus.accepted
    await db_session.commit()

    response = await client.patch(
        f"/api/invoices/upload/items/{item_id}/reject",
        headers=auth_headers,
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "INVALID_ITEM_STATUS"
