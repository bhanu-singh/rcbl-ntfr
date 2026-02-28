"""Data access layer for auth module. No business logic here."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.models import Company, User


async def get_company_by_slug(db: AsyncSession, slug: str) -> Company | None:
    result = await db.execute(
        select(Company).where(Company.slug == slug, Company.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def get_company_by_id(db: AsyncSession, company_id: uuid.UUID) -> Company | None:
    result = await db.execute(
        select(Company).where(Company.id == company_id, Company.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def create_company(db: AsyncSession, **kwargs) -> Company:
    company = Company(**kwargs)
    db.add(company)
    await db.flush()  # get the id before committing
    return company


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User).where(User.email == email, User.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, **kwargs) -> User:
    user = User(**kwargs)
    db.add(user)
    await db.flush()
    return user


async def update_last_login(db: AsyncSession, user: User) -> None:
    from datetime import UTC, datetime

    user.last_login_at = datetime.now(UTC)
    db.add(user)
    await db.flush()
