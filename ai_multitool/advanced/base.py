"""Base classes and interfaces for advanced tools."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel, Field
from enum import Enum
import asyncio
import time
from dataclasses import dataclass

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

    class Config:
        use_enum_values = True


class AdvancedToolConfig(BaseModel):
    """Configuration for advanced tools."""
    cache_enabled: bool = True
    parallel_execution: bool = True
    max_workers: int = 4
    timeout_seconds: int = 300
    retry_attempts: int = 3
    retry_delay_ms: int = 1000
    
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
        self.llm_client = llm_client
        self.config = config or AdvancedSettings.get()
        self.metrics = metrics_collector or MetricsCollector()
        self._cache = {}
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool.
        
        Args:
            **kwargs: Tool-specific arguments
            
        Returns:
            ToolResult with standardized format
        """
        pass
    
    @abstractmethod
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get tool definition for registration.
        
        Returns:
            Tool definition in standard format
        """
        pass
    
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
