import asyncio
import pytest
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.database import Base
from app.models.merchant import Merchant # Assuming Merchant model is needed for create_test_merchant

# Use a separate test database URL if available, otherwise use the main one
# Ensure the test database URL is also async
TEST_DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
).replace("zidisha_loyalty_db", "zidisha_loyalty_test_db")

# ------------------------
# ENGINE + SCHEMA SETUP
# ------------------------
@pytest.fixture(scope="session")
async def test_async_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Provides a session-scoped asynchronous engine for tests.
    Creates and drops schema once per test session.
    """
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(scope="function")
async def db(test_async_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Per-test session with SAVEPOINT rollback (ensures full isolation).
    Each test gets its own session and transaction.
    """
    async_session_maker = async_sessionmaker(
        bind=test_async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with async_session_maker() as session:
        # Start a transaction for the test
        trans = await session.begin()
        try:
            yield session
        finally:
            # Roll back the transaction to ensure database state is clean
            await trans.rollback()
            # Close the session to release the connection back to the pool
            await session.close()

# ------------------------
# TEST DATA HELPERS
# ------------------------
@pytest.fixture(scope="function")
async def create_test_merchant(db: AsyncSession) -> Merchant:
    """
    Fixture to create a test merchant for use in tests.
    """
    merchant = Merchant(
        name="Test Merchant",
        email="test@merchant.com",
        phone_number="254712345678",
        business_location="Nairobi",
        industry="Retail",
        # Add any other required fields for Merchant
    )
    db.add(merchant)
    await db.flush()
    await db.refresh(merchant)
    return merchant