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
from datetime import datetime

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
        
        # Daraja credentials are now optional on Merchant, as they might move to Till in future
        # For now, we'll check if they exist for DarajaService to function
        if not merchant.daraja_consumer_key or not merchant.daraja_consumer_secret or not merchant.daraja_shortcode or not merchant.daraja_passkey:
            logger.warning(f"Daraja API credentials not fully configured for merchant {self.merchant_id}. Some Daraja features may not work.")
            # We won't raise an error here, but allow partial functionality if needed.
            # Specific Daraja API calls will fail if credentials are truly missing.
            
        self._merchant_credentials = merchant
        return merchant

    async def _get_access_token(self, merchant: Merchant) -> str:
        """Get Daraja API access token using consumer key and secret."""
        consumer_key = merchant.daraja_consumer_key
        consumer_secret = merchant.daraja_consumer_secret
        
        if not consumer_key or not consumer_secret:
            raise DarajaAPIError("Daraja consumer key or secret not configured for this merchant.")

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
        """Normalize phone number to standard format for Kenya (+254)"""
        # Remove any non-digit characters
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Handle Kenyan phone numbers
        if clean_phone.startswith('254'):
            return clean_phone
        elif clean_phone.startswith('0'):
            return '254' + clean_phone[1:]
        elif len(clean_phone) == 9: # Assuming 9-digit numbers are missing '0' prefix
            return '254' + clean_phone
        
        return clean_phone # Return as is if it doesn't match known patterns

    def _parse_daraja_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Daraja transaction data into our format"""
        # This parsing logic might need to be adjusted based on actual Daraja webhook/API response format
        # Assuming the webhook data structure from the original DaraaaService
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

    # --- C2B (Register URLs, Validation, Confirmation) ---

    async def register_c2b_urls(
        self,
        shortcode: str,
        confirmation_url: str,
        validation_url: str,
        response_type: str = "Completed",
    ) -> Dict[str, Any]:
        """Register C2B Confirmation and Validation URLs for a shortcode."""
        payload = {
            "ShortCode": shortcode,
            "ResponseType": response_type,
            "ConfirmationURL": confirmation_url,
            "ValidationURL": validation_url,
        }
        return await self._make_request("POST", "/mpesa/c2b/v1/registerurl", json=payload)

    def _parse_c2b_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Map C2B confirmation/validation payload to our transaction shape."""
        trans_time = payload.get("TransTime")
        # TransTime is YYYYMMDDHHMMSS
        paid_at = None
        try:
            if trans_time:
                paid_at = datetime.strptime(trans_time, "%Y%m%d%H%M%S")
        except Exception:
            paid_at = None

        customer_name = " ".join(
            [
                n for n in [payload.get("FirstName"), payload.get("MiddleName"), payload.get("LastName")] if n
            ]
        ) or None

        return {
            "mpesa_receipt_number": payload.get("TransID"),
            "mpesa_transaction_id": payload.get("TransID"),
            "till_number": payload.get("BusinessShortCode"),
            "amount": float(payload.get("TransAmount", 0) or 0),
            "customer_phone": self._normalize_phone_number(payload.get("MSISDN", "")),
            "customer_name": customer_name,
            "transaction_date": paid_at or datetime.utcnow(),
            "reference": payload.get("BillRefNumber"),
            "description": payload.get("TransactionType"),
            "raw_daraaa_data": json.dumps(payload),
        }

    async def handle_c2b_confirmation(self, payload: Dict[str, Any]) -> Optional[Transaction]:
        """Persist a C2B confirmation into our transactions table (idempotent by TransID)."""
        try:
            parsed = self._parse_c2b_payload(payload)

            # Find merchant by shortcode
            merchant_result = await self.db.execute(
                select(Merchant).where(Merchant.mpesa_till_number == parsed["till_number"])
            )
            merchant = merchant_result.scalar_one_or_none()
            if not merchant:
                logger.warning(f"C2B confirmation for unknown shortcode: {parsed['till_number']}")
                return None

            # Idempotency on receipt number
            existing_q = await self.db.execute(
                select(Transaction).where(Transaction.mpesa_receipt_number == parsed["mpesa_receipt_number"]) 
            )
            existing = existing_q.scalar_one_or_none()
            if existing:
                # Update minimal fields if needed
                for k, v in parsed.items():
                    if k != "mpesa_receipt_number":
                        setattr(existing, k, v)
                await self.db.commit()
                await self.db.refresh(existing)
                return existing

            # Create customer
            customer = await self.customer_service.find_or_create_customer(
                merchant_id=merchant.id,
                phone=parsed["customer_phone"],
                name=parsed.get("customer_name"),
            )

            # Create transaction
            tx = Transaction(
                merchant_id=merchant.id,
                customer_id=customer.id,
                **parsed,
            )
            self.db.add(tx)
            await self.db.commit()
            await self.db.refresh(tx)

            # Update metrics
            await self.customer_service.update_customer_metrics(customer.id)

            return tx
        except Exception as e:
            await self.db.rollback()
            logger.error(f"C2B confirmation handling failed: {str(e)}")
            raise

    async def handle_c2b_validation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a pending C2B transaction. Accept all by default."""
        # Example: enforce BillRefNumber existence for PayBill shortcodes
        bill_ref = payload.get("BillRefNumber")
        if bill_ref is None:
            return {"ResultCode": "C2B00012", "ResultDesc": "Rejected"}
        return {"ResultCode": "0", "ResultDesc": "Accepted", "ThirdPartyTransID": payload.get("TransID")}

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
                            await self.db.commit() # Commit updates
                            await self.db.refresh(existing_transaction)
                            updated_transactions += 1
                            
                            # Update customer metrics
                            if existing_transaction.customer_id:
                                await self.customer_service.update_customer_metrics(existing_transaction.customer_id)

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
                            await self.db.commit() # Commit new transaction
                            await self.db.refresh(transaction)
                            new_transactions += 1
                            total_amount += parsed_data["amount"]
                            
                            # Update customer metrics
                            await self.customer_service.update_customer_metrics(customer.id)
                            
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
            
            # Commit final merchant update
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
            merchant_result = await self.db.execute(
                select(Merchant).where(Merchant.mpesa_till_number == till_number)
            )
            merchant = merchant_result.scalar_one_or_none()
            
            if not merchant:
                logger.warning(f"Webhook received for unknown till number: {till_number}")
                return None
            
            # Re-initialize DarajaService with the correct merchant_id for parsing
            # This ensures the correct merchant context for _parse_daraja_transaction
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
                await self.db.refresh(existing_transaction)
                
                # Update customer metrics
                if existing_transaction.customer_id:
                    await self.customer_service.update_customer_metrics(existing_transaction.customer_id)

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
                
                # Update customer metrics
                await self.customer_service.update_customer_metrics(customer.id)

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