"""
M-Pesa Transaction Service

Handles M-Pesa transaction operations like simulation, status queries, and reversals.
"""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal

from .base import BaseMpesaService
from .config import MpesaConfig
from .exceptions import ValidationError, BusinessLogicError, InsufficientFundsError, InvalidPhoneNumberError
from .protocols import HTTPClient, CacheProvider, LoggerProtocol


class MpesaTransactionService(BaseMpesaService):
    """
    Service for M-Pesa transaction operations.
    
    This service handles:
    - Transaction simulation (C2B)
    - Transaction status queries
    - Transaction reversals
    - Payment requests (STK Push)
    """
    
    def __init__(
        self,
        config: MpesaConfig,
        http_client: Optional[HTTPClient] = None,
        cache: Optional[CacheProvider] = None,
        logger: Optional[LoggerProtocol] = None
    ):
        super().__init__(config, http_client, cache, logger)
    
    def _validate_phone_number(self, phone: str) -> str:
        """
        Validate and format Kenyan phone number.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Formatted phone number (254XXXXXXXXX)
            
        Raises:
            InvalidPhoneNumberError: If phone number is invalid
        """
        if not phone:
            raise InvalidPhoneNumberError("Phone number is required")
        
        # Remove any non-digit characters
        phone = re.sub(r'\D', '', phone)
        
        # Handle different formats
        if phone.startswith('254'):
            # Already in international format
            formatted = phone
        elif phone.startswith('0'):
            # Local format (0XXXXXXXXX)
            formatted = '254' + phone[1:]
        elif len(phone) == 9:
            # Without country code or leading zero
            formatted = '254' + phone
        else:
            raise InvalidPhoneNumberError(phone)
        
        # Validate length and format
        if len(formatted) != 12 or not formatted.startswith('254'):
            raise InvalidPhoneNumberError(phone)
        
        # Validate Kenyan mobile prefixes
        valid_prefixes = ['2547', '2541', '2570', '2571', '2572', '2573', '2574', '2575', '2576', '2577', '2578', '2579']
        if not any(formatted.startswith(prefix) for prefix in valid_prefixes):
            raise InvalidPhoneNumberError(phone)
        
        return formatted
    
    def _validate_amount(self, amount: float) -> Decimal:
        """
        Validate transaction amount.
        
        Args:
            amount: Amount to validate
            
        Returns:
            Validated amount as Decimal
            
        Raises:
            ValidationError: If amount is invalid
        """
        if not isinstance(amount, (int, float, Decimal)):
            raise ValidationError(f"Invalid amount type: {type(amount)}")
        
        amount_decimal = Decimal(str(amount))
        
        if amount_decimal <= 0:
            raise ValidationError("Amount must be positive")
        
        if amount_decimal < Decimal('1'):
            raise ValidationError("Minimum transaction amount is KES 1")
        
        if amount_decimal > Decimal('70000'):
            raise ValidationError("Maximum transaction amount is KES 70,000")
        
        # Check decimal places (max 2)
        if amount_decimal.as_tuple().exponent < -2:
            raise ValidationError("Amount cannot have more than 2 decimal places")
        
        return amount_decimal
    
    async def simulate_c2b_transaction(
        self,
        shortcode: str,
        amount: float,
        customer_phone: str,
        bill_ref: Optional[str] = None,
        command_id: str = "CustomerPayBillOnline"
    ) -> Dict[str, Any]:
        """
        Simulate a Customer-to-Business (C2B) transaction.
        
        Args:
            shortcode: M-Pesa shortcode receiving the payment
            amount: Transaction amount
            customer_phone: Customer's phone number
            bill_ref: Bill reference number (optional)
            command_id: Transaction command ID
            
        Returns:
            Simulation result
            
        Raises:
            ValidationError: If parameters are invalid
            BusinessLogicError: If simulation fails
        """
        # Validate inputs
        if not shortcode or not shortcode.isdigit():
            raise ValidationError(f"Invalid shortcode: {shortcode}")
        
        validated_amount = self._validate_amount(amount)
        validated_phone = self._validate_phone_number(customer_phone)
        
        if command_id not in ("CustomerPayBillOnline", "CustomerBuyGoodsOnline"):
            raise ValidationError(f"Invalid command ID: {command_id}")
        
        self.logger.info(f"Simulating C2B transaction: {validated_amount} from {validated_phone} to {shortcode}")
        
        endpoint = "/mpesa/c2b/v1/simulate"
        
        request_data = {
            "ShortCode": shortcode,
            "CommandID": command_id,
            "Amount": str(validated_amount),
            "Msisdn": validated_phone,
            "BillRefNumber": bill_ref or f"TEST-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        }
        
        try:
            response = await self.make_authenticated_request(
                method="POST",
                endpoint=endpoint,
                json_data=request_data
            )
            
            if response.get("ResponseCode") == "0":
                result = {
                    "status": "success",
                    "transaction_type": "c2b_simulation",
                    "shortcode": shortcode,
                    "amount": str(validated_amount),
                    "customer_phone": validated_phone,
                    "bill_ref": request_data["BillRefNumber"],
                    "command_id": command_id,
                    "response_code": response.get("ResponseCode"),
                    "response_description": response.get("ResponseDescription"),
                    "conversation_id": response.get("ConversationID"),
                    "originator_conversation_id": response.get("OriginatorConversationID"),
                    "simulated_at": datetime.utcnow().isoformat()
                }
                
                self.logger.info(f"C2B simulation successful: {result['conversation_id']}")
                return result
            else:
                raise BusinessLogicError(
                    f"C2B simulation failed: {response.get('ResponseDescription', 'Unknown error')}",
                    error_code=response.get("ResponseCode")
                )
                
        except Exception as e:
            self.logger.error(f"C2B simulation error: {e}")
            raise
    
    async def initiate_stk_push(
        self,
        business_shortcode: str,
        amount: float,
        customer_phone: str,
        account_reference: str,
        transaction_desc: str,
        callback_url: str,
        passkey: str
    ) -> Dict[str, Any]:
        """
        Initiate STK Push (Lipa Na M-Pesa Online) transaction.
        
        Args:
            business_shortcode: Business shortcode
            amount: Transaction amount
            customer_phone: Customer's phone number
            account_reference: Account reference
            transaction_desc: Transaction description
            callback_url: Callback URL for result
            passkey: Lipa Na M-Pesa passkey
            
        Returns:
            STK Push initiation result
        """
        # Validate inputs
        validated_amount = self._validate_amount(amount)
        validated_phone = self._validate_phone_number(customer_phone)
        
        if not business_shortcode or not business_shortcode.isdigit():
            raise ValidationError(f"Invalid business shortcode: {business_shortcode}")
        
        if not account_reference:
            raise ValidationError("Account reference is required")
        
        if not callback_url or not callback_url.startswith(('http://', 'https://')):
            raise ValidationError(f"Invalid callback URL: {callback_url}")
        
        self.logger.info(f"Initiating STK Push: {validated_amount} to {validated_phone}")
        
        # Generate timestamp and password
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        password_string = f"{business_shortcode}{passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode()
        
        endpoint = "/mpesa/stkpush/v1/processrequest"
        
        request_data = {
            "BusinessShortCode": business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": str(validated_amount),
            "PartyA": validated_phone,
            "PartyB": business_shortcode,
            "PhoneNumber": validated_phone,
            "CallBackURL": callback_url,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc
        }
        
        try:
            response = await self.make_authenticated_request(
                method="POST",
                endpoint=endpoint,
                json_data=request_data
            )
            
            if response.get("ResponseCode") == "0":
                result = {
                    "status": "initiated",
                    "transaction_type": "stk_push",
                    "checkout_request_id": response.get("CheckoutRequestID"),
                    "merchant_request_id": response.get("MerchantRequestID"),
                    "response_code": response.get("ResponseCode"),
                    "response_description": response.get("ResponseDescription"),
                    "customer_message": response.get("CustomerMessage"),
                    "amount": str(validated_amount),
                    "customer_phone": validated_phone,
                    "account_reference": account_reference,
                    "initiated_at": datetime.utcnow().isoformat()
                }
                
                self.logger.info(f"STK Push initiated: {result['checkout_request_id']}")
                return result
            else:
                raise BusinessLogicError(
                    f"STK Push failed: {response.get('ResponseDescription', 'Unknown error')}",
                    error_code=response.get("ResponseCode")
                )
                
        except Exception as e:
            self.logger.error(f"STK Push error: {e}")
            raise
    
    async def query_transaction_status(
        self,
        business_shortcode: str,
        checkout_request_id: str,
        passkey: str
    ) -> Dict[str, Any]:
        """
        Query STK Push transaction status.
        
        Args:
            business_shortcode: Business shortcode
            checkout_request_id: Checkout request ID from STK Push
            passkey: Lipa Na M-Pesa passkey
            
        Returns:
            Transaction status
        """
        if not checkout_request_id:
            raise ValidationError("Checkout request ID is required")
        
        self.logger.info(f"Querying transaction status: {checkout_request_id}")
        
        # Generate timestamp and password
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        password_string = f"{business_shortcode}{passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode()
        
        endpoint = "/mpesa/stkpushquery/v1/query"
        
        request_data = {
            "BusinessShortCode": business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }
        
        try:
            response = await self.make_authenticated_request(
                method="POST",
                endpoint=endpoint,
                json_data=request_data
            )
            
            result = {
                "checkout_request_id": checkout_request_id,
                "response_code": response.get("ResponseCode"),
                "response_description": response.get("ResponseDescription"),
                "merchant_request_id": response.get("MerchantRequestID"),
                "result_code": response.get("ResultCode"),
                "result_desc": response.get("ResultDesc"),
                "queried_at": datetime.utcnow().isoformat()
            }
            
            # Add transaction details if successful
            if response.get("ResultCode") == "0":
                result.update({
                    "status": "completed",
                    "mpesa_receipt_number": response.get("MpesaReceiptNumber"),
                    "transaction_date": response.get("TransactionDate"),
                    "amount": response.get("Amount"),
                    "phone_number": response.get("PhoneNumber")
                })
            elif response.get("ResultCode") == "1032":
                result["status"] = "cancelled"
            elif response.get("ResultCode") == "1037":
                result["status"] = "timeout"
            else:
                result["status"] = "failed"
            
            self.logger.info(f"Transaction status query result: {result['status']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Transaction status query error: {e}")
            raise
    
    async def reverse_transaction(
        self,
        initiator: str,
        security_credential: str,
        transaction_id: str,
        amount: float,
        receiver_party: str,
        remarks: str,
        queue_timeout_url: str,
        result_url: str,
        occasion: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Reverse a completed M-Pesa transaction.
        
        Args:
            initiator: API operator username
            security_credential: Encrypted security credential
            transaction_id: M-Pesa transaction ID to reverse
            amount: Amount to reverse
            receiver_party: Organization receiving the reversal
            remarks: Reversal remarks
            queue_timeout_url: Timeout callback URL
            result_url: Result callback URL
            occasion: Optional occasion
            
        Returns:
            Reversal initiation result
        """
        validated_amount = self._validate_amount(amount)
        
        if not transaction_id:
            raise ValidationError("Transaction ID is required")
        
        self.logger.info(f"Initiating transaction reversal: {transaction_id}")
        
        endpoint = "/mpesa/reversal/v1/request"
        
        request_data = {
            "Initiator": initiator,
            "SecurityCredential": security_credential,
            "CommandID": "TransactionReversal",
            "TransactionID": transaction_id,
            "Amount": str(validated_amount),
            "ReceiverParty": receiver_party,
            "RecieverIdentifierType": "11",
            "ResultURL": result_url,
            "QueueTimeOutURL": queue_timeout_url,
            "Remarks": remarks,
            "Occasion": occasion or remarks
        }
        
        try:
            response = await self.make_authenticated_request(
                method="POST",
                endpoint=endpoint,
                json_data=request_data
            )
            
            if response.get("ResponseCode") == "0":
                result = {
                    "status": "initiated",
                    "transaction_type": "reversal",
                    "original_transaction_id": transaction_id,
                    "reversal_amount": str(validated_amount),
                    "conversation_id": response.get("ConversationID"),
                    "originator_conversation_id": response.get("OriginatorConversationID"),
                    "response_code": response.get("ResponseCode"),
                    "response_description": response.get("ResponseDescription"),
                    "initiated_at": datetime.utcnow().isoformat()
                }
                
                self.logger.info(f"Transaction reversal initiated: {result['conversation_id']}")
                return result
            else:
                raise BusinessLogicError(
                    f"Transaction reversal failed: {response.get('ResponseDescription', 'Unknown error')}",
                    error_code=response.get("ResponseCode")
                )
                
        except Exception as e:
            self.logger.error(f"Transaction reversal error: {e}")
            raise
