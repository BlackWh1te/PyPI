"""Base LLM client and implementations"""

from abc import ABC, abstractmethod
from typing import List, AsyncIterator, Optional
import asyncio
import time
import hashlib
from collections import OrderedDict

from .models import Message, LLMResponse, ModelInfo
from .exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
    QuotaExceededError,
    ModelNotFoundError,
    TimeoutError as CustomTimeoutError,
    NetworkError,
    ConfigurationError
)
from ..utils.logging_config import get_logger
from ..utils.validation import is_empty_string

logger = get_logger(__name__)


class RateLimiter:
    """Token bucket rate limiter for API calls"""

    def __init__(self, rate: int = 60, per: float = 60.0):
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self):
        """Acquire permission to make API call"""
        async with self._lock:
            current = time.time()
            time_passed = current - self.last_check
            self.last_check = current
            # Use min() to prevent overflow if time_passed is very large
            self.allowance = min(self.rate, self.allowance + time_passed * (self.rate / self.per))

            if self.allowance < 1:
                sleep_time = (1 - self.allowance) * (self.per / self.rate)
                await asyncio.sleep(sleep_time)
                self.allowance = 0
            else:
                self.allowance -= 1


class ResponseCache:
    """Simple in-memory cache for LLM responses"""

    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        # Use OrderedDict for efficient cache cleanup (O(1) instead of O(n))
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl
        self._lock = asyncio.Lock()

    def _make_key(self, data: str) -> str:
        """Make cache key from data"""
        return hashlib.sha256(data.encode()).hexdigest()

    def _make_cache_key(self, messages: List[Message], temperature: float, max_tokens: int) -> str:
        """Make cache key from messages and parameters efficiently."""
        # Hash the message contents instead of building large string
        content_hash = hashlib.sha256(
            str([m.content for m in messages]).encode()
        ).hexdigest()
        return f"{content_hash}_{temperature}_{max_tokens}"

    async def get(self, messages: List[Message], temperature: float, max_tokens: int) -> Optional[LLMResponse]:
        """Get cached response if available"""
        key = self._make_cache_key(messages, temperature, max_tokens)

        async with self._lock:
            if key in self.cache:
                item = self.cache[key]
                if time.time() - item["timestamp"] < self.ttl:
                    item["value"].cached = True
                    return item["value"]
                else:
                    del self.cache[key]
            return None

    async def set(self, messages: List[Message], response: LLMResponse, temperature: float, max_tokens: int):
        """Cache response"""
        key = self._make_cache_key(messages, temperature, max_tokens)

        async with self._lock:
            if len(self.cache) >= self.max_size:
                # Remove oldest entry efficiently (O(1) with OrderedDict)
                self.cache.popitem(last=False)

            self.cache[key] = {
                "value": response,
                "timestamp": time.time()
            }


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients"""

    def __init__(self, api_key: str, model: str, timeout: int = 120, enable_cache: bool = True):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self._rate_limiter = RateLimiter()
        self._cache = ResponseCache() if enable_cache else None

    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """Send chat request and get response"""
        pass

    @abstractmethod
    async def stream_chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream chat response"""
        pass

    @abstractmethod
    def get_model_info(self) -> ModelInfo:
        """Get model capabilities and limits"""
        pass


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude client"""

    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", timeout: int = 120, enable_cache: bool = True):
        if is_empty_string(api_key):
            raise ConfigurationError("API key is required for Anthropic", suggestion="Set ANTHROPIC_API_KEY in .env or use 'ai-multitool keys set anthropic'")
        
        super().__init__(api_key, model, timeout, enable_cache)
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(api_key=api_key, timeout=timeout)
        except ImportError as e:
            raise ConfigurationError(
                "anthropic package is required",
                suggestion="Install with: pip install anthropic",
                details={"error": str(e)}
            )
        except Exception as e:
            raise ConfigurationError(
                f"Failed to initialize Anthropic client",
                suggestion="Check your API key and internet connection",
                details={"error": str(e)}
            )

    async def chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Send chat request to Anthropic with retry and caching"""
        if not messages:
            raise ConfigurationError("Messages list cannot be empty", suggestion="Provide at least one message")
        
        logger.debug(f"Chat request: model={self.model}, messages={len(messages)}, temperature={temperature}")
        
        # Check cache first
        if self._cache:
            cached = await self._cache.get(messages, temperature, max_tokens)
            if cached:
                logger.debug("Cache hit - returning cached response")
                return cached

        # Rate limiting
        await self._rate_limiter.acquire()

        # Retry logic with better error handling
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()

                # Build messages
                anthropic_messages = [
                    {"role": m.role.value, "content": m.content}
                    for m in messages
                ]

                # Make API call
                response = await self.client.messages.create(
                    model=self.model,
                    messages=anthropic_messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    **kwargs
                )

                # Parse response
                latency_ms = (time.time() - start_time) * 1000

                result = LLMResponse(
                    content=response.content[0].text,
                    model=self.model,
                    tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                    finish_reason=response.stop_reason,
                    latency_ms=latency_ms
                )

                logger.info(f"Chat success: tokens={result.tokens_used}, latency={latency_ms:.2f}ms")

                # Cache result
                if self._cache:
                    await self._cache.set(messages, result, temperature, max_tokens)

                return result

            except anthropic.AuthenticationError as e:
                raise AuthenticationError("anthropic")
            except anthropic.RateLimitError as e:
                retry_after = getattr(e, 'retry_after', None)
                if attempt == max_retries - 1:
                    raise RateLimitError(retry_after=retry_after)
                await asyncio.sleep(retry_after or 2 ** attempt)
            except anthropic.BadRequestError as e:
                if "model" in str(e).lower():
                    raise ModelNotFoundError(self.model, "anthropic")
                raise APIError(f"Bad request: {e}", status_code=400, response_body=str(e))
            except anthropic.UnprocessableEntityError as e:
                raise APIError(f"Unprocessable entity: {e}", status_code=422, response_body=str(e))
            except anthropic.InternalServerError as e:
                if attempt == max_retries - 1:
                    raise NetworkError(f"Anthropic internal server error: {e}")
                await asyncio.sleep(2 ** attempt)
            except anthropic.APITimeoutError as e:
                if attempt == max_retries - 1:
                    raise CustomTimeoutError("Anthropic API call", self.timeout)
                await asyncio.sleep(2 ** attempt)
            except anthropic.APIConnectionError as e:
                if attempt == max_retries - 1:
                    raise NetworkError(f"Failed to connect to Anthropic: {e}")
                await asyncio.sleep(2 ** attempt)
            except anthropic.APIStatusError as e:
                if e.status_code == 429:
                    raise RateLimitError()
                elif e.status_code == 401:
                    raise AuthenticationError("anthropic")
                elif e.status_code == 429:
                    raise QuotaExceededError("anthropic")
                else:
                    raise APIError(
                        f"API error: {e}",
                        status_code=e.status_code,
                        response_body=str(e)
                    )
            except Exception as e:
                last_error = e
                if attempt == max_retries - 1:
                    raise APIError(f"Unexpected error: {e}", details={"error_type": type(e).__name__})
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)

    async def stream_chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream chat response from Anthropic"""
        if not messages:
            raise ConfigurationError("Messages list cannot be empty", suggestion="Provide at least one message")
        
        anthropic_messages = [
            {"role": m.role.value, "content": m.content}
            for m in messages
        ]

        try:
            async with self.client.messages.stream(
                model=self.model,
                messages=anthropic_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                **kwargs
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except anthropic.AuthenticationError:
            raise AuthenticationError("anthropic")
        except anthropic.RateLimitError as e:
            retry_after = getattr(e, 'retry_after', None)
            raise RateLimitError(retry_after=retry_after)
        except anthropic.BadRequestError as e:
            if "model" in str(e).lower():
                raise ModelNotFoundError(self.model, "anthropic")
            raise APIError(f"Bad request: {e}", status_code=400)
        except anthropic.APIConnectionError as e:
            raise NetworkError(f"Failed to connect to Anthropic: {e}")
        except Exception as e:
            raise APIError(f"Streaming error: {e}", details={"error_type": type(e).__name__})

    def get_model_info(self) -> ModelInfo:
        """Get Anthropic model info"""
        return ModelInfo(
            name=self.model,
            max_tokens=8192 if "opus" in self.model else 4096,
            supports_streaming=True,
            supports_function_calling="3" in self.model,
            cost_per_1k_input=0.003 if "opus" in self.model else 0.00025,
            cost_per_1k_output=0.015 if "opus" in self.model else 0.00125
        )


class OpenAIClient(BaseLLMClient):
    """OpenAI GPT client"""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview", timeout: int = 120, enable_cache: bool = True):
        if is_empty_string(api_key):
            raise ConfigurationError("API key is required for OpenAI", suggestion="Set OPENAI_API_KEY in .env or use 'ai-multitool keys set openai'")
        
        super().__init__(api_key, model, timeout, enable_cache)
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=api_key, timeout=timeout)
        except ImportError as e:
            raise ConfigurationError(
                "openai package is required",
                suggestion="Install with: pip install openai",
                details={"error": str(e)}
            )
        except Exception as e:
            raise ConfigurationError(
                f"Failed to initialize OpenAI client",
                suggestion="Check your API key and internet connection",
                details={"error": str(e)}
            )

    async def chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """Send chat request to OpenAI with retry and caching"""
        if not messages:
            raise ConfigurationError("Messages list cannot be empty", suggestion="Provide at least one message")
        
        # Check cache first
        if self._cache:
            cached = await self._cache.get(messages, temperature, max_tokens)
            if cached:
                return cached

        # Rate limiting
        await self._rate_limiter.acquire()

        # Retry logic with better error handling
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()

                # Build messages
                openai_messages = [
                    {"role": m.role.value, "content": m.content}
                    for m in messages
                ]

                # Make API call
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=openai_messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )

                # Parse response
                latency_ms = (time.time() - start_time) * 1000

                result = LLMResponse(
                    content=response.choices[0].message.content,
                    model=self.model,
                    tokens_used=response.usage.total_tokens,
                    finish_reason=response.choices[0].finish_reason,
                    latency_ms=latency_ms
                )

                # Cache result
                if self._cache:
                    await self._cache.set(messages, result, temperature, max_tokens)

                return result

            except openai.AuthenticationError as e:
                raise AuthenticationError("openai")
            except openai.RateLimitError as e:
                if attempt == max_retries - 1:
                    raise RateLimitError()
                await asyncio.sleep(2 ** attempt)
            except openai.BadRequestError as e:
                if "model" in str(e).lower():
                    raise ModelNotFoundError(self.model, "openai")
                raise APIError(f"Bad request: {e}", status_code=400, response_body=str(e))
            except openai.APITimeoutError as e:
                if attempt == max_retries - 1:
                    raise CustomTimeoutError("OpenAI API call", self.timeout)
                await asyncio.sleep(2 ** attempt)
            except openai.APIConnectionError as e:
                if attempt == max_retries - 1:
                    raise NetworkError(f"Failed to connect to OpenAI: {e}")
                await asyncio.sleep(2 ** attempt)
            except openai.APIStatusError as e:
                if e.status_code == 429:
                    raise RateLimitError()
                elif e.status_code == 401:
                    raise AuthenticationError("openai")
                elif e.status_code == 429:
                    raise QuotaExceededError("openai")
                else:
                    raise APIError(
                        f"API error: {e}",
                        status_code=e.status_code,
                        response_body=str(e)
                    )
            except Exception as e:
                last_error = e
                if attempt == max_retries - 1:
                    raise APIError(f"Unexpected error: {e}", details={"error_type": type(e).__name__})
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)

    async def stream_chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream chat response from OpenAI"""
        if not messages:
            raise ConfigurationError("Messages list cannot be empty", suggestion="Provide at least one message")
        
        openai_messages = [
            {"role": m.role.value, "content": m.content}
            for m in messages
        ]

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                **kwargs
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except openai.AuthenticationError:
            raise AuthenticationError("openai")
        except openai.RateLimitError:
            raise RateLimitError()
        except openai.BadRequestError as e:
            if "model" in str(e).lower():
                raise ModelNotFoundError(self.model, "openai")
            raise APIError(f"Bad request: {e}", status_code=400)
        except openai.APIConnectionError as e:
            raise NetworkError(f"Failed to connect to OpenAI: {e}")
        except Exception as e:
            raise APIError(f"Streaming error: {e}", details={"error_type": type(e).__name__})

    def get_model_info(self) -> ModelInfo:
        """Get OpenAI model info"""
        return ModelInfo(
            name=self.model,
            max_tokens=128000 if "turbo" in self.model else 4096,
            supports_streaming=True,
            supports_function_calling=True,
            cost_per_1k_input=0.01 if "turbo" in self.model else 0.03,
            cost_per_1k_output=0.03 if "turbo" in self.model else 0.06
        )


class OllamaClient(BaseLLMClient):
    """Ollama client for local models"""

    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: Optional[str] = None,
        enable_cache: bool = True,
        **kwargs
    ):
        try:
            import ollama
        except ImportError:
            raise ConfigurationError(
                "Ollama library not installed",
                suggestion="Install with: pip install ai-multitool[ollama]"
            )

        self.host = host
        self.client = ollama.Client(host=host)
        
        # Auto-detect model if not specified
        if model is None:
            model = self._get_first_model()
        
        self.model = model
        self._cache = ResponseCache() if enable_cache else None
        logger.info(f"Ollama client initialized with model: {model}")

    def _get_first_model(self) -> str:
        """Get the first available model from Ollama"""
        try:
            models = self.client.list()
            if models and 'models' in models and models['models']:
                first_model = models['models'][0]['name']
                logger.info(f"Auto-detected Ollama model: {first_model}")
                return first_model
            else:
                raise ConfigurationError(
                    "No models found in Ollama",
                    suggestion="Pull a model with: ollama pull llama2\nOr install with: pip install ai-multitool[ollama]"
                )
        except Exception as e:
            error_msg = str(e).lower()
            if "connect" in error_msg or "connection" in error_msg:
                raise ConfigurationError(
                    f"Cannot connect to Ollama at {self.host}",
                    suggestion="1. Make sure Ollama is running: ollama serve\n"
                               "2. Install Ollama from: https://ollama.com\n"
                               "3. Install ollama extra: pip install ai-multitool[ollama]"
                )
            else:
                raise ConfigurationError(
                    f"Ollama error: {e}",
                    suggestion="Check Ollama installation and try: ollama serve"
                )

    async def chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Chat with Ollama model"""
        if not messages:
            raise ConfigurationError("Messages list cannot be empty", suggestion="Provide at least one message")

        start_time = time.time()

        # Convert messages to Ollama format
        ollama_messages = [
            {"role": m.role.value, "content": m.content}
            for m in messages
        ]

        # Add system prompt if provided
        if system_prompt:
            ollama_messages.insert(0, {"role": "system", "content": system_prompt})

        try:
            # Make API call (ollama library is synchronous, run in thread pool)
            import asyncio
            loop = asyncio.get_event_loop()
            
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat(
                    model=self.model,
                    messages=ollama_messages,
                    options={
                        'temperature': temperature,
                        'num_predict': max_tokens,
                    }
                )
            )

            # Parse response
            latency_ms = (time.time() - start_time) * 1000

            result = LLMResponse(
                content=response['message']['content'],
                model=self.model,
                tokens_used=response.get('eval_count', 0) + response.get('prompt_eval_count', 0),
                finish_reason='stop',
                latency_ms=latency_ms
            )

            logger.info(f"Ollama chat success: tokens={result.tokens_used}, latency={latency_ms:.2f}ms")

            # Cache result
            if self._cache:
                await self._cache.set(messages, result, temperature, max_tokens)

            return result

        except Exception as e:
            if "connect" in str(e).lower():
                raise NetworkError(f"Failed to connect to Ollama at {self.host}")
            raise APIError(f"Ollama error: {e}", details={"error_type": type(e).__name__})

    async def stream_chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream chat response from Ollama"""
        if not messages:
            raise ConfigurationError("Messages list cannot be empty", suggestion="Provide at least one message")

        # Convert messages to Ollama format
        ollama_messages = [
            {"role": m.role.value, "content": m.content}
            for m in messages
        ]

        # Add system prompt if provided
        if system_prompt:
            ollama_messages.insert(0, {"role": "system", "content": system_prompt})

        try:
            import asyncio
            loop = asyncio.get_event_loop()
            
            # Stream response
            stream = await loop.run_in_executor(
                None,
                lambda: self.client.chat(
                    model=self.model,
                    messages=ollama_messages,
                    stream=True,
                    options={
                        'temperature': temperature,
                        'num_predict': max_tokens,
                    }
                )
            )

            for chunk in stream:
                if chunk['message']['content']:
                    yield chunk['message']['content']

        except Exception as e:
            if "connect" in str(e).lower():
                raise NetworkError(f"Failed to connect to Ollama at {self.host}")
            raise APIError(f"Ollama streaming error: {e}", details={"error_type": type(e).__name__})

    def get_model_info(self) -> ModelInfo:
        """Get Ollama model info"""
        return ModelInfo(
            name=self.model,
            max_tokens=4096,  # Default for most Ollama models
            supports_streaming=True,
            supports_function_calling=False,
            cost_per_1k_input=0.0,  # Free - local
            cost_per_1k_output=0.0
        )


class ClientFactory:
    """Factory for creating LLM clients"""

    @staticmethod
    def create_client(
        provider: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        enable_cache: bool = True,
        **kwargs
    ) -> BaseLLMClient:
        """Create LLM client based on provider"""
        providers = {
            "anthropic": AnthropicClient,
            "openai": OpenAIClient,
            "ollama": OllamaClient,
        }

        if is_empty_string(provider):
            # Auto-detect: try Ollama first, then default to anthropic
            try:
                return OllamaClient(model=model, enable_cache=enable_cache, **kwargs)
            except:
                provider = "anthropic"
        
        provider = provider.lower()
        
        if provider not in providers:
            raise ConfigurationError(
                f"Unknown provider: {provider}",
                suggestion=f"Available providers: {', '.join(providers.keys())}"
            )

        client_class = providers[provider]

        # Ollama doesn't need API key
        if provider == "ollama":
            try:
                return client_class(model=model, enable_cache=enable_cache, **kwargs)
            except Exception as e:
                if isinstance(e, (ConfigurationError, APIError)):
                    raise
                raise ConfigurationError(
                    f"Failed to create Ollama client: {e}",
                    suggestion="Make sure Ollama is running: ollama serve"
                )

        # Other providers need API key
        if not api_key:
            raise ConfigurationError(
                f"API key required for {provider}",
                suggestion=f"Set {provider.upper()}_API_KEY environment variable"
            )

        # Default models
        if model is None:
            if provider == "anthropic":
                model = "claude-3-sonnet-20240229"
            elif provider == "openai":
                model = "gpt-4-turbo-preview"

        try:
            return client_class(api_key, model, enable_cache=enable_cache, **kwargs)
        except Exception as e:
            if isinstance(e, (ConfigurationError, APIError)):
                raise
            raise ConfigurationError(
                f"Failed to create {provider} client",
                suggestion="Check your API key and configuration",
                details={"error": str(e), "error_type": type(e).__name__}
            )
