"""Data access layer for invoice upload and OCR module.

All queries filter deleted_at IS NULL (soft deletes from V021).
Optimistic locking version columns are checked in update statements.
"""

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.exceptions import ConflictError
from src.modules.invoices.models import (
    BatchStatus,
    BatchUploadType,
    Invoice,
    ItemStatus,
    UploadBatch,
    UploadItem,
)

# ── UploadBatch ───────────────────────────────────────────────────────────────


async def create_batch(
    db: AsyncSession,
    company_id: uuid.UUID,
    created_by: uuid.UUID,
    upload_type: BatchUploadType,
    total_files: int,
) -> UploadBatch:
    batch = UploadBatch(
        id=uuid.uuid4(),
        company_id=company_id,
        created_by=created_by,
        upload_type=upload_type.value,
        total_files=total_files,
        status=BatchStatus.uploading.value,
    )
    db.add(batch)
    await db.flush()
    return batch


async def get_batch_by_id(
    db: AsyncSession,
    batch_id: uuid.UUID,
    company_id: uuid.UUID | None = None,
    with_items: bool = False,
) -> UploadBatch | None:
    stmt = select(UploadBatch).where(UploadBatch.id == batch_id)
    if company_id is not None:
        stmt = stmt.where(UploadBatch.company_id == company_id)
    if with_items:
        stmt = stmt.options(selectinload(UploadBatch.items))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_batches(
    db: AsyncSession,
    company_id: uuid.UUID,
    offset: int = 0,
    limit: int = 20,
) -> list[UploadBatch]:
    result = await db.execute(
        select(UploadBatch)
        .where(UploadBatch.company_id == company_id)
        .order_by(UploadBatch.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(result.scalars().all())


async def update_batch_status(
    db: AsyncSession,
    batch_id: uuid.UUID,
    status: BatchStatus,
    completed_at: datetime | None = None,
) -> None:
    values: dict = {"status": status.value}
    if completed_at is not None:
        values["completed_at"] = completed_at
    await db.execute(
        update(UploadBatch).where(UploadBatch.id == batch_id).values(**values)
    )


async def increment_batch_counters(
    db: AsyncSession,
    batch_id: uuid.UUID,
    *,
    success: bool,
) -> UploadBatch | None:
    """Atomically increment processed_files and either successful or failed."""

    batch = await get_batch_by_id(db, batch_id)
    if batch is None:
        return None

    batch.processed_files += 1
    if success:
        batch.successful_files += 1
    else:
        batch.failed_files += 1

    # Auto-finalise when all files processed
    if batch.processed_files >= batch.total_files:
        batch.status = BatchStatus.review_pending.value
        batch.completed_at = datetime.now(UTC)

    db.add(batch)
    await db.flush()
    return batch


# ── UploadItem ────────────────────────────────────────────────────────────────


async def create_item(
    db: AsyncSession,
    batch_id: uuid.UUID,
    company_id: uuid.UUID,
    file_name: str,
    file_url: str,
    file_hash: str | None,
    file_size_bytes: int | None,
) -> UploadItem:
    item = UploadItem(
        id=uuid.uuid4(),
        batch_id=batch_id,
        company_id=company_id,
        file_name=file_name,
        file_url=file_url,
        file_hash=file_hash,
        file_size_bytes=file_size_bytes,
        status=ItemStatus.queued.value,
    )
    db.add(item)
    await db.flush()
    return item


async def get_item_by_id(
    db: AsyncSession,
    item_id: uuid.UUID,
    company_id: uuid.UUID | None = None,
) -> UploadItem | None:
    stmt = select(UploadItem).where(UploadItem.id == item_id)
    if company_id is not None:
        stmt = stmt.where(UploadItem.company_id == company_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_item_ocr_result(
    db: AsyncSession,
    item_id: uuid.UUID,
    ocr_extracted_data: dict,
    ocr_confidence_score: float,
    ocr_processing_time_ms: int,
    status: ItemStatus,
) -> None:
    await db.execute(
        update(UploadItem)
        .where(UploadItem.id == item_id)
        .values(
            ocr_extracted_data=ocr_extracted_data,
            ocr_confidence_score=Decimal(str(round(ocr_confidence_score, 2))),
            ocr_processing_time_ms=ocr_processing_time_ms,
            status=status.value,
            processed_at=datetime.now(UTC),
        )
    )


async def update_item_failed(
    db: AsyncSession,
    item_id: uuid.UUID,
    error_message: str,
) -> None:
    await db.execute(
        update(UploadItem)
        .where(UploadItem.id == item_id)
        .values(
            status=ItemStatus.failed.value,
            error_message=error_message,
            processed_at=datetime.now(UTC),
        )
    )


async def update_item_status(
    db: AsyncSession,
    item_id: uuid.UUID,
    status: ItemStatus,
) -> None:
    await db.execute(
        update(UploadItem).where(UploadItem.id == item_id).values(status=status.value)
    )


async def accept_item(
    db: AsyncSession,
    item: UploadItem,
    invoice_id: uuid.UUID,
) -> None:
    """Link the accepted invoice to the upload item and mark it accepted."""
    await db.execute(
        update(UploadItem)
        .where(UploadItem.id == item.id)
        .values(
            invoice_id=invoice_id,
            status=ItemStatus.accepted.value,
        )
    )


# ── Invoice ───────────────────────────────────────────────────────────────────


async def create_invoice(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    customer_id: uuid.UUID,
    invoice_number: str,
    amount: Decimal,
    currency: str,
    invoice_date: date,
    due_date: date,
    payment_terms_days: int,
    status: str,
    source: str,
    ocr_processed: bool,
    ocr_confidence_score: Decimal | None,
    ocr_extracted_data: dict | None,
    upload_item_id: uuid.UUID | None,
    file_url: str | None,
) -> Invoice:
    """Create an invoice from accepted OCR data. Catches unique constraint violations."""
    invoice = Invoice(
        id=uuid.uuid4(),
        company_id=company_id,
        customer_id=customer_id,
        invoice_number=invoice_number,
        amount=amount,
        currency=currency,
        invoice_date=invoice_date,
        due_date=due_date,
        payment_terms_days=payment_terms_days,
        status=status,
        source=source,
        ocr_processed=ocr_processed,
        ocr_confidence_score=ocr_confidence_score,
        ocr_extracted_data=ocr_extracted_data,
        upload_item_id=upload_item_id,
        file_url=file_url,
    )
    db.add(invoice)
    try:
        await db.flush()
    except IntegrityError as exc:
        await db.rollback()
        if "unique_invoice_per_company" in str(exc.orig):
            raise ConflictError(
                f"Invoice number '{invoice_number}' already exists for this company"
            ) from exc
        raise
    return invoice


async def get_invoice_by_id(
    db: AsyncSession,
    invoice_id: uuid.UUID,
    company_id: uuid.UUID,
) -> Invoice | None:
    result = await db.execute(
        select(Invoice).where(
            Invoice.id == invoice_id,
            Invoice.company_id == company_id,
            Invoice.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()
