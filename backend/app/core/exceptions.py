"""
Custom exception classes for the Zidisha Loyalty Platform.

This module defines custom exceptions used throughout the application
for better error handling and more specific error reporting.
"""

from typing import Any, Dict, Optional


class ZidishaBaseException(Exception):
    """Base exception class for all Zidisha-specific exceptions."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(ZidishaBaseException):
    """
    Raised when input validation fails.
    
    This exception is used when user input or data doesn't meet
    the required validation criteria.
    """
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.field = field
        super().__init__(message, details)


class NotFoundError(ZidishaBaseException):
    """
    Raised when a requested resource is not found.
    
    This exception is used when trying to access a resource
    (merchant, channel, customer, etc.) that doesn't exist.
    """
    
    def __init__(self, resource_type: str, resource_id: Any, details: Optional[Dict[str, Any]] = None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(message, details)


class BusinessLogicError(ZidishaBaseException):
    """
    Raised when business logic rules are violated.
    
    This exception is used when an operation violates business rules
    or constraints that are not simple validation errors.
    """
    
    def __init__(self, message: str, operation: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.operation = operation
        super().__init__(message, details)


class AuthenticationError(ZidishaBaseException):
    """
    Raised when authentication fails.
    
    This exception is used when user authentication fails
    or when authentication credentials are invalid.
    """
    pass


class AuthorizationError(ZidishaBaseException):
    """
    Raised when authorization fails.
    
    This exception is used when a user doesn't have permission
    to perform a requested operation.
    """
    
    def __init__(self, message: str, user_id: Optional[Any] = None, resource: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        self.user_id = user_id
        self.resource = resource
        super().__init__(message, details)


class ExternalServiceError(ZidishaBaseException):
    """
    Raised when external service calls fail.
    
    This exception is used when calls to external APIs
    (M-Pesa, SMS, etc.) fail or return errors.
    """
    
    def __init__(self, service_name: str, message: str, status_code: Optional[int] = None, 
                 response_data: Optional[Dict[str, Any]] = None, details: Optional[Dict[str, Any]] = None):
        self.service_name = service_name
        self.status_code = status_code
        self.response_data = response_data or {}
        full_message = f"{service_name} error: {message}"
        super().__init__(full_message, details)


class MpesaError(ExternalServiceError):
    """
    Raised when M-Pesa API calls fail.
    
    This is a specialized exception for M-Pesa-specific errors.
    """
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.error_code = error_code
        super().__init__("M-Pesa API", message, status_code, response_data, details)


class DatabaseError(ZidishaBaseException):
    """
    Raised when database operations fail.
    
    This exception is used when database operations fail
    due to connection issues, constraint violations, etc.
    """
    
    def __init__(self, message: str, operation: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        self.operation = operation
        super().__init__(message, details)


class ConfigurationError(ZidishaBaseException):
    """
    Raised when configuration is invalid or missing.
    
    This exception is used when required configuration
    is missing or invalid.
    """
    
    def __init__(self, message: str, config_key: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        self.config_key = config_key
        super().__init__(message, details)


class RateLimitError(ZidishaBaseException):
    """
    Raised when rate limits are exceeded.
    
    This exception is used when API rate limits or
    other throttling limits are exceeded.
    """
    
    def __init__(self, message: str, limit_type: Optional[str] = None, 
                 retry_after: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        self.limit_type = limit_type
        self.retry_after = retry_after
        super().__init__(message, details)


class EncryptionError(ZidishaBaseException):
    """
    Raised when encryption/decryption operations fail.
    
    This exception is used when credential encryption
    or decryption fails.
    """
    
    def __init__(self, message: str, operation: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        self.operation = operation
        super().__init__(message, details)


class LoyaltyProgramError(BusinessLogicError):
    """
    Raised when loyalty program operations fail.
    
    This is a specialized business logic error for
    loyalty program-specific issues.
    """
    
    def __init__(self, message: str, program_id: Optional[Any] = None, 
                 customer_id: Optional[Any] = None, details: Optional[Dict[str, Any]] = None):
        self.program_id = program_id
        self.customer_id = customer_id
        super().__init__(message, "loyalty_program", details)


class TransactionError(BusinessLogicError):
    """
    Raised when transaction processing fails.
    
    This is a specialized business logic error for
    transaction-specific issues.
    """
    
    def __init__(self, message: str, transaction_id: Optional[Any] = None, 
                 transaction_type: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.transaction_id = transaction_id
        self.transaction_type = transaction_type
        super().__init__(message, "transaction_processing", details)


# Exception mapping for HTTP status codes
EXCEPTION_STATUS_MAP = {
    ValidationError: 400,
    NotFoundError: 404,
    AuthenticationError: 401,
    AuthorizationError: 403,
    BusinessLogicError: 422,
    ExternalServiceError: 502,
    MpesaError: 502,
    DatabaseError: 500,
    ConfigurationError: 500,
    RateLimitError: 429,
    EncryptionError: 500,
    LoyaltyProgramError: 422,
    TransactionError: 422,
    ZidishaBaseException: 500,
}


def get_http_status_code(exception: Exception) -> int:
    """
    Get the appropriate HTTP status code for an exception.
    
    Args:
        exception: The exception to get status code for
        
    Returns:
        HTTP status code (default: 500)
    """
    return EXCEPTION_STATUS_MAP.get(type(exception), 500)


def format_error_response(exception: Exception) -> Dict[str, Any]:
    """
    Format an exception into a standardized error response.
    
    Args:
        exception: The exception to format
        
    Returns:
        Dictionary containing error details
    """
    if isinstance(exception, ZidishaBaseException):
        response = {
            "error": type(exception).__name__,
            "message": exception.message,
            "details": exception.details
        }
        
        # Add specific fields for certain exception types
        if isinstance(exception, ValidationError) and exception.field:
            response["field"] = exception.field
        elif isinstance(exception, NotFoundError):
            response["resource_type"] = exception.resource_type
            response["resource_id"] = exception.resource_id
        elif isinstance(exception, ExternalServiceError):
            response["service"] = exception.service_name
            if exception.status_code:
                response["service_status_code"] = exception.status_code
        elif isinstance(exception, MpesaError) and exception.error_code:
            response["mpesa_error_code"] = exception.error_code
            
        return response
    else:
        # Handle standard Python exceptions
        return {
            "error": type(exception).__name__,
            "message": str(exception),
            "details": {}
        }
