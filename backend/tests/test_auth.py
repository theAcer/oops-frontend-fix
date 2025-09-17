import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_service import AuthService
from app.models.user import User
from app.models.merchant import Merchant

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, setup_test_db: None):
    """Test successful user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "password123", "name": "Test User"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "id" in data
    assert "created_at" in data

@pytest.mark.asyncio
async def test_register_user_existing_email(client: AsyncClient, setup_test_db: None):
    """Test registration with an already existing email."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "existing@example.com", "password": "password123", "name": "Existing User"}
    )
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "existing@example.com", "password": "newpassword", "name": "Another User"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_login_for_access_token(client: AsyncClient, setup_test_db: None):
    """Test successful user login and token generation."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "password123", "name": "Login User"}
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, setup_test_db: None):
    """Test login with invalid password."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "invalid@example.com", "password": "password123", "name": "Invalid User"}
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "invalid@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

@pytest.mark.asyncio
async def test_read_users_me(client: AsyncClient, setup_test_db: None):
    """Test retrieving current authenticated user."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "me@example.com", "password": "password123", "name": "Me User"}
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "me@example.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["name"] == "Me User"
    assert "id" in data

@pytest.mark.asyncio
async def test_read_users_me_unauthenticated(client: AsyncClient, setup_test_db: None):
    """Test retrieving current user without authentication."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

@pytest.mark.asyncio
async def test_register_user_with_merchant_id(client: AsyncClient, setup_test_db: None, db: AsyncSession):
    """Test user registration with an associated merchant ID."""
    merchant_data = {
        "business_name": "Test Merchant",
        "owner_name": "Merchant Owner",
        "email": "merchant@example.com",
        "phone": "254712345678",
        "business_type": "retail",
        "mpesa_till_number": "123456"
    }
    merchant_response = await client.post("/api/v1/merchants/", json=merchant_data)
    assert merchant_response.status_code == 201
    merchant_id = merchant_response.json()["id"]

    user_data = {
        "email": "user_with_merchant@example.com",
        "password": "password123",
        "name": "User With Merchant",
        "merchant_id": merchant_id
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    assert user_response.status_code == 201
    assert user_response.json()["merchant_id"] == merchant_id

    # Verify in DB
    auth_service = AuthService(db)
    user_in_db = await auth_service.get_user_by_email("user_with_merchant@example.com")
    assert user_in_db.merchant_id == merchant_id