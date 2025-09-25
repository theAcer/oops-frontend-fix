import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from app.core.config import settings
from app.db.base import Base
from app.models.merchant import Merchant # Assuming this is the model for create_test_merchant

# It's good practice to explicitly set asyncio_mode in pytest.ini
# if you haven't already. Add this to your pytest.ini:
# [pytest]
# asyncio_mode = auto

@pytest.fixture(scope="session")
async def async_engine():
    """Provides an asynchronous SQLAlchemy engine for tests."""
    engine = create_async_engine(settings.DATABASE_URL_TEST, echo=False)
    yield engine
    await engine.dispose()

@pytest.fixture(scope="session")
async def setup_test_db(async_engine):
    """Creates and drops all tables for the test database."""
    # Use a separate connection for DDL operations to avoid conflicts
    async with async_engine.connect() as conn:
        # Drop all tables
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Teardown: Drop all tables again
    async with async_engine.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def async_session(async_engine, setup_test_db):
    """Provides an asynchronous SQLAlchemy session for each test, with automatic rollback."""
    async_session_maker = async_sessionmaker(
        async_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session_maker() as session:
        # Start a transaction for the test. All operations within the test
        # will be part of this transaction.
        async with session.begin():
            yield session
        # After the test, the transaction is automatically rolled back
        # by the outer async_session_maker context manager if an exception occurred,
        # or explicitly rolled back here to ensure a clean state.
        await session.rollback()

@pytest.fixture(scope="function")
async def create_test_merchant(async_session: AsyncSession):
    """Creates a test merchant and adds it to the session."""
    merchant = Merchant(
        business_name="Test Merchant",
        owner_name="Test Owner",
        email="test_merchant@example.com",
        phone="254700000000",
        business_type="RETAIL",
        mpesa_till_number="TESTTILL",
        is_active=True,
        subscription_tier="basic",
        city="Nairobi",
        country="Kenya",
    )
    async_session.add(merchant)
    # Flush the session to assign an ID to the merchant, but do not commit.
    # The transaction is managed by the async_session fixture.
    await async_session.flush()
    await async_session.refresh(merchant)
    yield merchant