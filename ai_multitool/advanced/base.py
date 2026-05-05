"""Base classes and interfaces for advanced tools."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
import asyncio
import time
import threading
from dataclasses import dataclass
from weakref import ref
import os
import re

from ..core.llm_client import BaseLLMClient
from ..utils.metrics import MetricsCollector


class ToolStatus(str, Enum):
    """Status of tool execution."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    SKIPPED = "skipped"


class ToolResult(BaseModel):
    """Standardized result format for all advanced tools."""
    success: bool = Field(..., description="Whether operation succeeded")
    status: ToolStatus = Field(default=ToolStatus.SUCCESS, description="Detailed status")
    data: Dict[str, Any] = Field(default_factory=dict, description="Tool-specific data")
    metrics: Dict[str, float] = Field(default_factory=dict, description="Performance metrics")
    suggestions: List[str] = Field(default_factory=list, description="Actionable suggestions")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    execution_time_ms: float = Field(default=0.0, description="Execution time in milliseconds")
    tokens_used: int = Field(default=0, description="Tokens consumed")

    model_config = ConfigDict(use_enum_values=True)

    def __str__(self) -> str:
        """String representation."""
        status_icon = "✓" if self.success else "✗"
        return f"ToolResult({status_icon} {self.status}, confidence={self.confidence:.2f}, time={self.execution_time_ms:.2f}ms)"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (f"ToolResult(success={self.success}, status={self.status}, "
                f"confidence={self.confidence:.2f}, execution_time_ms={self.execution_time_ms:.2f}, "
                f"tokens_used={self.tokens_used}, errors={len(self.errors)}, warnings={len(self.warnings)})")


class AdvancedToolConfig(BaseModel):
    """Configuration for advanced tools."""
    cache_enabled: bool = True
    parallel_execution: bool = True
    max_workers: int = 4
    timeout_seconds: int = 300
    retry_attempts: int = 3
    retry_delay_ms: int = 1000
    
    # Token budget controls
    max_tokens_per_session: int = 100000  # Total tokens allowed per session
    max_tokens_per_tool: int = 5000  # Max tokens per single tool execution
    warn_at_percent: float = 0.8  # Warn when 80% of budget used
    enable_token_tracking: bool = True  # Track token usage
    budget_exceeded_action: str = "warn"  # "warn", "stop", or "continue"
    
    # Content size limits
    max_code_lines: int = 1000  # Max lines of code to analyze
    max_file_size_kb: int = 500  # Max file size in KB
    
    # Category-specific configs
    code_analysis: Dict[str, Any] = Field(default_factory=dict)
    git_operations: Dict[str, Any] = Field(default_factory=dict)
    rag: Dict[str, Any] = Field(default_factory=dict)
    ai_features: Dict[str, Any] = Field(default_factory=dict)
    security: Dict[str, Any] = Field(default_factory=dict)
    testing: Dict[str, Any] = Field(default_factory=dict)
    documentation: Dict[str, Any] = Field(default_factory=dict)
    project: Dict[str, Any] = Field(default_factory=dict)
    collaboration: Dict[str, Any] = Field(default_factory=dict)


class AdvancedSettings:
    """Global settings for advanced tools."""
    
    _instance = None
    _config: Optional[AdvancedToolConfig] = None
    _session_tokens_used: int = 0  # Track tokens used in current session
    _budget_lock = threading.Lock()  # Lock for atomic budget operations
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def set(cls, config: Optional[AdvancedToolConfig] = None, **kwargs):
        """Set global settings."""
        if config:
            cls._config = config
        elif kwargs:
            if cls._config is None:
                cls._config = AdvancedToolConfig()
            for key, value in kwargs.items():
                if hasattr(cls._config, key):
                    setattr(cls._config, key, value)
    
    @classmethod
    def get(cls) -> AdvancedToolConfig:
        """Get current settings."""
        if cls._config is None:
            cls._config = AdvancedToolConfig()
        return cls._config
    
    @classmethod
    def add_tokens_used(cls, tokens: int):
        """Add tokens to session total (thread-safe)."""
        with cls._budget_lock:
            cls._session_tokens_used += tokens
    
    @classmethod
    def get_tokens_used(cls) -> int:
        """Get total tokens used in session (thread-safe)."""
        with cls._budget_lock:
            return cls._session_tokens_used
    
    @classmethod
    def reset_token_budget(cls):
        """Reset token budget (call at start of new session)."""
        with cls._budget_lock:
            cls._session_tokens_used = 0
    
    @classmethod
    def check_token_budget(cls, tokens_needed: int) -> tuple[bool, str]:
        """Check if token budget allows execution (thread-safe).
        
        Returns:
            (allowed: bool, message: str)
        """
        with cls._budget_lock:
            config = cls.get()
            if not config.enable_token_tracking:
                return True, ""
            
            total_after = cls._session_tokens_used + tokens_needed
            max_budget = config.max_tokens_per_session
            
            if total_after > max_budget:
                action = config.budget_exceeded_action
                if action == "stop":
                    return False, f"Token budget exceeded: {total_after}/{max_budget} tokens"
                elif action == "warn":
                    return True, f"WARNING: Token budget exceeded: {total_after}/{max_budget} tokens"
            
            # Check warning threshold
            if total_after > max_budget * config.warn_at_percent:
                return True, f"WARNING: {int(total_after/max_budget*100)}% of token budget used"
            
            return True, ""
    
    @classmethod
    def estimate_tokens(cls, text: str) -> int:
        """Estimate token count from text (fallback when LLM doesn't provide count).
        
        Rough estimation: ~4 characters per token for English text.
        More accurate would require a tokenizer, but this is a reasonable fallback.
        """
        if not text:
            return 0
        # Rough estimation: 4 chars per token, plus overhead
        return max(1, len(text) // 4)
    
    @classmethod
    def validate_path(cls, file_path: str) -> tuple[bool, str]:
        """Validate file path for security (prevent path traversal).
        
        Returns:
            (valid: bool, error_message: str)
        """
        if not file_path:
            return False, "File path cannot be empty"
        
        # Check for path traversal attempts
        if ".." in file_path or file_path.startswith("/"):
            return False, "Path traversal not allowed"
        
        # Check for absolute paths
        if os.path.isabs(file_path):
            return False, "Absolute paths not allowed"
        
        # Check for suspicious patterns
        suspicious_patterns = [r'\.env$', r'\.key$', r'\.pem$', r'secret', r'password']
        for pattern in suspicious_patterns:
            if re.search(pattern, file_path, re.IGNORECASE):
                return False, f"Suspicious file pattern detected: {pattern}"
        
        return True, ""


class AdvancedTool(ABC):
    """Base class for all advanced tools.
    
    All advanced tools must:
    1. Extend this class
    2. Implement execute() method
    3. Return ToolResult
    4. Handle errors gracefully
    """
    
    def __init__(
        self,
        llm_client: BaseLLMClient,
        config: Optional[AdvancedToolConfig] = None,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        """Initialize the advanced tool.

        Args:
            llm_client: LLM client for AI operations
            config: Tool configuration
            metrics_collector: Metrics collector
        """
        # Use weak references to prevent circular references
        self._llm_client_ref = ref(llm_client)
        self._metrics_ref = ref(metrics_collector or MetricsCollector())
        self.config = config or AdvancedSettings.get()
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_max_size = 1000
        self._cache_ttl = 3600  # 1 hour

    @property
    def llm_client(self) -> BaseLLMClient:
        """Get LLM client from weak reference."""
        client = self._llm_client_ref()
        if client is None:
            raise RuntimeError("LLM client has been garbage collected")
        return client

    @property
    def metrics(self) -> MetricsCollector:
        """Get metrics collector from weak reference."""
        collector = self._metrics_ref()
        if collector is None:
            raise RuntimeError("Metrics collector has been garbage collected")
        return collector
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool.
        
        Args:
            **kwargs: Tool-specific arguments
            
        Returns:
            ToolResult with standardized format
        """
        pass
    
    async def execute_with_budget_check(self, estimated_tokens: int = 2000, **kwargs) -> ToolResult:
        """Execute tool with token budget checking and validation.
        
        Args:
            estimated_tokens: Estimated tokens needed for this execution
            **kwargs: Tool-specific arguments
            
        Returns:
            ToolResult with standardized format
        """
        # Validate file paths if provided
        if 'file_path' in kwargs and kwargs['file_path']:
            valid, error = AdvancedSettings.validate_path(kwargs['file_path'])
            if not valid:
                return ToolResult(
                    success=False,
                    status=ToolStatus.FAILED,
                    errors=[error],
                    warnings=["File path validation failed for security reasons."]
                )
        
        # Check token budget before execution
        allowed, message = AdvancedSettings.check_token_budget(estimated_tokens)
        
        if not allowed:
            return ToolResult(
                success=False,
                status=ToolStatus.FAILED,
                errors=[message],
                warnings=["Token budget exceeded. Increase max_tokens_per_session or reset budget."]
            )
        
        if message:
            # Warning but continue
            print(f"[TOKEN BUDGET] {message}")
        
        # Execute the tool
        result = await self.execute(**kwargs)
        
        # Track tokens used (use fallback if not provided)
        tokens_used = result.tokens_used
        if tokens_used == 0:
            # Estimate from response content if available
            if hasattr(result, 'data') and result.data:
                content = str(result.data)
                tokens_used = AdvancedSettings.estimate_tokens(content)
            else:
                tokens_used = estimated_tokens  # Use estimate
        
        AdvancedSettings.add_tokens_used(tokens_used)
        
        # Update result with actual/estimated tokens
        result.tokens_used = tokens_used
        
        # Add budget info to warnings if near limit
        current_usage = AdvancedSettings.get_tokens_used()
        max_budget = self.config.max_tokens_per_session
        if current_usage > max_budget * self.config.warn_at_percent:
            result.warnings.append(
                f"Token budget at {int(current_usage/max_budget*100)}%: {current_usage}/{max_budget}"
            )
        
        return result
    
    @abstractmethod
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get tool definition for registration.
        
        Returns:
            Tool definition in standard format
        """
        pass
    
    async def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached value if available and not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key in self._cache:
            # Check if expired
            if time.time() - self._cache_timestamps[key] > self._cache_ttl:
                del self._cache[key]
                del self._cache_timestamps[key]
            else:
                return self._cache[key]
        return None
    
    async def _set_cached(self, key: str, value: Any) -> None:
        """Set cached value with TTL and memory limits.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # Enforce max size with LRU eviction
        if len(self._cache) >= self._cache_max_size:
            # Remove oldest entry (LRU)
            oldest_key = min(self._cache_timestamps.keys(), key=lambda k: self._cache_timestamps[k])
            del self._cache[oldest_key]
            del self._cache_timestamps[oldest_key]
        
        # Check if value is too large (prevent memory bloat)
        try:
            value_size = len(str(value))
            if value_size > 100000:  # 100KB limit per cached item
                # Don't cache large values
                return
        except:
            # If we can't determine size, still cache but limit count
            pass
        
        self._cache[key] = value
        self._cache_timestamps[key] = time.time()
    
    def _clear_cache(self) -> None:
        """Clear all cached values."""
        self._cache.clear()
        self._cache_timestamps.clear()
    
    async def _execute_with_retry(
        self,
        func,
        *args,
        max_retries: Optional[int] = None,
        **kwargs
    ) -> Any:
        """Execute function with retry logic.
        
        Args:
            func: Function to execute
            *args: Function arguments
            max_retries: Maximum retry attempts
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        max_retries = max_retries or self.config.retry_attempts
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    delay = self.config.retry_delay_ms / 1000
                    await asyncio.sleep(delay)
        
        raise last_exception
    
    def _get_cache_key(self, **kwargs) -> str:
        """Generate cache key from arguments.
        
        Args:
            **kwargs: Arguments to hash
            
        Returns:
            Cache key string
        """
        import hashlib
        import json
        key_str = json.dumps(kwargs, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get result from cache.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached result or None
        """
        if not self.config.cache_enabled:
            return None
        return self._cache.get(cache_key)
    
    def _set_cache(self, cache_key: str, result: Any):
        """Set result in cache.
        
        Args:
            cache_key: Cache key
            result: Result to cache
        """
        if self.config.cache_enabled:
            self._cache[cache_key] = result
    
    def _clear_cache(self):
        """Clear all cached results."""
        self._cache.clear()


class ToolPipeline:
    """Pipeline for executing multiple tools in sequence or parallel."""
    
    def __init__(
        self,
        tools: List[AdvancedTool],
        config: Optional[AdvancedToolConfig] = None
    ):
        """Initialize the pipeline.
        
        Args:
            tools: List of tools to execute
            config: Pipeline configuration
        """
        self.tools = tools
        self.config = config or AdvancedSettings.get()
    
    async def execute_sequential(self, **kwargs) -> List[ToolResult]:
        """Execute tools sequentially.
        
        Args:
            **kwargs: Arguments passed to all tools
            
        Returns:
            List of tool results
        """
        results = []
        for tool in self.tools:
            result = await tool.execute(**kwargs)
            results.append(result)
        return results
    
    async def execute_parallel(self, **kwargs) -> List[ToolResult]:
        """Execute tools in parallel.
        
        Args:
            **kwargs: Arguments passed to all tools
            
        Returns:
            List of tool results
        """
        if not self.config.parallel_execution:
            return await self.execute_sequential(**kwargs)
        
        tasks = [tool.execute(**kwargs) for tool in self.tools]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ToolResult(
                    success=False,
                    status=ToolStatus.FAILED,
                    errors=[str(result)]
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def execute(self, mode: str = "auto", **kwargs) -> List[ToolResult]:
        """Execute tools in specified mode.
        
        Args:
            mode: Execution mode ("sequential", "parallel", "auto")
            **kwargs: Arguments passed to all tools
            
        Returns:
            List of tool results
        """
        if mode == "auto":
            mode = "parallel" if self.config.parallel_execution else "sequential"
        
        if mode == "parallel":
            return await self.execute_parallel(**kwargs)
        else:
            return await self.execute_sequential(**kwargs)


class AdvancedToolRegistry:
    """Registry for managing advanced tools."""
    
    def __init__(self):
        """Initialize the registry."""
        self._tools: Dict[str, Type[AdvancedTool]] = {}
        self._instances: Dict[str, AdvancedTool] = {}
    
    def register(self, tool_class: Type[AdvancedTool], name: Optional[str] = None):
        """Register a tool class.
        
        Args:
            tool_class: Tool class to register
            name: Optional name (uses class name if not provided)
        """
        tool_name = name or tool_class.__name__
        self._tools[tool_name] = tool_class
    
    def unregister(self, tool_name: str):
        """Unregister a tool.
        
        Args:
            tool_name: Name of tool to unregister
        """
        self._tools.pop(tool_name, None)
        self._instances.pop(tool_name, None)
    
    def get_tool(
        self,
        tool_name: str,
        llm_client: BaseLLMClient,
        **kwargs
    ) -> AdvancedTool:
        """Get or create tool instance.
        
        Args:
            tool_name: Name of tool
            llm_client: LLM client
            **kwargs: Tool initialization arguments
            
        Returns:
            Tool instance
            
        Raises:
            KeyError: If tool not registered
        """
        if tool_name not in self._tools:
            raise KeyError(f"Tool '{tool_name}' not registered")
        
        if tool_name not in self._instances:
            tool_class = self._tools[tool_name]
            self._instances[tool_name] = tool_class(llm_client, **kwargs)
        
        return self._instances[tool_name]
    
    def list_tools(self) -> List[str]:
        """List all registered tool names.
        
        Returns:
            List of tool names
        """
        return list(self._tools.keys())
    
    def get_tool_definitions(self, llm_client: BaseLLMClient) -> List[Dict[str, Any]]:
        """Get all tool definitions.
        
        Args:
            llm_client: LLM client for tool initialization
            
        Returns:
            List of tool definitions
        """
        definitions = []
        for name, tool_class in self._tools.items():
            instance = tool_class(llm_client)
            definitions.append(instance.get_tool_definition())
        return definitions
