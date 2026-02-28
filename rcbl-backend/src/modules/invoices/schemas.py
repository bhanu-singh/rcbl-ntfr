"""Pydantic v2 schemas for invoice upload + OCR module.

All field constraints mirror the DB:
  V005: invoices — amount CHECK > 0, currency CHAR(3), payment_terms CHECK (1-365),
        due_date >= invoice_date, UNIQUE(company_id, invoice_number)
  V010: invoice_upload_batches — upload_type/status enums
  V011: invoice_upload_items — file_name VARCHAR(500), file_hash VARCHAR(64),
        ocr_confidence_score DECIMAL(3,2) CHECK (0-1)
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.modules.invoices.models import BatchStatus, BatchUploadType, ItemStatus

# ── OCR-extracted data (stored as JSONB) ──────────────────────────────────────


class OCRExtractedData(BaseModel):
    invoice_number: str | None = None
    amount: Decimal | None = None
    currency: str | None = None
    invoice_date: date | None = None
    due_date: date | None = None
    vendor_name: str | None = None
    raw_text: str | None = None


# ── Request schemas ───────────────────────────────────────────────────────────


class AcceptItemRequest(BaseModel):
    """
    User confirmation payload when accepting an OCR-processed item.

    customer_id is always required (maps to invoices.customer_id NOT NULL).
    All other fields are optional overrides merged on top of ocr_extracted_data.
    The service validates that the merged result satisfies all DB NOT NULL constraints.
    """

    # Required — invoices.customer_id NOT NULL (V005)
    customer_id: uuid.UUID

    # Optional overrides — all validated to match DB constraints
    invoice_number: str | None = Field(
        None,
        max_length=100,
        description="VARCHAR(100) NOT NULL in DB",
    )
    amount: Decimal | None = Field(
        None,
        gt=0,
        description="DECIMAL(10,2) CHECK (amount > 0)",
    )
    currency: str | None = Field(
        None,
        pattern=r"^[A-Z]{3}$",
        description="CHAR(3) — ISO 4217 code, e.g. EUR",
    )
    invoice_date: date | None = None
    due_date: date | None = None
    payment_terms_days: int | None = Field(
        None,
        gt=0,
        le=365,
        description="CHECK (payment_terms_days > 0 AND <= 365)",
    )

    @model_validator(mode="after")
    def due_after_invoice(self) -> "AcceptItemRequest":
        """Mirror DB CONSTRAINT due_after_invoice CHECK (due_date >= invoice_date)."""
        if self.invoice_date and self.due_date:
            if self.due_date < self.invoice_date:
                raise ValueError("due_date must be on or after invoice_date")
        return self


# ── Response schemas ──────────────────────────────────────────────────────────


class UploadItemResponse(BaseModel):
    """Response shape for a single upload item (V011 columns)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    batch_id: uuid.UUID
    file_name: str
    file_size_bytes: int | None = None
    file_hash: str | None = None
    status: ItemStatus
    ocr_confidence_score: float | None = None
    ocr_extracted_data: OCRExtractedData | None = None
    ocr_processing_time_ms: int | None = None
    error_message: str | None = None
    invoice_id: uuid.UUID | None = None
    created_at: datetime
    processed_at: datetime | None = None


class UploadBatchResponse(BaseModel):
    """Lightweight batch response without items (list endpoints)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    upload_type: BatchUploadType
    total_files: int
    processed_files: int
    successful_files: int
    failed_files: int
    status: BatchStatus
    created_at: datetime
    completed_at: datetime | None = None


class UploadBatchDetailResponse(UploadBatchResponse):
    """Full batch detail including all items."""

    items: list[UploadItemResponse] = []


class SingleUploadResponse(BaseModel):
    """Immediate response after a single file upload."""

    batch_id: uuid.UUID
    item_id: uuid.UUID
    status: str = "queued"
    message: str = "File uploaded successfully. OCR processing has been queued."


class BulkUploadItemSummary(BaseModel):
    """Summary of a single file within a bulk upload response."""

    item_id: uuid.UUID
    file_name: str
    status: str


class BulkUploadResponse(BaseModel):
    """Immediate response after bulk upload."""

    batch_id: uuid.UUID
    total_files: int
    items: list[BulkUploadItemSummary]
    message: str


class AcceptItemResponse(BaseModel):
    """Response after accepting an OCR item and creating an invoice."""

    invoice_id: uuid.UUID
    item_id: uuid.UUID
    message: str = "Invoice created successfully."
