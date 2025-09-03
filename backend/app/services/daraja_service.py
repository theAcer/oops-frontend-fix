import httpx
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.models.merchant import Merchant
from app.models.transaction import Transaction
from app.models.customer import Customer
from app.services.customer_service import CustomerService
import json
import logging
import base64

logger = logging.getLogger(__name__)

class DarajaAPIError(Exception):
    """Custom exception for Daraja API errors"""
    pass

class DarajaService:
    def __init__(self, db: AsyncSession, merchant_id: int):
        self.db = db
        self.merchant_id = merchant_id
        self.customer_service = CustomerService(db)
        self._merchant_credentials: Optional[Merchant] = None # Cache merchant credentials

    async def _load_merchant_credentials(self) -> Merchant:
        if self._merchant_credentials:
            return self._merchant_credentials
        
        merchant = await self.db.execute(
            select(Merchant).where(Merchant.id == self.merchant_id)
        )
        merchant = merchant.scalar_one_or_none()
        
        if not merchant:
            raise ValueError(f"Merchant {self.merchant_id} not found")
        
        if not merchant.daraja_consumer_key or not merchant.daraja_consumer_secret or not merchant.daraja_shortcode or not merchant.daraja_passkey:
            raise DarajaAPIError(f"Daraja API credentials not configured for merchant {self.merchant_id}")
            
        self._merchant_credentials = merchant
        return merchant

    async def _get_access_token(self, merchant: Merchant) -> str:
        """Get Daraja API access token using consumer key and secret."""
        consumer_key = merchant.daraja_consumer_key
        consumer_secret = merchant.daraja_consumer_secret
        
        if not consumer_key or not consumer_secret:
            raise DarajaAPIError("Daraja consumer key or secret not configured.")

        auth_string = f"{consumer_key}:{consumer_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()

        token_url = f"{settings.DARAJA_API_URL}/oauth/v1/generate?grant_type=client_credentials"
        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(token_url, headers=headers)
                response.raise_for_status()
                return response.json()["access_token"]
            except httpx.HTTPStatusError as e:
                logger.error(f"Daraja API token error: {e.response.status_code} - {e.response.text}")
                raise DarajaAPIError(f"Failed to get Daraja access token: {e.response.status_code}")
            except httpx.RequestError as e:
                logger.error(f"Daraja API token request error: {str(e)}")
                raise DarajaAPIError(f"Request to get Daraja access token failed: {str(e)}")

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make authenticated request to Daraja API"""
        merchant = await self._load_merchant_credentials()
        access_token = await self._get_access_token(merchant) # Get token for each request (simplified)
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        url = f"{settings.DARAJA_API_URL.rstrip('/')}/{endpoint.lstrip('/')}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Daraja API HTTP error: {e.response.status_code} - {e.response.text}")
                raise DarajaAPIError(f"API request failed: {e.response.status_code}")
            except httpx.RequestError as e:
                logger.error(f"Daraja API request error: {str(e)}")
                raise DarajaAPIError(f"Request failed: {str(e)}")

    async def get_merchant_transactions(
        self, 
        till_number: str, # This should be merchant.mpesa_till_number
        start_date: datetime, 
        end_date: datetime,
        page: int = 1,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Fetch transactions for a specific till number (simplified for Daraja)"""
        # Daraja API doesn't typically have a direct 'get all transactions by till number' endpoint for pulling.
        # Transactions are usually pushed via C2B webhooks.
        # This method is a placeholder, assuming a mock Daraja API or a custom endpoint that aggregates.
        # For a real Daraja integration, this would be more complex, possibly involving querying a local DB of webhook-received transactions.
        # For now, I'll keep the structure but acknowledge its simplification.
        
        # The original `DaraaaService` had `/transactions` endpoint. Let's keep that for the mock.
        params = {
            "till_number": till_number,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "page": page,
            "limit": limit
        }
        
        return await self._make_request("GET", "/transactions", params=params)

    async def get_transaction_details(self, transaction_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific transaction (simplified for Daraja)"""
        return await self._make_request("GET", f"/transactions/{transaction_id}")

    async def verify_till_number(self, till_number: str) -> Dict[str, Any]:
        """Verify if a till number is valid and accessible (simplified for Daraja)"""
        return await self._make_request("GET", f"/merchants/verify/{till_number}")

    def _normalize_phone_number(self, phone: str) -> str:
        """Normalize phone number to standard format"""
        # Remove any non-digit characters
        phone = ''.join(filter(str.isdigit, phone))
        
        # Handle Kenyan phone numbers
        if phone.startswith('254'):
            return phone
        elif phone.startswith('0'):
            return '254' + phone[1:]
        elif len(phone) == 9:
            return '254' + phone
        
        return phone

    def _parse_daraja_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Daraja transaction data into our format"""
        # This parsing logic might need to be adjusted based on actual Daraja webhook/API response format
        return {
            "mpesa_receipt_number": transaction_data.get("receipt_number"),
            "mpesa_transaction_id": transaction_data.get("transaction_id"),
            "till_number": transaction_data.get("till_number"),
            "amount": float(transaction_data.get("amount", 0)),
            "customer_phone": self._normalize_phone_number(transaction_data.get("customer_phone", "")),
            "customer_name": transaction_data.get("customer_name"),
            "transaction_date": datetime.fromisoformat(transaction_data.get("transaction_date")),
            "description": transaction_data.get("description"),
            "reference": transaction_data.get("reference"),
            "daraaa_transaction_id": transaction_data.get("id"), # Renamed from daraaa_transaction_id to daraja_transaction_id in model? No, keep for now.
            "raw_daraaa_data": json.dumps(transaction_data)
        }

    async def sync_merchant_transactions(
        self, 
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Sync transactions for a merchant from Daraja API"""
        merchant = await self._load_merchant_credentials() # Load merchant to get till number and last sync
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = merchant.last_sync_at or (end_date - timedelta(days=days_back))
        
        logger.info(f"Syncing transactions for merchant {self.merchant_id} from {start_date} to {end_date}")
        
        new_transactions = 0
        updated_transactions = 0
        total_amount = 0.0
        page = 1
        
        try:
            while True:
                # Fetch transactions from Daraja API
                response = await self.get_merchant_transactions(
                    till_number=merchant.mpesa_till_number,
                    start_date=start_date,
                    end_date=end_date,
                    page=page,
                    limit=100
                )
                
                transactions = response.get("data", [])
                if not transactions:
                    break
                
                # Process each transaction
                for transaction_data in transactions:
                    try:
                        parsed_data = self._parse_daraja_transaction(transaction_data)
                        
                        # Check if transaction already exists
                        existing_transaction = await self.db.execute(
                            select(Transaction).where(
                                Transaction.mpesa_receipt_number == parsed_data["mpesa_receipt_number"]
                            )
                        )
                        existing_transaction = existing_transaction.scalar_one_or_none()
                        
                        if existing_transaction:
                            # Update existing transaction
                            for key, value in parsed_data.items():
                                if key not in ["mpesa_receipt_number"]:  # Don't update receipt number
                                    setattr(existing_transaction, key, value)
                            updated_transactions += 1
                        else:
                            # Create new transaction
                            # First, find or create customer
                            customer = await self.customer_service.find_or_create_customer(
                                merchant_id=self.merchant_id,
                                phone=parsed_data["customer_phone"],
                                name=parsed_data.get("customer_name")
                            )
                            
                            # Create transaction
                            transaction = Transaction(
                                merchant_id=self.merchant_id,
                                customer_id=customer.id,
                                **parsed_data
                            )
                            self.db.add(transaction)
                            new_transactions += 1
                            total_amount += parsed_data["amount"]
                            
                    except Exception as e:
                        logger.error(f"Error processing transaction {transaction_data.get('id')}: {str(e)}")
                        continue
                
                # Check if there are more pages
                if len(transactions) < 100:  # Assuming 100 is the page limit
                    break
                page += 1
                
                # Add small delay to avoid rate limiting
                await asyncio.sleep(0.1)
            
            # Update merchant's last sync time
            merchant.last_sync_at = end_date
            
            # Commit all changes
            await self.db.commit()
            
            logger.info(f"Sync completed: {new_transactions} new, {updated_transactions} updated")
            
            return {
                "new_transactions": new_transactions,
                "updated_transactions": updated_transactions,
                "total_amount": total_amount,
                "sync_period_start": start_date,
                "sync_period_end": end_date
            }
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Transaction sync failed for merchant {self.merchant_id}: {str(e)}")
            raise DarajaAPIError(f"Sync failed: {str(e)}")

    async def setup_webhook(self, webhook_url: str) -> Dict[str, Any]:
        """Setup webhook for real-time transaction notifications (simplified for Daraja)"""
        merchant = await self._load_merchant_credentials()
        
        payload = {
            "till_number": merchant.mpesa_till_number,
            "webhook_url": webhook_url,
            "events": ["transaction.created", "transaction.updated"]
        }
        
        return await self._make_request("POST", "/webhooks", json=payload)

    async def validate_webhook_signature(self, payload: str, signature: str) -> bool:
        """Validate webhook signature for security (placeholder for Daraja)"""
        # Daraja webhooks have specific validation mechanisms (e.g., security credentials, IP whitelisting)
        # This is a placeholder - implement according to Daraja's documentation
        return True

    async def process_webhook_transaction(self, webhook_data: Dict[str, Any]) -> Optional[Transaction]:
        """Process incoming webhook transaction data (simplified for Daraja)"""
        try:
            transaction_data = webhook_data.get("data", {})
            till_number = transaction_data.get("till_number")
            
            # Find merchant by till number
            merchant = await self.db.execute(
                select(Merchant).where(Merchant.mpesa_till_number == till_number)
            )
            merchant = merchant.scalar_one_or_none()
            
            if not merchant:
                logger.warning(f"Webhook received for unknown till number: {till_number}")
                return None
            
            # Re-initialize DarajaService with the correct merchant_id for parsing
            daraja_service_for_parsing = DarajaService(self.db, merchant.id)

            # Parse transaction data
            parsed_data = daraja_service_for_parsing._parse_daraja_transaction(transaction_data)
            
            # Check if transaction already exists
            existing_transaction = await self.db.execute(
                select(Transaction).where(
                    Transaction.mpesa_receipt_number == parsed_data["mpesa_receipt_number"]
                )
            )
            existing_transaction = existing_transaction.scalar_one_or_none()
            
            if existing_transaction:
                # Update existing transaction
                for key, value in parsed_data.items():
                    if key not in ["mpesa_receipt_number"]:
                        setattr(existing_transaction, key, value)
                await self.db.commit()
                return existing_transaction
            else:
                # Create new transaction
                customer = await self.customer_service.find_or_create_customer(
                    merchant_id=merchant.id,
                    phone=parsed_data["customer_phone"],
                    name=parsed_data.get("customer_name")
                )
                
                transaction = Transaction(
                    merchant_id=merchant.id,
                    customer_id=customer.id,
                    **parsed_data
                )
                self.db.add(transaction)
                await self.db.commit()
                await self.db.refresh(transaction)
                
                logger.info(f"New transaction created from webhook: {transaction.mpesa_receipt_number}")
                return transaction
                
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error processing webhook transaction: {str(e)}")
            raise DarajaAPIError(f"Webhook processing failed: {str(e)}")

    async def get_merchant_balance(self, till_number: str) -> Dict[str, Any]:
        """Get current balance for a merchant's till (simplified for Daraja)"""
        return await self._make_request("GET", f"/merchants/{till_number}/balance")

    async def get_transaction_analytics(
        self, 
        till_number: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get transaction analytics from Daraja (simplified)"""
        params = {
            "till_number": till_number,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        return await self._make_request("GET", "/analytics/transactions", params=params)