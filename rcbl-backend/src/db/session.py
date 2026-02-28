from collections.abc import AsyncGenerator
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=settings.ENVIRONMENT == "development",
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def set_tenant_context(session: AsyncSession, company_id: UUID) -> None:
    """Set PostgreSQL RLS context variable for the current transaction.

    asyncpg does not support $1 placeholders in SET LOCAL statements — the value
    must be a quoted string literal embedded directly in the SQL.
    The company_id is a UUID so there is no injection risk.
    """
    safe_id = str(company_id).replace("'", "")  # strip any stray quotes (UUID is always safe)
    await session.execute(text(f"SET LOCAL app.current_company_id = '{safe_id}'"))
