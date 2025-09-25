"""
Tests for M-Pesa Configuration Management
"""

import pytest
import os
from unittest.mock import patch

from app.services.mpesa.config import MpesaConfig, MpesaEnvironment
from app.services.mpesa.exceptions import ConfigurationError


class TestMpesaConfig:
    """Test M-Pesa configuration management"""
    
    def test_config_creation_with_required_fields(self):
        """Test creating config with required fields"""
        config = MpesaConfig(
            consumer_key="test_key",
            consumer_secret="test_secret"
        )
        
        assert config.consumer_key == "test_key"
        assert config.consumer_secret == "test_secret"
        assert config.environment == MpesaEnvironment.SANDBOX
        assert config.timeout == 30
        assert config.max_retries == 3
    
    def test_config_creation_with_custom_values(self):
        """Test creating config with custom values"""
        config = MpesaConfig(
            consumer_key="test_key",
            consumer_secret="test_secret",
            environment=MpesaEnvironment.PRODUCTION,
            timeout=60,
            max_retries=5,
            retry_delay=2.0,
            token_cache_ttl=7200
        )
        
        assert config.environment == MpesaEnvironment.PRODUCTION
        assert config.timeout == 60
        assert config.max_retries == 5
        assert config.retry_delay == 2.0
        assert config.token_cache_ttl == 7200
    
    def test_config_validation_missing_consumer_key(self):
        """Test config validation with missing consumer key"""
        with pytest.raises(ValueError, match="consumer_key and consumer_secret are required"):
            MpesaConfig(
                consumer_key="",
                consumer_secret="test_secret"
            )
    
    def test_config_validation_missing_consumer_secret(self):
        """Test config validation with missing consumer secret"""
        with pytest.raises(ValueError, match="consumer_key and consumer_secret are required"):
            MpesaConfig(
                consumer_key="test_key",
                consumer_secret=""
            )
    
    def test_config_validation_invalid_timeout(self):
        """Test config validation with invalid timeout"""
        with pytest.raises(ValueError, match="timeout must be positive"):
            MpesaConfig(
                consumer_key="test_key",
                consumer_secret="test_secret",
                timeout=0
            )
    
    def test_config_validation_invalid_max_retries(self):
        """Test config validation with invalid max retries"""
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            MpesaConfig(
                consumer_key="test_key",
                consumer_secret="test_secret",
                max_retries=-1
            )
    
    def test_config_validation_invalid_token_cache_ttl(self):
        """Test config validation with invalid token cache TTL"""
        with pytest.raises(ValueError, match="token_cache_ttl must be positive"):
            MpesaConfig(
                consumer_key="test_key",
                consumer_secret="test_secret",
                token_cache_ttl=0
            )
    
    def test_base_url_sandbox(self):
        """Test base URL for sandbox environment"""
        config = MpesaConfig(
            consumer_key="test_key",
            consumer_secret="test_secret",
            environment=MpesaEnvironment.SANDBOX
        )
        
        assert config.base_url == "https://sandbox.safaricom.co.ke"
    
    def test_base_url_production(self):
        """Test base URL for production environment"""
        config = MpesaConfig(
            consumer_key="test_key",
            consumer_secret="test_secret",
            environment=MpesaEnvironment.PRODUCTION
        )
        
        assert config.base_url == "https://api.safaricom.co.ke"
    
    def test_oauth_url(self):
        """Test OAuth URL generation"""
        config = MpesaConfig(
            consumer_key="test_key",
            consumer_secret="test_secret"
        )
        
        expected_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        assert config.oauth_url == expected_url
    
    @patch.dict(os.environ, {
        "MPESA_CONSUMER_KEY": "env_key",
        "MPESA_CONSUMER_SECRET": "env_secret",
        "MPESA_ENVIRONMENT": "production",
        "MPESA_TIMEOUT": "45",
        "MPESA_MAX_RETRIES": "2"
    })
    def test_from_env_with_all_variables(self):
        """Test creating config from environment variables"""
        config = MpesaConfig.from_env()
        
        assert config.consumer_key == "env_key"
        assert config.consumer_secret == "env_secret"
        assert config.environment == MpesaEnvironment.PRODUCTION
        assert config.timeout == 45
        assert config.max_retries == 2
    
    @patch.dict(os.environ, {
        "MPESA_CONSUMER_KEY": "env_key",
        "MPESA_CONSUMER_SECRET": "env_secret"
    })
    def test_from_env_with_defaults(self):
        """Test creating config from environment with defaults"""
        config = MpesaConfig.from_env()
        
        assert config.consumer_key == "env_key"
        assert config.consumer_secret == "env_secret"
        assert config.environment == MpesaEnvironment.SANDBOX
        assert config.timeout == 30
        assert config.max_retries == 3
    
    @patch.dict(os.environ, {
        "CUSTOM_CONSUMER_KEY": "custom_key",
        "CUSTOM_CONSUMER_SECRET": "custom_secret"
    })
    def test_from_env_with_custom_prefix(self):
        """Test creating config from environment with custom prefix"""
        config = MpesaConfig.from_env(prefix="CUSTOM_")
        
        assert config.consumer_key == "custom_key"
        assert config.consumer_secret == "custom_secret"
    
    def test_from_env_missing_required_variables(self):
        """Test creating config from environment with missing variables"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(KeyError):
                MpesaConfig.from_env()
    
    def test_for_testing(self):
        """Test creating config for testing"""
        config = MpesaConfig.for_testing()
        
        assert config.consumer_key == "test_consumer_key"
        assert config.consumer_secret == "test_consumer_secret"
        assert config.environment == MpesaEnvironment.SANDBOX
        assert config.timeout == 5  # Shorter for tests
        assert config.max_retries == 1  # Fewer retries for tests
        assert config.retry_delay == 0.1  # Faster retries for tests
        assert config.token_cache_ttl == 60  # Shorter cache for tests
        assert config.enable_request_logging is False  # Reduce test noise
    
    def test_config_immutability(self):
        """Test that config is immutable"""
        config = MpesaConfig(
            consumer_key="test_key",
            consumer_secret="test_secret"
        )
        
        # Should not be able to modify attributes
        with pytest.raises(AttributeError):
            config.consumer_key = "new_key"
        
        with pytest.raises(AttributeError):
            config.timeout = 60


class TestMpesaEnvironment:
    """Test M-Pesa environment enum"""
    
    def test_environment_values(self):
        """Test environment enum values"""
        assert MpesaEnvironment.SANDBOX.value == "sandbox"
        assert MpesaEnvironment.PRODUCTION.value == "production"
    
    def test_environment_from_string(self):
        """Test creating environment from string"""
        sandbox = MpesaEnvironment("sandbox")
        production = MpesaEnvironment("production")
        
        assert sandbox == MpesaEnvironment.SANDBOX
        assert production == MpesaEnvironment.PRODUCTION
    
    def test_invalid_environment(self):
        """Test invalid environment value"""
        with pytest.raises(ValueError):
            MpesaEnvironment("invalid")
