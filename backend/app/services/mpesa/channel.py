"""
M-Pesa Channel Service

Handles M-Pesa channel-specific operations like verification, URL registration, and configuration.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from .base import BaseMpesaService
from .config import MpesaConfig
from .exceptions import ValidationError, BusinessLogicError
from .protocols import HTTPClient, CacheProvider, LoggerProtocol


class MpesaChannelService(BaseMpesaService):
    """
    Service for M-Pesa channel management operations.
    
    This service handles:
    - Channel verification
    - URL registration for callbacks
    - Channel configuration
    - Status monitoring
    """
    
    def __init__(
        self,
        config: MpesaConfig,
        http_client: Optional[HTTPClient] = None,
        cache: Optional[CacheProvider] = None,
        logger: Optional[LoggerProtocol] = None
    ):
        super().__init__(config, http_client, cache, logger)
    
    async def verify_channel(self, shortcode: str) -> Dict[str, Any]:
        """
        Verify M-Pesa channel credentials and configuration.
        
        Args:
            shortcode: M-Pesa shortcode to verify
            
        Returns:
            Verification result with status and details
            
        Raises:
            ValidationError: If shortcode is invalid
            BusinessLogicError: If verification fails
        """
        if not shortcode or not shortcode.isdigit():
            raise ValidationError(f"Invalid shortcode format: {shortcode}")
        
        self.logger.info(f"Verifying M-Pesa channel: {shortcode}")
        
        # For sandbox, we can use a test endpoint
        # For production, this would be a real verification call
        endpoint = "/mpesa/accountbalance/v1/query"
        
        request_data = {
            "Initiator": "testapi",
            "SecurityCredential": "test_credential",
            "CommandID": "AccountBalance",
            "PartyA": shortcode,
            "IdentifierType": "4",
            "Remarks": "Channel verification",
            "QueueTimeOutURL": f"{self._get_callback_base_url()}/timeout",
            "ResultURL": f"{self._get_callback_base_url()}/result"
        }
        
        try:
            response = await self.make_authenticated_request(
                method="POST",
                endpoint=endpoint,
                json_data=request_data
            )
            
            # Check response for success indicators
            if response.get("ResponseCode") == "0":
                result = {
                    "status": "verified",
                    "shortcode": shortcode,
                    "response_code": response.get("ResponseCode"),
                    "response_description": response.get("ResponseDescription"),
                    "conversation_id": response.get("ConversationID"),
                    "originator_conversation_id": response.get("OriginatorConversationID"),
                    "verified_at": datetime.utcnow().isoformat()
                }
                
                self.logger.info(f"Channel verification successful: {shortcode}")
                return result
            else:
                raise BusinessLogicError(
                    f"Channel verification failed: {response.get('ResponseDescription', 'Unknown error')}",
                    error_code=response.get("ResponseCode")
                )
                
        except Exception as e:
            self.logger.error(f"Channel verification error for {shortcode}: {e}")
            raise
    
    async def register_urls(
        self,
        shortcode: str,
        validation_url: str,
        confirmation_url: str,
        response_type: str = "Completed"
    ) -> Dict[str, Any]:
        """
        Register validation and confirmation URLs for M-Pesa channel.
        
        Args:
            shortcode: M-Pesa shortcode
            validation_url: URL for transaction validation
            confirmation_url: URL for transaction confirmation
            response_type: Response type (Completed or Cancelled)
            
        Returns:
            Registration result
            
        Raises:
            ValidationError: If parameters are invalid
        """
        # Validate inputs
        if not shortcode or not shortcode.isdigit():
            raise ValidationError(f"Invalid shortcode: {shortcode}")
        
        if not validation_url or not validation_url.startswith(('http://', 'https://')):
            raise ValidationError(f"Invalid validation URL: {validation_url}")
        
        if not confirmation_url or not confirmation_url.startswith(('http://', 'https://')):
            raise ValidationError(f"Invalid confirmation URL: {confirmation_url}")
        
        if response_type not in ("Completed", "Cancelled"):
            raise ValidationError(f"Invalid response type: {response_type}")
        
        self.logger.info(f"Registering URLs for shortcode: {shortcode}")
        
        endpoint = "/mpesa/c2b/v1/registerurl"
        
        request_data = {
            "ShortCode": shortcode,
            "ResponseType": response_type,
            "ConfirmationURL": confirmation_url,
            "ValidationURL": validation_url
        }
        
        try:
            response = await self.make_authenticated_request(
                method="POST",
                endpoint=endpoint,
                json_data=request_data
            )
            
            if response.get("ResponseCode") == "0":
                result = {
                    "status": "registered",
                    "shortcode": shortcode,
                    "validation_url": validation_url,
                    "confirmation_url": confirmation_url,
                    "response_type": response_type,
                    "response_code": response.get("ResponseCode"),
                    "response_description": response.get("ResponseDescription"),
                    "registered_at": datetime.utcnow().isoformat()
                }
                
                self.logger.info(f"URL registration successful for shortcode: {shortcode}")
                return result
            else:
                raise BusinessLogicError(
                    f"URL registration failed: {response.get('ResponseDescription', 'Unknown error')}",
                    error_code=response.get("ResponseCode")
                )
                
        except Exception as e:
            self.logger.error(f"URL registration error for {shortcode}: {e}")
            raise
    
    async def get_channel_status(self, shortcode: str) -> Dict[str, Any]:
        """
        Get current status of M-Pesa channel.
        
        Args:
            shortcode: M-Pesa shortcode
            
        Returns:
            Channel status information
        """
        self.logger.info(f"Getting channel status: {shortcode}")
        
        # This would typically involve checking:
        # 1. Account balance
        # 2. URL registration status
        # 3. Recent transaction activity
        # 4. Any error conditions
        
        try:
            # For now, return a basic status check
            # In production, this would make actual API calls
            status = {
                "shortcode": shortcode,
                "status": "active",
                "last_checked": datetime.utcnow().isoformat(),
                "balance_available": True,
                "urls_registered": True,
                "api_accessible": True
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting channel status for {shortcode}: {e}")
            return {
                "shortcode": shortcode,
                "status": "error",
                "error": str(e),
                "last_checked": datetime.utcnow().isoformat()
            }
    
    async def list_registered_urls(self, shortcode: str) -> List[Dict[str, Any]]:
        """
        List all registered URLs for a shortcode.
        
        Args:
            shortcode: M-Pesa shortcode
            
        Returns:
            List of registered URLs
        """
        # This would typically query the M-Pesa API for registered URLs
        # For now, return a placeholder implementation
        
        self.logger.info(f"Listing registered URLs for shortcode: {shortcode}")
        
        # Placeholder implementation
        return [
            {
                "shortcode": shortcode,
                "validation_url": f"https://api.example.com/mpesa/validation/{shortcode}",
                "confirmation_url": f"https://api.example.com/mpesa/confirmation/{shortcode}",
                "response_type": "Completed",
                "registered_at": datetime.utcnow().isoformat()
            }
        ]
    
    def _get_callback_base_url(self) -> str:
        """Get base URL for callbacks based on environment"""
        # This should come from configuration
        if self.config.environment.value == "sandbox":
            return "https://api-sandbox.example.com/mpesa/callbacks"
        else:
            return "https://api.example.com/mpesa/callbacks"
    
    async def validate_channel_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate channel configuration data.
        
        Args:
            config_data: Channel configuration to validate
            
        Returns:
            Validation result
            
        Raises:
            ValidationError: If configuration is invalid
        """
        errors = []
        
        # Required fields
        required_fields = ["shortcode", "channel_type", "environment"]
        for field in required_fields:
            if not config_data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate shortcode format
        shortcode = config_data.get("shortcode")
        if shortcode and not shortcode.isdigit():
            errors.append(f"Invalid shortcode format: {shortcode}")
        
        # Validate channel type
        channel_type = config_data.get("channel_type")
        if channel_type and channel_type not in ("paybill", "till", "buygoods"):
            errors.append(f"Invalid channel type: {channel_type}")
        
        # Validate environment
        environment = config_data.get("environment")
        if environment and environment not in ("sandbox", "production"):
            errors.append(f"Invalid environment: {environment}")
        
        if errors:
            raise ValidationError(f"Configuration validation failed: {'; '.join(errors)}")
        
        return {
            "status": "valid",
            "validated_at": datetime.utcnow().isoformat(),
            "config": config_data
        }
