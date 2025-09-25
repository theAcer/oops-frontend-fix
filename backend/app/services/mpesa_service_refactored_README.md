"""
M-Pesa/Daraja API Integration Services - REFACTORED

This refactored version demonstrates best practices for scalable, maintainable API integrations:

## 🏗️ Architecture Best Practices Applied

### 1. **Single Responsibility Principle**
- `BaseMpesaService`: Handles common HTTP client, authentication, and retry logic
- `MpesaChannelService`: Focuses only on channel-specific operations
- `MpesaTransactionService`: Handles transaction-specific operations
- Clear separation of concerns

### 2. **Interface Segregation & Dependency Injection**
```python
class TokenProvider(Protocol):
    async def get_token(self) -> str: ...

class HTTPClient(Protocol):
    async def request(self, method: str, url: str, **kwargs) -> httpx.Response: ...
```
- Easy to mock for testing
- Clear contracts for dependencies
- Dependency injection ready

### 3. **Configuration Management**
```python
@dataclass
class MpesaConfig:
    consumer_key: str
    consumer_secret: str
    environment: str = "sandbox"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    token_cache_ttl: int = 3500
```
- Centralized configuration
- Environment-specific settings
- Easy to modify without code changes

### 4. **Error Handling & Resilience**
```python
class AuthenticationError(MpesaAPIError): ...
class RateLimitError(MpesaAPIError): ...
class ValidationError(MpesaAPIError): ...
```
- Custom exception hierarchy
- Exponential backoff retry logic
- Rate limit handling
- Comprehensive error logging

### 5. **Performance Optimizations**
- Token caching with TTL
- Connection pooling via HTTP client
- Lazy initialization
- Efficient retry mechanisms

### 6. **Code Organization & Maintainability**
- Factory pattern for service creation
- Legacy compatibility layer
- Clear import structure
- Comprehensive documentation

### 7. **Testing & Mocking**
```python
# Easy to test with dependency injection
async def test_channel_verification(mock_http_client):
    service = MpesaChannelService(config)
    service.http_client = mock_http_client
    # Test logic here
```

## 📈 Scalability Benefits

### 1. **Horizontal Scaling**
- Stateless services
- Connection pooling
- No shared mutable state

### 2. **Performance Scaling**
- Token caching reduces API calls
- Connection reuse
- Configurable timeouts and limits

### 3. **Development Scaling**
- Easy to add new API endpoints
- Clear patterns for new services
- Comprehensive error handling

### 4. **Operational Scaling**
- Structured logging for monitoring
- Health check endpoints
- Configuration management

## 🔧 Maintenance Benefits

### 1. **Code Reusability**
- Base class for common functionality
- Shared HTTP client logic
- Consistent error handling

### 2. **Easy Debugging**
- Structured logging with context
- Clear error messages
- Request/response tracing

### 3. **Configuration Flexibility**
- Environment-specific configs
- Runtime configuration changes
- Feature flags ready

### 4. **Testing Strategy**
- Unit tests for each service
- Integration tests for API calls
- Mock-friendly architecture

## 🚀 Migration Strategy

### Phase 1: New Features
- Use new architecture for Phase 2/3 features
- Keep existing DarajaService for backward compatibility

### Phase 2: Gradual Migration
- Refactor existing DarajaService to use new base classes
- Migrate endpoints one by one
- Maintain API compatibility

### Phase 3: Full Migration
- Replace old services completely
- Update all imports and dependencies
- Remove legacy compatibility code

## 💡 Key Improvements Over Original

1. **Better Error Handling**: Custom exceptions with proper hierarchy
2. **Performance**: Token caching, connection pooling, retry logic
3. **Maintainability**: Clear interfaces, separation of concerns
4. **Testability**: Easy to mock and test individual components
5. **Scalability**: Stateless, configurable, resource-efficient
6. **Observability**: Comprehensive logging and error tracking
7. **Flexibility**: Easy to extend and modify

## 🔍 Usage Examples

### Basic Usage
```python
# Create service instance
service = MpesaServiceFactory.create_channel_service(
    consumer_key="your_key",
    consumer_secret="your_secret",
    environment="sandbox"
)

# Use service
result = await service.verify_channel("174379")
await service.close()  # Cleanup
```

### Advanced Usage
```python
# Custom configuration
config = MpesaConfig(
    consumer_key="key",
    consumer_secret="secret",
    environment="production",
    max_retries=5,
    timeout=60
)
service = MpesaChannelService(config)
```

This refactored architecture provides a solid foundation for scalable, maintainable M-Pesa integration that can grow with your application needs.
"""

# Keep the original file for reference
# Original implementation moved to mpesa_service_refactored.py
