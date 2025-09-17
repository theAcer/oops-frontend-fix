import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base import Base
from app.models.merchant import Merchant
from app.schemas.merchant import MerchantCreate
from app.main import app
from app.api.deps import get_db
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

# Ensure the event loop is managed correctly for async tests
# pytest_asyncio.plugin.event_loop_scope = "session" # This can be set in pytest.ini or here

@pytest.fixture(scope="session")
async def async_engine():
    """
    Provides a session-scoped asynchronous SQLAlchemy engine.
    Creates and drops all tables once per test session.
    """
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(scope="function")
async def session(async_engine):
    """
    Provides a function-scoped, transactional database session for each test.
    All operations within the test will be part of this transaction,
    which is rolled back at the end of the test to ensure a clean state.
    """
    async with async_engine.connect() as connection:
        async with connection.begin() as transaction:
            # Bind the session to the connection for isolation
            async_session_local = async_sessionmaker(
                bind=connection, expire_on_commit=False, class_=AsyncSession
            )
            async with async_session_local() as session:
                yield session
                # Rollback the transaction to clean the database state for the next test
                await transaction.rollback()

@pytest.fixture(scope="function")
async def client(session: AsyncSession) -> AsyncClient:
    """
    Provides an asynchronous test client for FastAPI,
    with the database dependency overridden to use the test session.
    """
    app.dependency_overrides[get_db] = lambda: session
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def create_test_merchant(session: AsyncSession):
    """
    Fixture to create a test merchant in the database.
    """
    merchant_data = MerchantCreate(
        business_name="Test Merchant",
        owner_name="Test Owner",
        email="test_merchant@example.com",
        phone="254700000000",
        business_type="RETAIL",
        mpesa_till_number="TESTTILL",
        address="123 Test St",
        city="Test City",
        country="Kenya",
    )
    merchant = Merchant(**merchant_data.model_dump())
    session.add(merchant)
    await session.commit()
    await session.refresh(merchant)
    return merchant

@pytest.fixture(scope="function")
async def create_test_user(session: AsyncSession, create_test_merchant: Merchant):
    """
    Fixture to create a test user associated with a merchant.
    """
    user_data = UserCreate(
        email="testuser@example.com",
        password="testpassword",
        first_name="Test",
        last_name="User",
        phone_number="254712345678",
        role="merchant_admin",
        merchant_id=create_test_merchant.id,
    )
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number,
        role=user_data.role,
        merchant_id=user_data.merchant_id,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user