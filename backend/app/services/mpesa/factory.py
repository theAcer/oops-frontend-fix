"""
M-Pesa Service Factory

Factory for creating M-Pesa service instances with proper configuration and dependencies.
"""

from typing import Optional, Dict, Any
import os

from .config import MpesaConfig, MpesaEnvironment
from .base import BaseMpesaService
from .channel import MpesaChannelService
from .transaction import MpesaTransactionService
from .protocols import HTTPClient, CacheProvider, LoggerProtocol


class MpesaServiceFactory:
    """
    Factory for creating M-Pesa service instances.
    
    This factory provides:
    - Centralized service creation
    - Configuration management
    - Dependency injection
    - Environment-specific defaults
    """
    
    @staticmethod
    def create_config(
        consumer_key: Optional[str] = None,
        consumer_secret: Optional[str] = None,
        environment: str = "sandbox",
        **kwargs
    ) -> MpesaConfig:
        """
        Create M-Pesa configuration.
        
        Args:
            consumer_key: M-Pesa consumer key (or from env)
            consumer_secret: M-Pesa consumer secret (or from env)
            environment: API environment (sandbox/production)
            **kwargs: Additional configuration parameters
            
        Returns:
            MpesaConfig instance
        """
        # Use provided values or fall back to environment variables
        consumer_key = consumer_key or os.environ.get("MPESA_CONSUMER_KEY")
        consumer_secret = consumer_secret or os.environ.get("MPESA_CONSUMER_SECRET")
        
        if not consumer_key or not consumer_secret:
            raise ValueError("M-Pesa consumer key and secret are required")
        
        return MpesaConfig(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            environment=MpesaEnvironment(environment),
            **kwargs
        )
    
    @classmethod
    def create_channel_service(
        cls,
        consumer_key: Optional[str] = None,
        consumer_secret: Optional[str] = None,
        environment: str = "sandbox",
        http_client: Optional[HTTPClient] = None,
        cache: Optional[CacheProvider] = None,
        logger: Optional[LoggerProtocol] = None,
        **config_kwargs
    ) -> MpesaChannelService:
        """
        Create M-Pesa channel service.
        
        Args:
            consumer_key: M-Pesa consumer key
            consumer_secret: M-Pesa consumer secret
            environment: API environment
            http_client: Custom HTTP client
            cache: Custom cache provider
            logger: Custom logger
            **config_kwargs: Additional configuration
            
        Returns:
            MpesaChannelService instance
        """
        config = cls.create_config(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            environment=environment,
            **config_kwargs
        )
        
        return MpesaChannelService(
            config=config,
            http_client=http_client,
            cache=cache,
            logger=logger
        )
    
    @classmethod
    def create_transaction_service(
        cls,
        consumer_key: Optional[str] = None,
        consumer_secret: Optional[str] = None,
        environment: str = "sandbox",
        http_client: Optional[HTTPClient] = None,
        cache: Optional[CacheProvider] = None,
        logger: Optional[LoggerProtocol] = None,
        **config_kwargs
    ) -> MpesaTransactionService:
        """
        Create M-Pesa transaction service.
        
        Args:
            consumer_key: M-Pesa consumer key
            consumer_secret: M-Pesa consumer secret
            environment: API environment
            http_client: Custom HTTP client
            cache: Custom cache provider
            logger: Custom logger
            **config_kwargs: Additional configuration
            
        Returns:
            MpesaTransactionService instance
        """
        config = cls.create_config(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            environment=environment,
            **config_kwargs
        )
        
        return MpesaTransactionService(
            config=config,
            http_client=http_client,
            cache=cache,
            logger=logger
        )
    
    @classmethod
    def create_services(
        cls,
        consumer_key: Optional[str] = None,
        consumer_secret: Optional[str] = None,
        environment: str = "sandbox",
        shared_dependencies: Optional[Dict[str, Any]] = None,
        **config_kwargs
    ) -> Dict[str, BaseMpesaService]:
        """
        Create multiple M-Pesa services with shared dependencies.
        
        Args:
            consumer_key: M-Pesa consumer key
            consumer_secret: M-Pesa consumer secret
            environment: API environment
            shared_dependencies: Shared HTTP client, cache, logger
            **config_kwargs: Additional configuration
            
        Returns:
            Dictionary of service instances
        """
        config = cls.create_config(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            environment=environment,
            **config_kwargs
        )
        
        # Extract shared dependencies
        deps = shared_dependencies or {}
        http_client = deps.get("http_client")
        cache = deps.get("cache")
        logger = deps.get("logger")
        
        return {
            "channel": MpesaChannelService(config, http_client, cache, logger),
            "transaction": MpesaTransactionService(config, http_client, cache, logger)
        }
    
    @classmethod
    def from_merchant_config(
        cls,
        merchant_config: Dict[str, Any],
        service_type: str = "channel"
    ) -> BaseMpesaService:
        """
        Create service from merchant configuration.
        
        Args:
            merchant_config: Merchant M-Pesa configuration
            service_type: Type of service to create (channel/transaction)
            
        Returns:
            Appropriate service instance
        """
        required_fields = ["consumer_key", "consumer_secret"]
        for field in required_fields:
            if field not in merchant_config:
                raise ValueError(f"Missing required field: {field}")
        
        config = MpesaConfig(
            consumer_key=merchant_config["consumer_key"],
            consumer_secret=merchant_config["consumer_secret"],
            environment=MpesaEnvironment(
                merchant_config.get("environment", "sandbox")
            )
        )
        
        if service_type == "channel":
            return MpesaChannelService(config)
        elif service_type == "transaction":
            return MpesaTransactionService(config)
        else:
            raise ValueError(f"Unknown service type: {service_type}")
    
    @classmethod
    def for_testing(
        cls,
        service_type: str = "channel",
        mock_dependencies: Optional[Dict[str, Any]] = None
    ) -> BaseMpesaService:
        """
        Create service instance for testing.
        
        Args:
            service_type: Type of service to create
            mock_dependencies: Mock dependencies for testing
            
        Returns:
            Service instance configured for testing
        """
        config = MpesaConfig.for_testing()
        
        deps = mock_dependencies or {}
        http_client = deps.get("http_client")
        cache = deps.get("cache")
        logger = deps.get("logger")
        
        if service_type == "channel":
            return MpesaChannelService(config, http_client, cache, logger)
        elif service_type == "transaction":
            return MpesaTransactionService(config, http_client, cache, logger)
        else:
            raise ValueError(f"Unknown service type: {service_type}")


# Convenience functions for common use cases
def create_channel_service(**kwargs) -> MpesaChannelService:
    """Convenience function to create channel service"""
    return MpesaServiceFactory.create_channel_service(**kwargs)


def create_transaction_service(**kwargs) -> MpesaTransactionService:
    """Convenience function to create transaction service"""
    return MpesaServiceFactory.create_transaction_service(**kwargs)


def create_services(**kwargs) -> Dict[str, BaseMpesaService]:
    """Convenience function to create multiple services"""
    return MpesaServiceFactory.create_services(**kwargs)
