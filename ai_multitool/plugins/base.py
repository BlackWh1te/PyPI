"""Base plugin class for CLI tool integration."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum

from ..core.llm_client import BaseLLMClient
from ..core.models import Message, MessageRole
from ..rag.indexer import DocumentIndexer
from ..rag.embeddings import EmbeddingModel
from ..rag.vector_store import VectorStore
from ..utils.validation import is_empty_string


class Provider(str, Enum):
    """Supported AI providers."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    LITELLM = "litellm"


class PluginConfig(BaseModel):
    """Configuration for ai-multitool plugin."""
    api_key: str = Field(..., description="API key for the AI provider")
    provider: Provider = Field(default=Provider.ANTHROPIC, description="AI provider to use")
    model: str = Field(default="claude-3-sonnet-20240229", description="Model to use")
    max_tokens: int = Field(default=4096, description="Maximum tokens in response")
    temperature: float = Field(default=0.7, description="Temperature for generation")
    enable_cache: bool = Field(default=True, description="Enable response caching")
    enable_rag: bool = Field(default=False, description="Enable RAG capabilities")
    enable_code_analysis: bool = Field(default=True, description="Enable code analysis tools")
    enable_git_integration: bool = Field(default=True, description="Enable Git integration")
    timeout: int = Field(default=120, description="Request timeout in seconds")

    model_config = ConfigDict(use_enum_values=True)

    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key is not empty."""
        if is_empty_string(v):
            raise ValueError("API key cannot be empty")
        if len(v) < 10:
            raise ValueError("API key appears to be too short")
        return v.strip()

    @field_validator('max_tokens')
    @classmethod
    def validate_max_tokens(cls, v: int) -> int:
        """Validate max_tokens is positive and reasonable."""
        if v <= 0:
            raise ValueError("max_tokens must be positive")
        if v > 100000:
            raise ValueError("max_tokens is too large (max 100000)")
        return v

    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Validate temperature is in valid range."""
        if not 0.0 <= v <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")
        return v

    @field_validator('timeout')
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        """Validate timeout is positive and reasonable."""
        if v <= 0:
            raise ValueError("timeout must be positive")
        if v > 600:
            raise ValueError("timeout is too large (max 600 seconds)")
        return v


class BasePlugin(ABC):
    """Base class for ai-multitool plugins for CLI tools.

    CLI tools (Claude Code, Devin, OpenCode, etc.) should extend this class
    to integrate ai-multitool functionality.
    """

    def __init__(self, config: PluginConfig):
        """Initialize the plugin.

        Args:
            config: Plugin configuration
        """
        self.config = config
        self.llm_client: Optional[BaseLLMClient] = None
        self.rag_indexer: Optional[DocumentIndexer] = None
        self._initialize()

    def _initialize(self):
        """Initialize LLM client and optional components."""
        self.llm_client = self._create_llm_client()

    @abstractmethod
    def _create_llm_client(self) -> BaseLLMClient:
        """Create and configure LLM client for the CLI tool.

        Returns:
            Configured LLM client instance
        """
        pass

    @abstractmethod
    def get_tool_definitions(self) -> List[Any]:
        """Return list of tools available to the CLI tool.

        The format should match the CLI tool's expected tool definition format.

        Returns:
            List of tool definitions
        """
        pass

    @abstractmethod
    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool by name.

        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool-specific arguments

        Returns:
            Tool execution result

        Raises:
            ToolExecutionError: If tool execution fails
        """
        pass

    def enable_rag(
        self,
        embedding_model: Optional[EmbeddingModel] = None,
        vector_store: Optional[VectorStore] = None
    ):
        """Enable RAG capabilities.

        Args:
            embedding_model: Model for generating embeddings
            vector_store: Store for embeddings and chunks
        """
        if not self.config.enable_rag:
            raise ValueError("RAG is not enabled in plugin config")

        self.rag_indexer = DocumentIndexer(
            embedding_model=embedding_model,
            vector_store=vector_store
        )

    async def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> str:
        """Send a chat message to the LLM.

        Args:
            message: User message
            system_prompt: Optional system prompt
            stream: Whether to stream the response

        Returns:
            LLM response text
        """
        if not self.llm_client:
            raise RuntimeError("LLM client not initialized")

        messages = [Message(role=MessageRole.USER, content=message)]
        if system_prompt:
            messages.insert(0, Message(role=MessageRole.SYSTEM, content=system_prompt))

        response = await self.llm_client.chat(
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            stream=stream
        )

        return response.content

    def get_config(self) -> PluginConfig:
        """Get the plugin configuration.

        Returns:
            Plugin configuration
        """
        return self.config

    def is_rag_enabled(self) -> bool:
        """Check if RAG is enabled.

        Returns:
            True if RAG is enabled
        """
        return self.rag_indexer is not None
