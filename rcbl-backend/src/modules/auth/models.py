"""SQLAlchemy ORM models for companies and users.

Mapped from Flyway migrations:
  V002__create_companies.sql
  V003__create_users.sql
  V021__add_soft_deletes.sql

Type notes:
  - UUID          → postgresql UUID (as_uuid=True) / TEXT on SQLite
  - JSON          → postgresql JSONB / JSON on SQLite (SQLAlchemy maps automatically)
  - DateTime(tz)  → postgresql TIMESTAMPTZ / DATETIME on SQLite
"""

import uuid
from datetime import datetime

from sqlalchemy import JSON, BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.db.session import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    default_payment_terms: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    default_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")
    eu_regulation_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    storage_quota_bytes: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=10_737_418_240
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    # V021 soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    users: Mapped[list["User"]] = relationship("User", back_populates="company")


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="UTC")
    # JSON maps to JSONB on PostgreSQL, JSON on SQLite
    email_notifications: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # V021 soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    company: Mapped["Company"] = relationship("Company", back_populates="users")
