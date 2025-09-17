import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_service import AuthService
from app.models.user import User
from app.models.merchant import Merchant

# The authenticated_client fixture is now defined in conftest.py and will be used globally.
# No need to redefine it here.

@pytest.mark.asyncio
async def test_create_merchant(client: AsyncClient, setup_test_db: None):
    """Test successful merchant creation."""
    merchant_data = {
        "business_name": "Test Business",
        "owner_name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "254712345678",
        "business_type": "retail",
        "mpesa_till_number": "12345"
    }
    response = await client.post("/api/v1/merchants/", json=merchant_data)
    assert response.status_code == 201
    data = response.json()
    assert data["business_name"] == "Test Business"
    assert data["email"] == "john.doe@example.com"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_merchant_duplicate_till_number(client: AsyncClient, setup_test_db: None):
    """Test creating a merchant with a duplicate M-Pesa till number."""
    merchant_data = {
        "business_name": "First Business",
        "owner_name": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone": "254712345679",
        "business_type": "restaurant",
        "mpesa_till_number": "DUPLICATE1"
    }
    await client.post("/api/v1/merchants/", json=merchant_data)

    duplicate_merchant_data = {
        "business_name": "Second Business",
        "owner_name": "Jim Beam",
        "email": "jim.beam@example.com",
        "phone": "254712345680",
        "business_type": "service",
        "mpesa_till_number": "DUPLICATE1"
    }
    response = await client.post("/api/v1/merchants/", json=duplicate_merchant_data)
    assert response.status_code == 422 # FastAPI validation error for unique constraint

@pytest.mark.asyncio
async def test_get_merchant(client: AsyncClient, setup_test_db: None):
    """Test retrieving a merchant by ID."""
    merchant_data = {
        "business_name": "Get Test Business",
        "owner_name": "Get Owner",
        "email": "get@example.com",
        "phone": "254712345681",
        "business_type": "retail",
        "mpesa_till_number": "GET123"
    }
    create_response = await client.post("/api/v1/merchants/", json=merchant_data)
    merchant_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/merchants/{merchant_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == merchant_id
    assert data["business_name"] == "Get Test Business"

@pytest.mark.asyncio
async def test_get_merchant_not_found(client: AsyncClient, setup_test_db: None):
    """Test retrieving a non-existent merchant."""
    response = await client.get("/api/v1/merchants/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Merchant not found"

@pytest.mark.asyncio
async def test_update_merchant(client: AsyncClient, setup_test_db: None):
    """Test updating an existing merchant."""
    merchant_data = {
        "business_name": "Update Test Business",
        "owner_name": "Update Owner",
        "email": "update@example.com",
        "phone": "254712345682",
        "business_type": "retail",
        "mpesa_till_number": "UPDATE123"
    }
    create_response = await client.post("/api/v1/merchants/", json=merchant_data)
    merchant_id = create_response.json()["id"]

    update_data = {"business_name": "Updated Business Name", "city": "Nairobi"}
    response = await client.put(f"/api/v1/merchants/{merchant_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["business_name"] == "Updated Business Name"
    assert data["city"] == "Nairobi"

@pytest.mark.asyncio
async def test_update_merchant_not_found(client: AsyncClient, setup_test_db: None):
    """Test updating a non-existent merchant."""
    update_data = {"business_name": "Non Existent"}
    response = await client.put("/api/v1/merchants/99999", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Merchant not found"

@pytest.mark.asyncio
async def test_delete_merchant(client: AsyncClient, setup_test_db: None):
    """Test deleting a merchant."""
    merchant_data = {
        "business_name": "Delete Test Business",
        "owner_name": "Delete Owner",
        "email": "delete@example.com",
        "phone": "254712345683",
        "business_type": "retail",
        "mpesa_till_number": "DELETE123"
    }
    create_response = await client.post("/api/v1/merchants/", json=merchant_data)
    merchant_id = create_response.json()["id"]

    response = await client.delete(f"/api/v1/merchants/{merchant_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Merchant deleted successfully"

    get_response = await client.get(f"/api/v1/merchants/{merchant_id}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_merchant_not_found(client: AsyncClient, setup_test_db: None):
    """Test deleting a non-existent merchant."""
    response = await client.delete("/api/v1/merchants/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Merchant not found"

@pytest.mark.asyncio
async def test_link_user_to_merchant(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: Merchant):
    """Test linking an authenticated user to a new merchant."""
    # The authenticated_client fixture already has a user linked to a merchant.
    # We need to create a new user that is NOT linked to a merchant first.
    # Then, we'll use that user's token to call link-user-merchant.

    # Create a new user without a merchant_id
    new_user_email = "unlinked_user@example.com"
    new_user_password = "password123"
    await authenticated_client.post(
        "/api/v1/auth/register",
        json={"email": new_user_email, "password": new_user_password, "name": "Unlinked User"}
    )
    login_response = await authenticated_client.post(
        "/api/v1/auth/login",
        json={"email": new_user_email, "password": new_user_password}
    )
    unlinked_user_token = login_response.json()["access_token"]

    # Create new merchant data
    new_merchant_data = {
        "business_name": "New Linked Business",
        "owner_name": "New Owner",
        "email": "new_linked@example.com",
        "phone": "254722222222",
        "business_type": "retail",
        "mpesa_till_number": "NEWLINKED"
    }

    # Call link-user-merchant with the unlinked user's token
    response = await authenticated_client.post(
        "/api/v1/merchants/link-user-merchant",
        json=new_merchant_data,
        headers={"Authorization": f"Bearer {unlinked_user_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["business_name"] == "New Linked Business"
    assert "id" in data
    new_merchant_id = data["id"]

    # Verify that the user is now linked to the new merchant
    auth_service = AuthService(db)
    user_in_db = await auth_service.get_user_by_email(new_user_email)
    assert user_in_db.merchant_id == new_merchant_id

@pytest.mark.asyncio
async def test_link_user_to_merchant_already_linked(authenticated_client: AsyncClient, create_test_merchant: Merchant):
    """Test linking a user who is already linked to a merchant."""
    # The authenticated_client fixture already has a user linked to a merchant.
    # We'll use its token to try and link to another merchant.
    
    # Create new merchant data
    new_merchant_data = {
        "business_name": "Another Business",
        "owner_name": "Another Owner",
        "email": "another@example.com",
        "phone": "254733333333",
        "business_type": "service",
        "mpesa_till_number": "ANOTHER123"
    }

    response = await authenticated_client.post(
        "/api/v1/merchants/link-user-merchant",
        json=new_merchant_data
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "User already linked to a merchant"

@pytest.mark.asyncio
async def test_link_user_to_merchant_unauthenticated(client: AsyncClient, setup_test_db: None):
    """Test linking a user to a merchant without authentication."""
    merchant_data = {
        "business_name": "Unauth Business",
        "owner_name": "Unauth Owner",
        "email": "unauth@example.com",
        "phone": "254744444444",
        "business_type": "retail",
        "mpesa_till_number": "UNAUTH123"
    }
    response = await client.post(
        "/api/v1/merchants/link-user-merchant",
        json=merchant_data
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"