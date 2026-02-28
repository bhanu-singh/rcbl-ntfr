"""Pydantic v2 schemas for auth module.

Field constraints mirror the DB:
  V002: companies.email VARCHAR(255), default_currency CHAR(3), default_payment_terms CHECK (1-365)
  V003: users.email UNIQUE, name VARCHAR(255), timezone VARCHAR(50) DEFAULT 'UTC', password bcrypt
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    # ── Company ───────────────────────────────────────────────────────────────
    company_name: str = Field(..., min_length=1, max_length=255)
    company_email: EmailStr
    # Slug is auto-generated from company_name via python-slugify in the service

    # ── First user ────────────────────────────────────────────────────────────
    user_name: str = Field(..., min_length=1, max_length=255)
    user_email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters")
    timezone: str = Field("UTC", max_length=50)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    email: str
    default_payment_terms: int
    default_currency: str
    eu_regulation_enabled: bool
    created_at: datetime


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    email: str
    name: str
    timezone: str
    created_at: datetime
    last_login_at: datetime | None = None


class MeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user: UserResponse
    company: CompanyResponse
