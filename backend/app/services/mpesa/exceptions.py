"""
M-Pesa Service Exceptions

Comprehensive exception hierarchy for M-Pesa API operations.
"""

from typing import Optional, Dict, Any


class MpesaAPIError(Exception):
    """Base exception for all M-Pesa API errors"""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        self.request_id = request_id
    
    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        return " | ".join(parts)


class AuthenticationError(MpesaAPIError):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, **kwargs)


class ValidationError(MpesaAPIError):
    """Raised when request validation fails"""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.field = field


class RateLimitError(MpesaAPIError):
    """Raised when rate limit is exceeded"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class NetworkError(MpesaAPIError):
    """Raised when network/connectivity issues occur"""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.original_error = original_error


class TimeoutError(NetworkError):
    """Raised when request times out"""
    
    def __init__(self, message: str = "Request timed out", **kwargs):
        super().__init__(message, **kwargs)


class ConfigurationError(MpesaAPIError):
    """Raised when configuration is invalid"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, **kwargs)


class BusinessLogicError(MpesaAPIError):
    """Raised when business logic validation fails"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.error_code = error_code


class InsufficientFundsError(BusinessLogicError):
    """Raised when transaction fails due to insufficient funds"""
    
    def __init__(self, message: str = "Insufficient funds", **kwargs):
        super().__init__(message, error_code="INSUFFICIENT_FUNDS", **kwargs)


class InvalidPhoneNumberError(ValidationError):
    """Raised when phone number format is invalid"""
    
    def __init__(self, phone_number: str, **kwargs):
        message = f"Invalid phone number format: {phone_number}"
        super().__init__(message, field="phone_number", **kwargs)
        self.phone_number = phone_number


class TransactionNotFoundError(BusinessLogicError):
    """Raised when transaction cannot be found"""
    
    def __init__(self, transaction_id: str, **kwargs):
        message = f"Transaction not found: {transaction_id}"
        super().__init__(message, error_code="TRANSACTION_NOT_FOUND", **kwargs)
        self.transaction_id = transaction_id


# Exception mapping for HTTP status codes
STATUS_CODE_EXCEPTIONS = {
    400: ValidationError,
    401: AuthenticationError,
    403: AuthenticationError,
    404: BusinessLogicError,
    429: RateLimitError,
    500: MpesaAPIError,
    502: NetworkError,
    503: NetworkError,
    504: TimeoutError,
}


def create_exception_from_response(
    status_code: int,
    response_data: Dict[str, Any],
    default_message: str = "M-Pesa API error"
) -> MpesaAPIError:
    """
    Create appropriate exception from HTTP response.
    
    Args:
        status_code: HTTP status code
        response_data: Response JSON data
        default_message: Default error message
        
    Returns:
        Appropriate MpesaAPIError subclass
    """
    # Extract error message from response
    message = (
        response_data.get("errorMessage") or
        response_data.get("message") or
        response_data.get("ResponseDescription") or
        default_message
    )
    
    # Get exception class for status code
    exception_class = STATUS_CODE_EXCEPTIONS.get(status_code, MpesaAPIError)
    
    # Create exception with response context
    return exception_class(
        message=message,
        status_code=status_code,
        response_data=response_data,
        request_id=response_data.get("requestId")
    )
