import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy.pool import NullPool
from app.core.database import Base, get_db
from main import root, health_check # Import root and health_check
from httpx import AsyncClient
from app.models.merchant import Merchant, BusinessType
from app.models.user import User
from app.services.auth_service import AuthService
import os
import uuid
import sqlalchemy as sa # Re-add sqlalchemy import for raw SQL
# from alembic.config import Config # Removed alembic imports
# from alembic import command # Removed alembic imports
from fastapi import FastAPI # Added this line
from app.api.v1.api import api_router # Ensure API router is available for test app
# Import all models so SQLAlchemy registers them on Base.metadata
from app.models import *  # noqa: F401,F403

# Use a separate test database
# IMPORTANT: Use 'db-test' as the hostname to connect to the PostgreSQL service within Docker Compose
# Read the DATABASE_URL from environment variables, which is set correctly in docker-compose.yml
TEST_DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:password@db-test:5432/test_db")

# These will be initialized in the function-scoped fixture
_test_engine: AsyncEngine | None = None
_TestSessionLocal: async_sessionmaker[AsyncSession] | None = None

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override the get_db dependency for tests."""
    if _TestSessionLocal is None:
        print("ERROR: TestSessionLocal not initialized. Ensure setup_test_db fixture runs.") # Changed to print
        raise RuntimeError("TestSessionLocal not initialized. Ensure setup_test_db fixture runs.")
    async with _TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()  # Rollback on error
            await session.close() # Ensure the session is closed

# The app.dependency_overrides[get_db] is now handled within the client fixture
# app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(scope="function")
async def setup_test_db():
    """Set up and tear down the test database per test function."""
    global _test_engine, _TestSessionLocal
    
    print(f"DEBUG: Initializing test DB with URL: {TEST_DATABASE_URL}") # Changed to print

    _test_engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        poolclass=NullPool,
    )
    _TestSessionLocal = async_sessionmaker(
        _test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    conn = await _test_engine.connect()
    try:
        # Drop all tables first
        await conn.run_sync(Base.metadata.drop_all)

        # Drop and re-create enum types explicitly in a separate transaction
        await conn.run_sync(lambda sync_conn: sync_conn.execute(sa.text("DROP TYPE IF EXISTS businesstype CASCADE")))
        await conn.run_sync(lambda sync_conn: sync_conn.execute(sa.text("DROP TYPE IF EXISTS subscriptiontier CASCADE")))

        # Build BusinessType enum values from the model to keep in sync
        businesstype_values = ", ".join([f"'{e.value}'" for e in BusinessType])
        await conn.run_sync(lambda sync_conn: sync_conn.execute(sa.text(f"CREATE TYPE businesstype AS ENUM ({businesstype_values})")))
        await conn.run_sync(lambda sync_conn: sync_conn.execute(sa.text("CREATE TYPE subscriptiontier AS ENUM ('basic', 'premium', 'enterprise')")))

        # Close and re-open connection to ensure DDL is committed and visible
        await conn.close()
        conn = await _test_engine.connect()

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

        # Explicitly set customer_id to nullable for notifications table in test DB
        await conn.run_sync(lambda sync_conn: sync_conn.execute(sa.text("ALTER TABLE notifications ALTER COLUMN customer_id DROP NOT NULL")))

    finally:
        await conn.close()

    yield

    # Teardown: Drop all tables and enum types again
    print("DEBUG: Starting test teardown...") # Changed to print
    conn = await _test_engine.connect()
    try:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(lambda sync_conn: sync_conn.execute(sa.text("DROP TYPE IF EXISTS businesstype CASCADE")))
        await conn.run_sync(lambda sync_conn: sync_conn.execute(sa.text("DROP TYPE IF EXISTS subscriptiontier CASCADE")))
    finally:
        await conn.close()

    await _test_engine.dispose()
    _test_engine = None
    _TestSessionLocal = None

@pytest_asyncio.fixture(scope="function")
async def client(setup_test_db: None) -> AsyncGenerator[AsyncClient, None]:
    # Create a fresh FastAPI app instance for each test
    test_app = FastAPI(redirect_slashes=False)
    # Include the API router with its prefix
    test_app.include_router(api_router, prefix="/api/v1")
    # Manually add the root and health check routes
    test_app.add_api_route("/", root, methods=["GET"])
    test_app.add_api_route("/health", health_check, methods=["GET"])
    # Override the database dependency to use the test database session
    test_app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    if _TestSessionLocal is None:
        raise RuntimeError("TestSessionLocal not initialized. Ensure setup_test_db fixture runs.")
    async with _TestSessionLocal() as session:
        try:
            yield session
            await session.flush()  # Flush pending changes to the database
            await session.commit()  # Commit the transaction
        except Exception:
            await session.rollback()  # Rollback on error
            raise
        finally:
            await session.close() # Ensure the session is closed

@pytest_asyncio.fixture
async def create_test_merchant() -> Merchant:
    if _TestSessionLocal is None:
        raise RuntimeError("TestSessionLocal not initialized. Ensure setup_test_db fixture runs.")
    async with _TestSessionLocal() as session:
        unique = uuid.uuid4().hex[:8]
        merchant = Merchant(
            business_name=f"Test Merchant {unique}",
            owner_name="Test Owner",
            email=f"test_merchant_{unique}@example.com",
            phone="254700000000",
            business_type=BusinessType.RETAIL.value,
            mpesa_till_number=f"TESTTILL{unique}",
            subscription_tier="basic"
        )
        session.add(merchant)
        await session.commit()
        await session.refresh(merchant)
        return merchant

@pytest_asyncio.fixture
async def create_test_user(create_test_merchant: Merchant) -> User:
    if _TestSessionLocal is None:
        raise RuntimeError("TestSessionLocal not initialized. Ensure setup_test_db fixture runs.")
    async with _TestSessionLocal() as session:
        auth_service = AuthService(session)
        hashed_password = auth_service.get_password_hash("password123")
        user = User(
            email=f"test_user_{uuid.uuid4().hex[:8]}@example.com",
            hashed_password=hashed_password,
            name="Test User",
            merchant_id=create_test_merchant.id
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

@pytest_asyncio.fixture
async def get_auth_token(client: AsyncClient, create_test_user: User) -> str:
    login_data = {
        "email": create_test_user.email,
        "password": "password123"
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest_asyncio.fixture
async def authenticated_client(client: AsyncClient, get_auth_token: str) -> AsyncClient:
    client.headers["Authorization"] = f"Bearer {get_auth_token}"
    return client