import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_service import AuthService
from app.models.user import User
from app.models.merchant import Merchant
import uuid # Import uuid

# The authenticated_client fixture is now defined in conftest.py and will be used globally.
# No need to redefine it here.

@pytest.mark.asyncio
async def test_create_merchant(client: AsyncClient, setup_test_db: None):
    """Test successful merchant creation."""
    unique_email = f"test_merchant_{uuid.uuid4().hex}@example.com"
    unique_till = f"TILL{uuid.uuid4().hex[:8].upper()}"
    unique_phone = f"2547{uuid.uuid4().hex[:8]}"
    merchant_data = {
        "business_name": "Test Business",
        "owner_name": "John Doe",
        "email": unique_email,
        "phone": unique_phone,
        "business_type": "retail",
        "mpesa_till_number": unique_till
    }
    response = await client.post("/api/v1/merchants/", json=merchant_data)
    assert response.status_code == 201
    data = response.json()
    assert data["business_name"] == "Test Business"
    assert data["email"] == unique_email
    assert data["mpesa_till_number"] == unique_till
    assert "id" in data

@pytest.mark.asyncio
async def test_create_merchant_duplicate_till_number(client: AsyncClient, setup_test_db: None):
    """Test creating a merchant with a duplicate M-Pesa till number."""
    common_till = f"DUPLICATE_TILL_{uuid.uuid4().hex[:8].upper()}"
    unique_email_1 = f"dup_till_1_{uuid.uuid4().hex}@example.com"
    unique_phone_1 = f"2547{uuid.uuid4().hex[:8]}"
    unique_email_2 = f"dup_till_2_{uuid.uuid4().hex}@example.com"
    unique_phone_2 = f"2547{uuid.uuid4().hex[:8]}"

    merchant_data = {
        "business_name": "First Business",
        "owner_name": "Jane Doe",
        "email": unique_email_1,
        "phone": unique_phone_1,
        "business_type": "restaurant",
        "mpesa_till_number": common_till
    }
    await client.post("/api/v1/merchants/", json=merchant_data)

    duplicate_merchant_data = {
        "business_name": "Second Business",
        "owner_name": "Jim Beam",
        "email": unique_email_2,
        "phone": unique_phone_2,
        "business_type": "service",
        "mpesa_till_number": common_till
    }
    response = await client.post("/api/v1/merchants/", json=duplicate_merchant_data)
    assert response.status_code == 422  # Conflict because till number is unique
    #assert "Duplicate till number" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_merchant(client: AsyncClient, setup_test_db: None):
    """Test retrieving a merchant by ID."""
    unique_email = f"get_merchant_{uuid.uuid4().hex}@example.com"
    unique_till = f"GETTILL{uuid.uuid4().hex[:8].upper()}"
    unique_phone = f"2547{uuid.uuid4().hex[:8]}"
    merchant_data = {
        "business_name": "Get Test Business",
        "owner_name": "Get Owner",
        "email": unique_email,
        "phone": unique_phone,
        "business_type": "retail",
        "mpesa_till_number": unique_till
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
    unique_email = f"update_merchant_{uuid.uuid4().hex}@example.com"
    unique_till = f"UPDATETILL{uuid.uuid4().hex[:8].upper()}"
    unique_phone = f"2547{uuid.uuid4().hex[:8]}"
    merchant_data = {
        "business_name": "Update Test Business",
        "owner_name": "Update Owner",
        "email": unique_email,
        "phone": unique_phone,
        "business_type": "retail",
        "mpesa_till_number": unique_till
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
    unique_email = f"delete_merchant_{uuid.uuid4().hex}@example.com"
    unique_till = f"DELTILL{uuid.uuid4().hex[:8].upper()}"
    unique_phone = f"2547{uuid.uuid4().hex[:8]}"
    merchant_data = {
        "business_name": "Delete Test Business",
        "owner_name": "Delete Owner",
        "email": unique_email,
        "phone": unique_phone,
        "business_type": "retail",
        "mpesa_till_number": unique_till
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
    new_user_email = f"unlinked_user_{uuid.uuid4().hex}@example.com"
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
    new_merchant_email = f"new_linked_{uuid.uuid4().hex}@example.com"
    new_merchant_till = f"NEWLINKED{uuid.uuid4().hex[:8].upper()}"
    new_merchant_phone = f"2547{uuid.uuid4().hex[:8]}"
    new_merchant_data = {
        "business_name": "New Linked Business",
        "owner_name": "New Owner",
        "email": new_merchant_email,
        "phone": new_merchant_phone,
        "business_type": "retail",
        "mpesa_till_number": new_merchant_till
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
    new_merchant_email = f"another_{uuid.uuid4().hex}@example.com"
    new_merchant_till = f"ANOTHER{uuid.uuid4().hex[:8].upper()}"
    new_merchant_phone = f"2547{uuid.uuid4().hex[:8]}"
    new_merchant_data = {
        "business_name": "Another Business",
        "owner_name": "Another Owner",
        "email": new_merchant_email,
        "phone": new_merchant_phone,
        "business_type": "service",
        "mpesa_till_number": new_merchant_till
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
    unique_email = f"unauth_{uuid.uuid4().hex}@example.com"
    unique_till = f"UNAUTH{uuid.uuid4().hex[:8].upper()}"
    unique_phone = f"2547{uuid.uuid4().hex[:8]}"
    merchant_data = {
        "business_name": "Unauth Business",
        "owner_name": "Unauth Owner",
        "email": unique_email,
        "phone": unique_phone,
        "business_type": "retail",
        "mpesa_till_number": unique_till
    }
    response = await client.post(
        "/api/v1/merchants/link-user-merchant",
        json=merchant_data
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"