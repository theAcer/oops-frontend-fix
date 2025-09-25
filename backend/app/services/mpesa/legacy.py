"""
Legacy M-Pesa Service Compatibility Layer

Provides backward compatibility with existing MpesaService and DarajaService implementations.
"""

from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .factory import MpesaServiceFactory
from .channel import MpesaChannelService
from .transaction import MpesaTransactionService
from .exceptions import MpesaAPIError


class LegacyMpesaService:
    """
    Legacy compatibility wrapper for the original MpesaService.
    
    This class provides the same interface as the original MpesaService
    while using the new unified architecture internally.
    """
    
    def __init__(self, consumer_key: str, consumer_secret: str, environment: str = "sandbox"):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.environment = environment.lower()
        
        # Create new services internally
        self._channel_service = MpesaServiceFactory.create_channel_service(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            environment=environment
        )
        self._transaction_service = MpesaServiceFactory.create_transaction_service(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            environment=environment
        )
    
    async def get_oauth_token(self) -> Optional[str]:
        """Legacy method: Get OAuth access token"""
        try:
            return await self._channel_service.get_access_token()
        except MpesaAPIError:
            return None
    
    async def register_urls(
        self,
        shortcode: str,
        validation_url: str,
        confirmation_url: str,
        response_type: str = "Completed"
    ) -> Optional[Dict[str, Any]]:
        """Legacy method: Register validation and confirmation URLs"""
        try:
            return await self._channel_service.register_urls(
                shortcode=shortcode,
                validation_url=validation_url,
                confirmation_url=confirmation_url,
                response_type=response_type
            )
        except MpesaAPIError:
            return None
    
    async def simulate_c2b_payment(
        self,
        shortcode: str,
        amount: float,
        msisdn: str,
        bill_ref: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Legacy method: Simulate C2B payment"""
        try:
            return await self._transaction_service.simulate_c2b_transaction(
                shortcode=shortcode,
                amount=amount,
                customer_phone=msisdn,
                bill_ref=bill_ref
            )
        except MpesaAPIError:
            return None
    
    async def stk_push(
        self,
        business_shortcode: str,
        amount: float,
        phone_number: str,
        account_reference: str,
        transaction_desc: str,
        callback_url: str,
        passkey: str
    ) -> Optional[Dict[str, Any]]:
        """Legacy method: Initiate STK Push"""
        try:
            return await self._transaction_service.initiate_stk_push(
                business_shortcode=business_shortcode,
                amount=amount,
                customer_phone=phone_number,
                account_reference=account_reference,
                transaction_desc=transaction_desc,
                callback_url=callback_url,
                passkey=passkey
            )
        except MpesaAPIError:
            return None
    
    async def close(self):
        """Close services and cleanup resources"""
        await self._channel_service.close()
        await self._transaction_service.close()


class LegacyDarajaService:
    """
    Legacy compatibility wrapper for the original DarajaService.
    
    This class provides database integration while using the new
    unified M-Pesa services internally.
    """
    
    def __init__(self, db: AsyncSession, merchant_id: int):
        self.db = db
        self.merchant_id = merchant_id
        self._merchant_credentials: Optional[Dict[str, Any]] = None
        self._channel_service: Optional[MpesaChannelService] = None
        self._transaction_service: Optional[MpesaTransactionService] = None
    
    async def _load_merchant_credentials(self) -> Dict[str, Any]:
        """Load merchant credentials from database"""
        if self._merchant_credentials:
            return self._merchant_credentials
        
        # This would typically query the database for merchant credentials
        # For now, return a placeholder implementation
        from sqlalchemy import select
        from app.models.merchant import Merchant
        
        result = await self.db.execute(
            select(Merchant).where(Merchant.id == self.merchant_id)
        )
        merchant = result.scalar_one_or_none()
        
        if not merchant:
            raise ValueError(f"Merchant {self.merchant_id} not found")
        
        # Extract M-Pesa credentials
        credentials = {
            "consumer_key": getattr(merchant, "daraja_consumer_key", None),
            "consumer_secret": getattr(merchant, "daraja_consumer_secret", None),
            "shortcode": getattr(merchant, "daraja_shortcode", None),
            "passkey": getattr(merchant, "daraja_passkey", None),
            "environment": getattr(merchant, "daraja_environment", "sandbox")
        }
        
        # Validate credentials
        if not credentials["consumer_key"] or not credentials["consumer_secret"]:
            raise ValueError(f"M-Pesa credentials not configured for merchant {self.merchant_id}")
        
        self._merchant_credentials = credentials
        return credentials
    
    async def _get_channel_service(self) -> MpesaChannelService:
        """Get channel service with merchant credentials"""
        if not self._channel_service:
            credentials = await self._load_merchant_credentials()
            self._channel_service = MpesaServiceFactory.create_channel_service(
                consumer_key=credentials["consumer_key"],
                consumer_secret=credentials["consumer_secret"],
                environment=credentials["environment"]
            )
        return self._channel_service
    
    async def _get_transaction_service(self) -> MpesaTransactionService:
        """Get transaction service with merchant credentials"""
        if not self._transaction_service:
            credentials = await self._load_merchant_credentials()
            self._transaction_service = MpesaServiceFactory.create_transaction_service(
                consumer_key=credentials["consumer_key"],
                consumer_secret=credentials["consumer_secret"],
                environment=credentials["environment"]
            )
        return self._transaction_service
    
    async def verify_channel(self) -> Optional[Dict[str, Any]]:
        """Verify merchant's M-Pesa channel"""
        try:
            credentials = await self._load_merchant_credentials()
            service = await self._get_channel_service()
            return await service.verify_channel(credentials["shortcode"])
        except Exception as e:
            # Log error but don't raise to maintain legacy behavior
            import logging
            logging.getLogger(__name__).error(f"Channel verification failed: {e}")
            return None
    
    async def register_urls(
        self,
        validation_url: str,
        confirmation_url: str
    ) -> Optional[Dict[str, Any]]:
        """Register URLs for merchant's channel"""
        try:
            credentials = await self._load_merchant_credentials()
            service = await self._get_channel_service()
            return await service.register_urls(
                shortcode=credentials["shortcode"],
                validation_url=validation_url,
                confirmation_url=confirmation_url
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"URL registration failed: {e}")
            return None
    
    async def simulate_payment(
        self,
        amount: float,
        customer_phone: str,
        bill_ref: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Simulate payment for merchant's channel"""
        try:
            credentials = await self._load_merchant_credentials()
            service = await self._get_transaction_service()
            return await service.simulate_c2b_transaction(
                shortcode=credentials["shortcode"],
                amount=amount,
                customer_phone=customer_phone,
                bill_ref=bill_ref
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Payment simulation failed: {e}")
            return None
    
    async def initiate_stk_push(
        self,
        amount: float,
        customer_phone: str,
        account_reference: str,
        transaction_desc: str,
        callback_url: str
    ) -> Optional[Dict[str, Any]]:
        """Initiate STK Push for merchant"""
        try:
            credentials = await self._load_merchant_credentials()
            service = await self._get_transaction_service()
            return await service.initiate_stk_push(
                business_shortcode=credentials["shortcode"],
                amount=amount,
                customer_phone=customer_phone,
                account_reference=account_reference,
                transaction_desc=transaction_desc,
                callback_url=callback_url,
                passkey=credentials["passkey"]
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"STK Push failed: {e}")
            return None
    
    async def close(self):
        """Close services and cleanup resources"""
        if self._channel_service:
            await self._channel_service.close()
        if self._transaction_service:
            await self._transaction_service.close()
