import asyncio
import logging
import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.pool import NullPool

from app.core.database import Base, get_db
from app.main import app
from app.models.merchant import Merchant

# Configure SQLAlchemy logging (optional but helpful for debugging)
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# Use a separate test database URL. Ensure it's configured for asyncpg.
TEST_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password@db-test:5432/test_db"
)

# --- ENGINE + SESSION FACTORY (Session-scoped) ---
_test_engine: AsyncEngine | None = None
_TestSessionLocal: async_sessionmaker[AsyncSession] | None = None

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """
    Session-scoped fixture to create the engine, create schema, and drop on teardown.
    Ensures a clean database state for the entire test session.
    """
    global _test_engine, _TestSessionLocal
    _test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
    _TestSessionLocal = async_sessionmaker(
        bind=_test_engine, expire_on_commit=False, class_=AsyncSession
    )

    # Use engine.begin() for DDL operations to ensure dedicated connection and transaction context
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield # Tests run here

    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _test_engine.dispose()

# --- TEST-ONLY DB SESSION (Function-scoped, Transactional) ---
@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a function-scoped AsyncSession with a transaction that is rolled back
    at the end of each test. This session is used for both direct test data setup
    and for overriding FastAPI's get_db dependency.
    """
    if _TestSessionLocal is None:
        raise RuntimeError("Test DB not initialized")
    async with _TestSessionLocal() as session:
        # Begin a transaction for the entire test function
        trans = await session.begin()
        try:
            yield session
        finally:
            # Roll back the transaction to ensure a clean state for the next test
            await trans.rollback()
            await session.close() # Ensure session is closed

# --- FASTAPI DEPENDENCY OVERRIDE (Autouse) ---
@pytest_asyncio.fixture(autouse=True)
async def override_get_db(db_session: AsyncSession):
    """
    Overrides FastAPI's get_db dependency to use the SAME session and transaction
    provided by the db_session fixture for each test.
    """
    async def _get_test_db():
        yield db_session # Yield the session from db_session fixture
    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()

# --- TEST DATA HELPERS ---
@pytest_asyncio.fixture
async def create_test_merchant(db_session: AsyncSession) -> Merchant:
    """
    Fixture to create a test merchant for use in tests, using the shared test session.
    Uses db_session.flush() to make data available without committing the transaction.
    """
    merchant = Merchant(
        business_name="Test Merchant",
        owner_name="Test Owner",
        email="test_merchant@example.com",
        phone="254700000000",
        business_type="retail",
        mpesa_till_number="TESTTILL"
    )
    db_session.add(merchant)
    await db_session.flush() # Changed from commit to flush
    await db_session.refresh(merchant)
    return merchant