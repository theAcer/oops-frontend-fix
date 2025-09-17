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
TEST_DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://").replace("zidisha_loyalty_db", "zidisha_loyalty_test_db")

@pytest.fixture(scope="session")
async def test_async_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Provides a session-scoped asynchronous engine for tests.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )
    yield engine
    await engine.dispose()

@pytest.fixture(scope="session")
async def TestAsyncSessionLocal_fixture(test_async_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """
    Provides a session-scoped asynchronous sessionmaker for tests.
    """
    return async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

@pytest.fixture(scope="session", autouse=True)
async def schema_setup(test_async_engine: AsyncEngine):
    """
    Sets up the database schema once per test session and tears it down afterwards.
    """
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    # Engine disposal is now handled by the test_async_engine fixture's teardown

@pytest.fixture(scope="function")
async def db(TestAsyncSessionLocal_fixture: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a function-scoped asynchronous database session for each test.
    Each test runs within a transaction that is rolled back afterwards.
    """
    async with TestAsyncSessionLocal_fixture() as session:
        try:
            yield session
        finally:
            # Ensure the transaction is rolled back and the session is closed
            # to release the connection back to the pool.
            await session.rollback()
            await session.close()

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