"""
Security utilities for the Zidisha Loyalty Platform

Handles encryption/decryption of sensitive data like M-Pesa credentials.
"""

import os
import base64
import secrets
import string
import bcrypt
import logging
from jose import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.merchant import Merchant
from app.core.config import settings
from app.core.database import get_db

logger = logging.getLogger(__name__)


class SecurityManager:
    """Manages encryption and decryption of sensitive data"""
    
    def __init__(self):
        self._fernet: Optional[Fernet] = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption with key from environment"""
        # Get encryption key from environment or generate one
        encryption_key = os.environ.get("ENCRYPTION_KEY")
        
        if not encryption_key:
            # Generate a key for development (NOT for production!)
            logger.warning("No ENCRYPTION_KEY found in environment. Generating temporary key for development.")
            encryption_key = Fernet.generate_key().decode()
            logger.warning(f"Generated encryption key: {encryption_key}")
            logger.warning("Please set ENCRYPTION_KEY environment variable for production!")
        
        # If key is a password, derive the actual key
        if len(encryption_key) != 44:  # Fernet keys are 44 characters when base64 encoded
            # Derive key from password
            password = encryption_key.encode()
            salt = b'zidisha_loyalty_salt'  # In production, use a random salt stored securely
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
        else:
            key = encryption_key.encode()
        
        self._fernet = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        if not data:
            return ""
        
        try:
            encrypted_data = self._fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise ValueError("Failed to encrypt data")
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        if not encrypted_data:
            return ""
        
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self._fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError("Failed to decrypt data")


# Global security manager instance
_security_manager = SecurityManager()


def encrypt_data(data: str) -> str:
    """Encrypt sensitive data"""
    return _security_manager.encrypt(data)


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    return _security_manager.decrypt(encrypted_data)


def generate_encryption_key() -> str:
    """Generate a new encryption key for production use"""
    return Fernet.generate_key().decode()


# Password hashing utilities (for user passwords)

def hash_password(password: str) -> str:
    """Hash a password for storing"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


# API Key generation for webhook authentication

def generate_api_key(length: int = 32) -> str:
    """Generate a secure API key"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_webhook_secret() -> str:
    """Generate a webhook secret for M-Pesa callbacks"""
    return generate_api_key(64)


# JWT Authentication utilities

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception

    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    return user


async def get_current_merchant(current_user: User = Depends(get_current_user)) -> Merchant:
    """Get current merchant from authenticated user"""
    if current_user.merchant_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with a merchant"
        )

    # In a real implementation, you would fetch the merchant from the database
    # For now, we'll create a mock merchant object
    # TODO: Implement proper merchant fetching from database

    class MockMerchant:
        def __init__(self, id: int):
            self.id = id
            self.business_name = "Mock Merchant"
            self.email = current_user.email

    return MockMerchant(current_user.merchant_id)
