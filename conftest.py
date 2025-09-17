import asyncio
import pytest
import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.database import Base, get_db # Import get_db to override it
from app.models.merchant import Merchant # Assuming Merchant model is needed for create_test_merchant
from app.main import app # Import your FastAPI app

# Configure SQLAlchemy logging for visibility
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

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
    Creates and drops schema once per test session, with explicit connection management.
    """
    print(f"Connecting to test database at: {TEST_DATABASE_URL}") # Added logging here
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)

    # Explicitly connect for schema creation to ensure isolation
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # The connection is automatically closed when exiting the 'async with' block

    yield engine # Now the engine is fully set up and ready for tests

    # Explicitly connect for schema dropping to ensure isolation
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    # The connection is automatically closed when exiting the 'async with' block

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
# FASTAPI DEPENDENCY OVERRIDE
# ------------------------
@pytest.fixture(autouse=True) # autouse=True makes this fixture run for every test
async def override_get_db_fixture(db: AsyncSession): # Now depends on the 'db' fixture
    """Override FastAPI's get_db dependency to use the SAME session as the test."""
    async def _get_test_db():
        yield db  # <-- Reuse the db fixture session
    app.dependency_overrides[get_db] = _get_test_db
    yield
    # Clear overrides after the test is done to prevent interference with other tests
    app.dependency_overrides.clear()

# ------------------------
# TEST DATA HELPERS
# ------------------------
@pytest.fixture(scope="function")
async def create_test_merchant(db: AsyncSession) -> Merchant: # Now depends on the 'db' fixture
    """
    Fixture to create a test merchant for use in tests, using the shared test session.
    """
    merchant = Merchant(
        business_name="Test Merchant",
        owner_name="Test Owner",
        email="test_merchant@example.com",
        phone="254700000000",
        business_type="retail",
        mpesa_till_number="TESTTILL"
    )
    db.add(merchant)
    await db.flush() # Changed from commit to flush
    await db.refresh(merchant)
    return merchant