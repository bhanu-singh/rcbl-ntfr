"""SQLAlchemy ORM models for invoice upload and OCR processing.

Mapped from Flyway migrations:
  V005__create_invoices.sql
  V010__create_invoice_upload_batches.sql
  V011__create_invoice_upload_items.sql
  V021__add_soft_deletes.sql       (deleted_at on invoices)
  V022__add_optimistic_locking.sql (version on invoices)
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy import Uuid as UuidType
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.db.session import Base

# ── Customer stub — satisfies FK from Invoice.customer_id ─────────────────────
# The full Customers module is not yet implemented. This stub ensures
# Base.metadata.create_all() can resolve the FK in tests.


class Customer(Base):
    """Minimal stub for invoices.customer_id FK. Will be replaced by a full module."""

    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(
        UuidType(), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UuidType(),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


# ── Enums — values match DB CHECK constraints exactly ─────────────────────────


class InvoiceStatus(StrEnum):
    pending = "pending"
    due_soon = "due_soon"
    overdue = "overdue"
    paid = "paid"
    written_off = "written_off"


class InvoiceSource(StrEnum):
    manual = "manual"
    upload = "upload"
    bulk_upload = "bulk_upload"
    csv_import = "csv_import"
    api_sync = "api_sync"
    email_forward = "email_forward"
    webhook = "webhook"


class ExternalSyncStatus(StrEnum):
    not_synced = "not_synced"
    synced = "synced"
    sync_failed = "sync_failed"


class BatchUploadType(StrEnum):
    single = "single"
    bulk = "bulk"
    csv_import = "csv_import"


class BatchStatus(StrEnum):
    uploading = "uploading"
    processing = "processing"
    review_pending = "review_pending"
    completed = "completed"
    failed = "failed"


class ItemStatus(StrEnum):
    queued = "queued"
    processing = "processing"
    ready = "ready"
    review_pending = "review_pending"
    accepted = "accepted"
    rejected = "rejected"
    failed = "failed"


# ── ORM Models ────────────────────────────────────────────────────────────────


class UploadBatch(Base):
    """V010 — invoice_upload_batches."""

    __tablename__ = "invoice_upload_batches"

    id: Mapped[uuid.UUID] = mapped_column(
        UuidType(), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UuidType(),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    upload_type: Mapped[str] = mapped_column(String(20), nullable=False)
    total_files: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processed_files: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    successful_files: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_files: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    # JSON: stores CSV column mappings or other batch-level metadata
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UuidType(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    items: Mapped[list["UploadItem"]] = relationship("UploadItem", back_populates="batch")


class UploadItem(Base):
    """V011 — invoice_upload_items."""

    __tablename__ = "invoice_upload_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UuidType(), primary_key=True, default=uuid.uuid4
    )
    batch_id: Mapped[uuid.UUID] = mapped_column(
        UuidType(),
        ForeignKey("invoice_upload_batches.id", ondelete="CASCADE"),
        nullable=False,
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UuidType(),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    # VARCHAR(500) NOT NULL
    file_name: Mapped[str] = mapped_column(String(500), nullable=False)
    # TEXT NOT NULL — S3/MinIO object path
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    # VARCHAR(64) — SHA-256 hex digest for deduplication
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    # DECIMAL(3,2) CHECK (0-1)
    ocr_confidence_score: Mapped[Decimal | None] = mapped_column(
        Numeric(3, 2), nullable=True
    )
    ocr_extracted_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ocr_processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    # FK → invoices(id) SET NULL — populated after acceptance
    invoice_id: Mapped[uuid.UUID | None] = mapped_column(
        UuidType(),
        ForeignKey("invoices.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    batch: Mapped["UploadBatch"] = relationship("UploadBatch", back_populates="items")


class Invoice(Base):
    """
    V005 — invoices (core fields)
    + V021 deleted_at
    + V022 version (optimistic locking — DB trigger auto-increments on UPDATE)
    """

    __tablename__ = "invoices"

    # ── Core (V005) ────────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UuidType(), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UuidType(),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UuidType(),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
    )
    # VARCHAR(100) NOT NULL — UNIQUE per company enforced at DB level
    invoice_number: Mapped[str] = mapped_column(String(100), nullable=False)
    # DECIMAL(10,2) NOT NULL CHECK (> 0)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    # CHAR(3) DEFAULT 'EUR'
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    # INTEGER DEFAULT 30 CHECK (1-365)
    payment_terms_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    # DATE NOT NULL — DB CHECK due_date >= invoice_date
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    file_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_reminder_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_action_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reminder_sequence_step: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # ── Ingestion source ───────────────────────────────────────────────────────
    source: Mapped[str] = mapped_column(String(30), nullable=False, default="manual")

    # ── OCR fields ─────────────────────────────────────────────────────────────
    ocr_processed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ocr_confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(3, 2), nullable=True)
    ocr_extracted_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # FK to invoice_upload_items — added by V012 migration
    upload_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UuidType(), nullable=True
    )

    # ── External integration ───────────────────────────────────────────────────
    external_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    external_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    external_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    external_sync_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="not_synced"
    )

    # ── SevDesk legacy ─────────────────────────────────────────────────────────
    sevdesk_invoice_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sevdesk_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sevdesk_sync_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="not_synced"
    )

    # ── AI prediction (post-MVP, all nullable) ─────────────────────────────────
    ai_conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UuidType(), nullable=True
    )
    payment_probability_7d: Mapped[Decimal | None] = mapped_column(Numeric(3, 2), nullable=True)
    payment_probability_30d: Mapped[Decimal | None] = mapped_column(Numeric(3, 2), nullable=True)
    expected_payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    prediction_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    anomaly_flags: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # ── Timestamps ─────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    # V021 soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # V022 optimistic locking (DB trigger auto-increments on every UPDATE)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
