"""Tests for core LLM client functionality."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from ai_multitool import (
    AnthropicClient,
    OpenAIClient,
    BaseLLMClient,
    Message,
    MessageRole,
    LLMResponse,
    ChatHistory,
    ModelInfo,
)
from ai_multitool.core.exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
)


class TestMessage:
    """Test Message model."""
    
    def test_message_creation(self):
        """Test creating a message."""
        message = Message(role=MessageRole.USER, content="Hello")
        assert message.role == MessageRole.USER
        assert message.content == "Hello"
    
    def test_message_with_optional_fields(self):
        """Test message with optional fields."""
        message = Message(
            role=MessageRole.ASSISTANT,
            content="Response",
            metadata={"key": "value"}
        )
        assert message.metadata == {"key": "value"}


class TestLLMResponse:
    """Test LLMResponse model."""
    
    def test_response_creation(self):
        """Test creating an LLM response."""
        response = LLMResponse(
            content="Response text",
            model="claude-3-sonnet-20240229",
            tokens_used=30,
            finish_reason="stop"
        )
        assert response.content == "Response text"
        assert response.model == "claude-3-sonnet-20240229"
        assert response.tokens_used == 30
        assert response.finish_reason == "stop"


class TestChatHistory:
    """Test ChatHistory model."""
    
    def test_history_creation(self):
        """Test creating chat history."""
        messages = [
            Message(role=MessageRole.USER, content="Hello"),
            Message(role=MessageRole.ASSISTANT, content="Hi"),
        ]
        history = ChatHistory(messages=messages)
        assert len(history.messages) == 2
    
    def test_history_add_message(self):
        """Test adding a message to history."""
        history = ChatHistory(messages=[])
        history.add_message(Message(role=MessageRole.USER, content="New"))
        assert len(history.messages) == 1


class TestAnthropicClient:
    """Test Anthropic client."""
    
    def test_client_initialization(self, mock_anthropic_api_key):
        """Test Anthropic client initialization."""
        client = AnthropicClient(
            api_key=mock_anthropic_api_key,
            model="claude-3-sonnet-20240229"
        )
        assert client.api_key == mock_anthropic_api_key
        assert client.model == "claude-3-sonnet-20240229"
    
    def test_client_validation_error_no_api_key(self):
        """Test that client raises error without API key."""
        from ai_multitool.core.exceptions import ConfigurationError
        with pytest.raises(ConfigurationError):
            AnthropicClient(api_key="", model="claude-3-sonnet-20240229")
    
    def test_client_validation_error_invalid_model(self, mock_anthropic_api_key):
        """Test that client raises error with invalid model."""
        from ai_multitool.core.exceptions import ConfigurationError
        with pytest.raises(ConfigurationError):
            AnthropicClient(api_key=mock_anthropic_api_key, model="")
    
    @pytest.mark.asyncio
    async def test_chat_call(self, mock_anthropic_api_key):
        """Test making a chat call."""
        with patch('ai_multitool.core.llm_client.anthropic.Anthropic') as mock_anthropic:
            # Setup mock
            mock_response = Mock()
            mock_response.content = [Mock(text="Response text")]
            mock_response.model = "claude-3-sonnet-20240229"
            mock_response.usage = Mock(input_tokens=10, output_tokens=20)
            
            mock_client = Mock()
            mock_client.messages.create = Mock(return_value=mock_response)
            mock_anthropic.return_value = mock_client
            
            # Test
            client = AnthropicClient(
                api_key=mock_anthropic_api_key,
                model="claude-3-sonnet-20240229"
            )
            
            messages = [Message(role=MessageRole.USER, content="Hello")]
            response = await client.chat(messages)
            
            assert response.content == "Response text"
            assert response.model == "claude-3-sonnet-20240229"
    
    @pytest.mark.asyncio
    async def test_chat_with_cache(self, mock_anthropic_api_key, sample_messages):
        """Test chat with caching enabled."""
        with patch('ai_multitool.core.llm_client.anthropic.Anthropic') as mock_anthropic:
            mock_response = Mock()
            mock_response.content = [Mock(text="Cached response")]
            mock_response.model = "claude-3-sonnet-20240229"
            mock_response.usage = Mock(input_tokens=5, output_tokens=10)
            
            mock_client = Mock()
            mock_client.messages.create = Mock(return_value=mock_response)
            mock_anthropic.return_value = mock_client
            
            client = AnthropicClient(
                api_key=mock_anthropic_api_key,
                model="claude-3-sonnet-20240229",
                enable_cache=True
            )
            
            # First call
            response1 = await client.chat(sample_messages)
            # Second call (should use cache)
            response2 = await client.chat(sample_messages)
            
            assert response1.content == "Cached response"
            assert response2.content == "Cached response"


class TestOpenAIClient:
    """Test OpenAI client."""
    
    def test_client_initialization(self, mock_openai_api_key):
        """Test OpenAI client initialization."""
        client = OpenAIClient(
            api_key=mock_openai_api_key,
            model="gpt-4"
        )
        assert client.config.api_key == mock_openai_api_key
        assert client.config.model == "gpt-4"
    
    @pytest.mark.asyncio
    async def test_chat_call(self, mock_openai_api_key):
        """Test making a chat call with OpenAI."""
        with patch('ai_multitool.core.llm_client.openai.OpenAI') as mock_openai:
            # Setup mock
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="OpenAI response"))]
            mock_response.model = "gpt-4"
            mock_response.usage = Mock(prompt_tokens=10, completion_tokens=20)
            
            mock_client = Mock()
            mock_client.chat.completions.create = Mock(return_value=mock_response)
            mock_openai.return_value = mock_client
            
            # Test
            client = OpenAIClient(
                api_key=mock_openai_api_key,
                model="gpt-4"
            )
            
            messages = [Message(role=MessageRole.USER, content="Hello")]
            response = await client.chat(messages)
            
            assert response.content == "OpenAI response"
            assert response.model == "gpt-4"


class TestRateLimiter:
    """Test rate limiter functionality."""
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization."""
        from ai_multitool.core.llm_client import RateLimiter
        
        limiter = RateLimiter(tokens_per_minute=10000)
        assert limiter.tokens_per_minute == 10000
    
    def test_rate_limiter_acquire(self):
        """Test acquiring tokens from rate limiter."""
        from ai_multitool.core.llm_client import RateLimiter
        import time
        
        limiter = RateLimiter(tokens_per_minute=1000)
        start_time = time.time()
        
        # Should not block for small request
        limiter.acquire(100)
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0  # Should be fast


class TestResponseCache:
    """Test response cache functionality."""
    
    def test_cache_initialization(self):
        """Test cache initialization."""
        from ai_multitool.core.llm_client import ResponseCache
        
        cache = ResponseCache(ttl=3600)
        assert cache.ttl == 3600
    
    def test_cache_get_set(self):
        """Test cache get and set operations."""
        from ai_multitool.core.llm_client import ResponseCache
        
        cache = ResponseCache(ttl=3600)
        key = "test_key"
        value = LLMResponse(content="Cached", model="test", usage={})
        
        cache.set(key, value)
        retrieved = cache.get(key)
        
        assert retrieved is not None
        assert retrieved.content == "Cached"
    
    def test_cache_expiration(self):
        """Test cache expiration."""
        from ai_multitool.core.llm_client import ResponseCache
        import time
        
        cache = ResponseCache(ttl=1)  # 1 second TTL
        key = "test_key"
        value = LLMResponse(content="Cached", model="test", usage={})
        
        cache.set(key, value)
        time.sleep(1.1)  # Wait for expiration
        
        retrieved = cache.get(key)
        assert retrieved is None


class TestModelInfo:
    """Test ModelInfo model."""
    
    def test_model_info_creation(self):
        """Test creating model info."""
        info = ModelInfo(
            model_id="claude-3-sonnet-20240229",
            provider="anthropic",
            max_tokens=4096,
            context_window=200000
        )
        assert info.model_id == "claude-3-sonnet-20240229"
        assert info.provider == "anthropic"
        assert info.max_tokens == 4096
