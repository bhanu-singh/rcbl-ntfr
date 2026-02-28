"""Business logic for invoice upload and OCR module.

Flow:
  1. Client uploads PDF(s) → service stores to S3, creates batch + items, enqueues OCR jobs
  2. Worker processes OCR → updates items (ready | review_pending | failed) + batch counters
  3. Client reviews items → PATCH accept (creates Invoice) or reject
"""

import uuid
from datetime import date
from decimal import Decimal

import structlog
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.clients import s3_client
from src.core.exceptions import NotFoundError, UnprocessableError
from src.modules.invoices import repository
from src.modules.invoices.models import (
    BatchUploadType,
    InvoiceSource,
    InvoiceStatus,
    ItemStatus,
    UploadBatch,
    UploadItem,
)
from src.modules.invoices.schemas import (
    AcceptItemRequest,
    AcceptItemResponse,
    BulkUploadItemSummary,
    BulkUploadResponse,
    SingleUploadResponse,
    UploadItemResponse,
)

logger = structlog.get_logger(__name__)

_ALLOWED_CONTENT_TYPES = {"application/pdf", "image/jpeg", "image/png", "image/tiff"}
_MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


async def upload_single(
    db: AsyncSession,
    company_id: uuid.UUID,
    user_id: uuid.UUID,
    file: UploadFile,
    arq_pool,
) -> SingleUploadResponse:
    """Upload a single PDF, create batch + item, enqueue OCR job."""
    file_bytes = await _read_and_validate_file(file)

    # Store in S3
    key = f"invoices/{company_id}/{uuid.uuid4()}/{file.filename}"
    await s3_client.upload_file(file_bytes, key, content_type=file.content_type or "application/pdf")
    file_hash = s3_client.compute_sha256(file_bytes)

    batch = await repository.create_batch(
        db,
        company_id=company_id,
        created_by=user_id,
        upload_type=BatchUploadType.single,
        total_files=1,
    )

    item = await repository.create_item(
        db,
        batch_id=batch.id,
        company_id=company_id,
        file_name=file.filename or "unnamed.pdf",
        file_url=key,
        file_hash=file_hash,
        file_size_bytes=len(file_bytes),
    )

    await arq_pool.enqueue_job("process_ocr", str(item.id), str(company_id))

    logger.info(
        "invoice.upload_single",
        batch_id=str(batch.id),
        item_id=str(item.id),
        file_name=file.filename,
    )

    return SingleUploadResponse(batch_id=batch.id, item_id=item.id)


async def upload_bulk(
    db: AsyncSession,
    company_id: uuid.UUID,
    user_id: uuid.UUID,
    files: list[UploadFile],
    arq_pool,
) -> BulkUploadResponse:
    """Upload multiple PDFs, create one batch with N items, enqueue N OCR jobs."""
    if not files:
        raise UnprocessableError("At least one file is required")

    batch = await repository.create_batch(
        db,
        company_id=company_id,
        created_by=user_id,
        upload_type=BatchUploadType.bulk,
        total_files=len(files),
    )

    items_summary: list[BulkUploadItemSummary] = []
    for file in files:
        file_bytes = await _read_and_validate_file(file)
        key = f"invoices/{company_id}/{batch.id}/{uuid.uuid4()}/{file.filename}"
        await s3_client.upload_file(
            file_bytes, key, content_type=file.content_type or "application/pdf"
        )
        file_hash = s3_client.compute_sha256(file_bytes)

        item = await repository.create_item(
            db,
            batch_id=batch.id,
            company_id=company_id,
            file_name=file.filename or "unnamed.pdf",
            file_url=key,
            file_hash=file_hash,
            file_size_bytes=len(file_bytes),
        )

        await arq_pool.enqueue_job("process_ocr", str(item.id), str(company_id))
        items_summary.append(
            BulkUploadItemSummary(item_id=item.id, file_name=file.filename or "unnamed.pdf", status="queued")
        )

    logger.info("invoice.upload_bulk", batch_id=str(batch.id), total=len(files))

    return BulkUploadResponse(
        batch_id=batch.id,
        total_files=len(files),
        items=items_summary,
        message=f"{len(files)} files uploaded. OCR processing has been queued.",
    )


async def get_batch(
    db: AsyncSession,
    batch_id: uuid.UUID,
    company_id: uuid.UUID,
    with_items: bool = False,
) -> UploadBatch:
    batch = await repository.get_batch_by_id(db, batch_id, company_id, with_items=with_items)
    if not batch:
        raise NotFoundError("UploadBatch", str(batch_id))
    return batch


async def list_batches(
    db: AsyncSession,
    company_id: uuid.UUID,
    offset: int = 0,
    limit: int = 20,
) -> list[UploadBatch]:
    return await repository.list_batches(db, company_id, offset=offset, limit=limit)


async def get_item(
    db: AsyncSession,
    item_id: uuid.UUID,
    company_id: uuid.UUID,
) -> UploadItem:
    item = await repository.get_item_by_id(db, item_id, company_id)
    if not item:
        raise NotFoundError("UploadItem", str(item_id))
    return item


async def accept_item(
    db: AsyncSession,
    item_id: uuid.UUID,
    company_id: uuid.UUID,
    payload: AcceptItemRequest,
) -> AcceptItemResponse:
    """
    Merge OCR-extracted data with user overrides, validate completeness,
    create an Invoice record, and mark the item as accepted.
    """
    item = await get_item(db, item_id, company_id)

    if item.status not in (ItemStatus.ready.value, ItemStatus.review_pending.value):
        raise UnprocessableError(
            f"Item status is '{item.status}' — only 'ready' or 'review_pending' items can be accepted"
        )

    # Merge: OCR data is the base, user overrides take precedence
    ocr = item.ocr_extracted_data or {}

    invoice_number: str | None = payload.invoice_number or ocr.get("invoice_number")
    raw_amount = payload.amount if payload.amount is not None else ocr.get("amount")
    amount: Decimal | None = Decimal(str(raw_amount)) if raw_amount is not None else None
    currency: str = payload.currency or ocr.get("currency") or "EUR"
    invoice_date: date | None = payload.invoice_date or _parse_date(ocr.get("invoice_date"))
    due_date: date | None = payload.due_date or _parse_date(ocr.get("due_date"))
    payment_terms_days: int = payload.payment_terms_days or 30

    # Validate completeness — all NOT NULL invoice columns must be present
    missing = []
    if not invoice_number:
        missing.append("invoice_number")
    if amount is None:
        missing.append("amount")
    if not invoice_date:
        missing.append("invoice_date")
    if not due_date:
        missing.append("due_date")

    if missing:
        raise UnprocessableError(
            f"Cannot create invoice — missing required fields: {', '.join(missing)}. "
            "Provide them in the request body to override OCR results."
        )

    # Final cross-field check (mirrors DB CONSTRAINT due_after_invoice)
    if due_date < invoice_date:  # type: ignore[operator]
        raise UnprocessableError("due_date must be on or after invoice_date")

    invoice = await repository.create_invoice(
        db,
        company_id=company_id,
        customer_id=payload.customer_id,
        invoice_number=invoice_number,
        amount=amount,
        currency=currency,
        invoice_date=invoice_date,
        due_date=due_date,
        payment_terms_days=payment_terms_days,
        status=InvoiceStatus.pending.value,
        source=InvoiceSource.upload.value,
        ocr_processed=True,
        ocr_confidence_score=item.ocr_confidence_score,
        ocr_extracted_data=ocr,
        upload_item_id=item.id,
        file_url=item.file_url,
    )

    await repository.accept_item(db, item, invoice.id)

    logger.info(
        "invoice.accepted",
        item_id=str(item_id),
        invoice_id=str(invoice.id),
        company_id=str(company_id),
    )

    return AcceptItemResponse(invoice_id=invoice.id, item_id=item.id)


async def reject_item(
    db: AsyncSession,
    item_id: uuid.UUID,
    company_id: uuid.UUID,
) -> UploadItemResponse:
    item = await get_item(db, item_id, company_id)

    if item.status not in (
        ItemStatus.ready.value,
        ItemStatus.review_pending.value,
        ItemStatus.queued.value,
    ):
        raise UnprocessableError(
            f"Item status is '{item.status}' — cannot reject an already accepted/failed item"
        )

    await repository.update_item_status(db, item.id, ItemStatus.rejected)

    item.status = ItemStatus.rejected.value
    return UploadItemResponse.model_validate(item)


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _read_and_validate_file(file: UploadFile) -> bytes:
    content_type = file.content_type or ""
    if content_type and content_type not in _ALLOWED_CONTENT_TYPES:
        raise UnprocessableError(
            f"Unsupported file type '{content_type}'. Allowed: PDF, JPEG, PNG, TIFF"
        )

    file_bytes = await file.read()
    if len(file_bytes) > _MAX_FILE_SIZE_BYTES:
        raise UnprocessableError(
            f"File '{file.filename}' exceeds 20 MB limit ({len(file_bytes)} bytes)"
        )
    if len(file_bytes) == 0:
        raise UnprocessableError(f"File '{file.filename}' is empty")

    return file_bytes


def _parse_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None
