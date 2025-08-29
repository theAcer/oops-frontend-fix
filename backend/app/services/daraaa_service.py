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

logger = logging.getLogger(__name__)

class DaraaaAPIError(Exception):
    """Custom exception for Daraaa API errors"""
    pass

class DaraaaService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.base_url = settings.DARAAA_API_URL
        self.api_key = settings.DARAAA_API_KEY
        self.customer_service = CustomerService(db)
        
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make authenticated request to Daraaa API"""
        if not self.api_key:
            raise DaraaaAPIError("Daraaa API key not configured")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
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
                logger.error(f"Daraaa API HTTP error: {e.response.status_code} - {e.response.text}")
                raise DaraaaAPIError(f"API request failed: {e.response.status_code}")
            except httpx.RequestError as e:
                logger.error(f"Daraaa API request error: {str(e)}")
                raise DaraaaAPIError(f"Request failed: {str(e)}")

    async def get_merchant_transactions(
        self, 
        till_number: str, 
        start_date: datetime, 
        end_date: datetime,
        page: int = 1,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Fetch transactions for a specific till number"""
        params = {
            "till_number": till_number,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "page": page,
            "limit": limit
        }
        
        return await self._make_request("GET", "/transactions", params=params)

    async def get_transaction_details(self, transaction_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific transaction"""
        return await self._make_request("GET", f"/transactions/{transaction_id}")

    async def verify_till_number(self, till_number: str) -> Dict[str, Any]:
        """Verify if a till number is valid and accessible"""
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

    def _parse_daraaa_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Daraaa transaction data into our format"""
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
            "daraaa_transaction_id": transaction_data.get("id"),
            "raw_daraaa_data": json.dumps(transaction_data)
        }

    async def sync_merchant_transactions(
        self, 
        merchant_id: int, 
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Sync transactions for a merchant from Daraaa API"""
        # Get merchant
        merchant = await self.db.execute(
            select(Merchant).where(Merchant.id == merchant_id)
        )
        merchant = merchant.scalar_one_or_none()
        
        if not merchant:
            raise ValueError(f"Merchant {merchant_id} not found")

        # Calculate date range
        end_date = datetime.utcnow()
        start_date = merchant.last_sync_at or (end_date - timedelta(days=days_back))
        
        logger.info(f"Syncing transactions for merchant {merchant_id} from {start_date} to {end_date}")
        
        new_transactions = 0
        updated_transactions = 0
        total_amount = 0.0
        page = 1
        
        try:
            while True:
                # Fetch transactions from Daraaa API
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
                        parsed_data = self._parse_daraaa_transaction(transaction_data)
                        
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
                                merchant_id=merchant_id,
                                phone=parsed_data["customer_phone"],
                                name=parsed_data.get("customer_name")
                            )
                            
                            # Create transaction
                            transaction = Transaction(
                                merchant_id=merchant_id,
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
            logger.error(f"Transaction sync failed for merchant {merchant_id}: {str(e)}")
            raise DaraaaAPIError(f"Sync failed: {str(e)}")

    async def setup_webhook(self, merchant_id: int, webhook_url: str) -> Dict[str, Any]:
        """Setup webhook for real-time transaction notifications"""
        merchant = await self.db.execute(
            select(Merchant).where(Merchant.id == merchant_id)
        )
        merchant = merchant.scalar_one_or_none()
        
        if not merchant:
            raise ValueError(f"Merchant {merchant_id} not found")
        
        payload = {
            "till_number": merchant.mpesa_till_number,
            "webhook_url": webhook_url,
            "events": ["transaction.created", "transaction.updated"]
        }
        
        return await self._make_request("POST", "/webhooks", json=payload)

    async def validate_webhook_signature(self, payload: str, signature: str) -> bool:
        """Validate webhook signature for security"""
        # Implementation depends on Daraaa's webhook signature method
        # This is a placeholder - implement according to Daraaa's documentation
        return True

    async def process_webhook_transaction(self, webhook_data: Dict[str, Any]) -> Optional[Transaction]:
        """Process incoming webhook transaction data"""
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
            
            # Parse transaction data
            parsed_data = self._parse_daraaa_transaction(transaction_data)
            
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
            raise DaraaaAPIError(f"Webhook processing failed: {str(e)}")

    async def get_merchant_balance(self, till_number: str) -> Dict[str, Any]:
        """Get current balance for a merchant's till"""
        return await self._make_request("GET", f"/merchants/{till_number}/balance")

    async def get_transaction_analytics(
        self, 
        till_number: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get transaction analytics from Daraaa"""
        params = {
            "till_number": till_number,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        return await self._make_request("GET", "/analytics/transactions", params=params)
