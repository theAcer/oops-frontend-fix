import asyncio
import pytest
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.database import Base # Corrected import for Base

# Use a separate test database URL if available, otherwise use the main one
# Ensure the test database URL is also async
TEST_DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://").replace("zidisha_loyalty_db", "zidisha_loyalty_test_db")

# Create an async engine for tests with NullPool to prevent connection sharing issues
test_async_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False, # Set to True for debugging SQL queries during tests
    poolclass=NullPool, # Important for tests to ensure isolated connections
)

# Create an async sessionmaker for tests
TestAsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest.fixture(scope="session", autouse=True)
async def schema_setup():
    """
    Sets up the database schema once per test session and tears it down afterwards.
    """
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Ensure the engine is properly disposed after all tests in the session are done
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_async_engine.dispose() # Explicitly dispose of the engine

@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a function-scoped asynchronous database session for each test.
    Each test runs within a transaction that is rolled back afterwards.
    """
    async with TestAsyncSessionLocal() as session:
        async with session.begin(): # Start a transaction
            yield session
            await session.rollback() # Rollback after each test to clean state