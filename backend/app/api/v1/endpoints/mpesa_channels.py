"""
M-Pesa Channel Management API Endpoints

RESTful API for managing M-Pesa channels in the multi-tenant loyalty platform.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_merchant
from app.models.merchant import Merchant
from app.models.mpesa_channel import ChannelType, ChannelStatus
from app.services.mpesa_channel_service import MpesaChannelManagementService
from app.schemas.mpesa_channel import (
    MpesaChannelCreate,
    MpesaChannelUpdate,
    MpesaChannelResponse,
    MpesaChannelListResponse,
    MpesaChannelVerificationResponse,
    MpesaChannelURLRegistrationRequest,
    MpesaChannelURLRegistrationResponse,
    MpesaChannelStatusResponse,
    MpesaChannelSimulationRequest,
    MpesaChannelSimulationResponse
)
from app.core.exceptions import NotFoundError, ValidationError, BusinessLogicError

router = APIRouter()


@router.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify router is working"""
    return {"message": "M-Pesa channels router is working!", "timestamp": "2025-09-25T15:26:00"}


@router.get("", response_model=MpesaChannelListResponse)
@router.get("/", response_model=MpesaChannelListResponse)
async def list_mpesa_channels(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    channel_type: Optional[ChannelType] = Query(None, description="Filter by channel type"),
    status: Optional[ChannelStatus] = Query(None, description="Filter by status"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    merchant_id: int = Query(..., description="Merchant ID"),  # Temporary: get from query param
    db: AsyncSession = Depends(get_db)
):
    """
    List M-Pesa channels for the specified merchant.
    
    **TEMPORARY**: This endpoint accepts merchant_id as query parameter for testing.
    In production, this should use authentication to get the current merchant.
    
    **Filtering Options:**
    - `channel_type`: Filter by paybill, till, or buygoods
    - `status`: Filter by channel status (draft, configured, verified, etc.)
    - `is_active`: Filter by active/inactive channels
    
    **Pagination:**
    - Results are paginated with configurable page size
    - Primary channels are shown first
    """
    print(f"[DEBUG] list_mpesa_channels called with merchant_id={merchant_id}")
    try:
        service = MpesaChannelManagementService(db)
        result = await service.list_channels(
            merchant_id=merchant_id,  # Use merchant_id from query param
            page=page,
            per_page=per_page,
            channel_type=channel_type,
            status=status,
            is_active=is_active
        )
        print(f"[DEBUG] Service returned: {result}")
        return result
    except Exception as e:
        print(f"[DEBUG] Error in list_mpesa_channels: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=MpesaChannelResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=MpesaChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_mpesa_channel(
    channel_data: MpesaChannelCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new M-Pesa channel.
    
    **TEMPORARY**: This endpoint doesn't require authentication for testing.
    In production, this should use authentication to get the current merchant.
    
    This endpoint allows merchants to add M-Pesa channels (PayBill, Till, Buy Goods)
    with their own Daraja API credentials. Credentials are encrypted before storage.
    
    **Features:**
    - Multiple channels per merchant
    - Secure credential encryption
    - Account number mapping for PayBills
    - Automatic configuration validation
    """
    print(f"[DEBUG] create_mpesa_channel called with data: {channel_data}")
    try:
        service = MpesaChannelManagementService(db)
        # For testing, we'll use merchant_id from the channel_data or default to 1
        merchant_id = getattr(channel_data, 'merchant_id', 1)
        print(f"[DEBUG] Using merchant_id: {merchant_id}")
        result = await service.create_channel(merchant_id, channel_data)
        print(f"[DEBUG] Channel created successfully: {result}")
        return result
    except ValidationError as e:
        print(f"[DEBUG] ValidationError: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        print(f"[DEBUG] BusinessLogicError: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        print(f"[DEBUG] Unexpected error in create_mpesa_channel: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{channel_id}", response_model=MpesaChannelResponse)
async def get_mpesa_channel(
    channel_id: int = Path(..., description="M-Pesa channel ID"),
    current_merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific M-Pesa channel.
    
    Returns detailed information about the channel including:
    - Configuration status
    - URL registration status
    - Verification details
    - Account mappings (for PayBills)
    
    **Note:** Credentials are never returned for security reasons.
    """
    try:
        service = MpesaChannelManagementService(db)
        return await service.get_channel(current_merchant.id, channel_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{channel_id}", response_model=MpesaChannelResponse)
async def update_mpesa_channel(
    channel_id: int = Path(..., description="M-Pesa channel ID"),
    update_data: MpesaChannelUpdate = ...,
    current_merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an M-Pesa channel.
    
    **Updatable Fields:**
    - Channel name and configuration
    - Credentials (will be re-encrypted)
    - URL configuration
    - Account mappings
    - Status and metadata
    
    **Business Rules:**
    - Only one primary channel per merchant
    - Shortcode must be unique per merchant
    - Status transitions are validated
    """
    try:
        service = MpesaChannelManagementService(db)
        return await service.update_channel(current_merchant.id, channel_id, update_data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mpesa_channel(
    channel_id: int = Path(..., description="M-Pesa channel ID"),
    current_merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an M-Pesa channel.
    
    **Warning:** This action is irreversible. Consider deactivating the channel instead.
    
    **Business Rules:**
    - Cannot delete channels with active transactions
    - All associated data will be removed
    - Credentials are securely wiped
    """
    try:
        service = MpesaChannelManagementService(db)
        await service.delete_channel(current_merchant.id, channel_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/{channel_id}/verify", response_model=MpesaChannelVerificationResponse)
async def verify_mpesa_channel(
    channel_id: int = Path(..., description="M-Pesa channel ID"),
    current_merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify M-Pesa channel with Safaricom API.
    
    This endpoint:
    1. Validates channel credentials with Safaricom
    2. Checks account balance access
    3. Updates channel status to 'verified'
    4. Stores verification response for audit
    
    **Prerequisites:**
    - Channel must be in 'configured' status
    - Valid consumer key and secret required
    - Network connectivity to Safaricom API
    """
    try:
        service = MpesaChannelManagementService(db)
        result = await service.verify_channel(current_merchant.id, channel_id)
        
        return MpesaChannelVerificationResponse(
            channel_id=result["channel_id"],
            status="verified" if result["verified"] else "failed",
            verified=result["verified"],
            verification_details=result.get("verification_details", {}),
            verified_at=result.get("verified_at") or result.get("error_details", {}).get("timestamp")
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{channel_id}/register-urls", response_model=MpesaChannelURLRegistrationResponse)
async def register_channel_urls(
    channel_id: int = Path(..., description="M-Pesa channel ID"),
    registration_data: MpesaChannelURLRegistrationRequest = ...,
    current_merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db)
):
    """
    Register validation and confirmation URLs for C2B transactions.
    
    **Required URLs:**
    - `validation_url`: Called to validate incoming transactions
    - `confirmation_url`: Called to confirm successful transactions
    
    **Prerequisites:**
    - Channel must be verified
    - URLs must be publicly accessible
    - URLs should implement proper M-Pesa callback handling
    
    **Response Types:**
    - `Completed`: Only successful transactions trigger confirmation
    - `Cancelled`: Both successful and failed transactions trigger confirmation
    """
    try:
        service = MpesaChannelManagementService(db)
        result = await service.register_urls(
            merchant_id=current_merchant.id,
            channel_id=channel_id,
            validation_url=str(registration_data.validation_url),
            confirmation_url=str(registration_data.confirmation_url),
            response_type=registration_data.response_type
        )
        
        return MpesaChannelURLRegistrationResponse(
            channel_id=result["channel_id"],
            status="registered" if result["registered"] else "failed",
            registered=result["registered"],
            registration_details=result.get("registration_details", {}),
            registered_at=result.get("registered_at")
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/{channel_id}/status", response_model=MpesaChannelStatusResponse)
async def get_channel_status(
    channel_id: int = Path(..., description="M-Pesa channel ID"),
    current_merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive status of an M-Pesa channel.
    
    **Status Information:**
    - Configuration completeness
    - Verification status
    - URL registration status
    - Transaction readiness
    - Health check details
    - Error information (if any)
    
    **Use Cases:**
    - Dashboard health monitoring
    - Troubleshooting configuration issues
    - Pre-transaction validation
    """
    try:
        service = MpesaChannelManagementService(db)
        result = await service.get_channel_status(current_merchant.id, channel_id)
        
        return MpesaChannelStatusResponse(**result)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{channel_id}/simulate", response_model=MpesaChannelSimulationResponse)
async def simulate_transaction(
    channel_id: int = Path(..., description="M-Pesa channel ID"),
    simulation_data: MpesaChannelSimulationRequest = ...,
    current_merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db)
):
    """
    Simulate a C2B transaction for testing purposes.
    
    **Simulation Features:**
    - Test channel configuration
    - Validate transaction flow
    - Generate test callbacks
    - Verify account mappings (PayBill)
    
    **Prerequisites:**
    - Channel must be active and ready for transactions
    - Valid phone number format (254XXXXXXXXX)
    - Amount within M-Pesa limits (1-70,000 KES)
    
    **Note:** This only works in sandbox environment. Production channels
    cannot simulate transactions.
    """
    try:
        service = MpesaChannelManagementService(db)
        result = await service.simulate_transaction(
            merchant_id=current_merchant.id,
            channel_id=channel_id,
            amount=simulation_data.amount,
            customer_phone=simulation_data.customer_phone,
            bill_ref=simulation_data.bill_ref
        )
        
        return MpesaChannelSimulationResponse(**result)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/{channel_id}/activate", response_model=MpesaChannelResponse)
async def activate_channel(
    channel_id: int = Path(..., description="M-Pesa channel ID"),
    current_merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db)
):
    """
    Activate an M-Pesa channel for live transactions.
    
    **Prerequisites:**
    - Channel must be verified
    - URLs must be registered
    - All configuration must be complete
    
    **Effect:**
    - Sets channel status to 'active'
    - Enables transaction processing
    - Channel becomes available for loyalty program integration
    """
    try:
        service = MpesaChannelManagementService(db)
        update_data = MpesaChannelUpdate(status=ChannelStatus.ACTIVE, is_active=True)
        return await service.update_channel(current_merchant.id, channel_id, update_data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/{channel_id}/deactivate", response_model=MpesaChannelResponse)
async def deactivate_channel(
    channel_id: int = Path(..., description="M-Pesa channel ID"),
    current_merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate an M-Pesa channel.
    
    **Effect:**
    - Sets channel status to 'suspended'
    - Stops processing new transactions
    - Preserves configuration for future reactivation
    
    **Use Cases:**
    - Temporary maintenance
    - Credential rotation
    - Business policy changes
    """
    try:
        service = MpesaChannelManagementService(db)
        update_data = MpesaChannelUpdate(status=ChannelStatus.SUSPENDED, is_active=False)
        return await service.update_channel(current_merchant.id, channel_id, update_data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Bulk operations for advanced users
@router.get("/bulk/status", response_model=List[MpesaChannelStatusResponse])
async def get_all_channels_status(
    current_merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db)
):
    """
    Get status of all M-Pesa channels for the merchant.
    
    **Use Cases:**
    - Dashboard overview
    - Health monitoring
    - Bulk status checks
    """
    service = MpesaChannelManagementService(db)
    channels_list = await service.list_channels(current_merchant.id, page=1, per_page=100)
    
    status_results = []
    for channel in channels_list.channels:
        try:
            status = await service.get_channel_status(current_merchant.id, channel.id)
            status_results.append(MpesaChannelStatusResponse(**status))
        except Exception:
            # Continue with other channels if one fails
            continue
    
    return status_results
