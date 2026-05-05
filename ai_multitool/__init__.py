"""
ai-multitool: AI-powered multitool library for CLI integration

This library provides AI-powered capabilities that can be integrated into
various CLI tools (Claude Code, Devin, OpenCode, Gemini CLI, Qwen CLI, etc.).

Example usage:
    from ai_multitool import AnthropicClient, Message, MessageRole

    client = AnthropicClient(api_key="your-key", model="claude-3-sonnet-20240229")
    response = await client.chat([Message(role=MessageRole.USER, content="Hello!")])
"""

__version__ = "0.2.0"

# Core LLM functionality
from .core.llm_client import (
    BaseLLMClient,
    AnthropicClient,
    OpenAIClient,
    RateLimiter,
    ResponseCache,
)

from .core.models import (
    Message,
    MessageRole,
    LLMResponse,
    ModelInfo,
    ChatHistory,
)

from .core.exceptions import (
    AIMultitoolError,
    APIError,
    AuthenticationError,
    RateLimitError,
    QuotaExceededError,
    ModelNotFoundError,
    TimeoutError,
    NetworkError,
    ConfigurationError,
    ValidationError,
    FileOperationError,
    CodeParsingError,
    KeyringError,
    MetricsError,
    SanitizationError,
    GitError,
    ContextError,
)

# RAG functionality
from .rag.indexer import DocumentIndexer, Document
from .rag.embeddings import EmbeddingModel, OpenAIEmbeddings, FakeEmbeddings
from .rag.chunkers import (
    DocumentChunker,
    RecursiveCharacterChunker,
    FixedSizeChunker,
    SentenceChunker,
)
from .rag.vector_store import VectorStore, InMemoryVectorStore
from .rag.retriever import SimilarityRetriever

# Code parsing
from .parsers.code_parser import CodeParser, CodeStructure

# Utilities
from .utils.key_manager import KeyManager
from .utils.sanitizer import ContentSanitizer, SanitizationResult
from .utils.git_utils import GitHelper
from .utils.context_builder import SmartContextBuilder, AnalysisContext
from .utils.metrics import MetricsCollector, MetricsContext
from .utils.file_utils import read_file, read_directory

# Plugin interface
from .plugins import (
    BasePlugin,
    PluginConfig,
    Provider,
    ToolDefinition,
    ToolRegistry,
    ToolCategory,
    PluginError,
    ToolExecutionError,
)

# Adapters
from .adapters import (
    BaseAdapter,
    ToolConverter,
    ClaudeCodeAdapter,
    create_claude_code_adapter,
    DevinAdapter,
    create_devin_adapter,
)

# Advanced tools (base only - advanced tool imports disabled due to naming inconsistencies)
from .advanced.base import (
    AdvancedTool,
    ToolResult,
    ToolPipeline,
    AdvancedToolConfig,
    AdvancedSettings,
)

__all__ = [
    # Version
    "__version__",

    # Core LLM
    "BaseLLMClient",
    "AnthropicClient",
    "OpenAIClient",
    "RateLimiter",
    "ResponseCache",

    # Models
    "Message",
    "MessageRole",
    "LLMResponse",
    "ModelInfo",
    "ChatHistory",

    # Exceptions
    "AIMultitoolError",
    "APIError",
    "AuthenticationError",
    "RateLimitError",
    "QuotaExceededError",
    "ModelNotFoundError",
    "TimeoutError",
    "NetworkError",
    "ConfigurationError",
    "ValidationError",
    "FileOperationError",
    "CodeParsingError",
    "KeyringError",
    "MetricsError",
    "SanitizationError",
    "GitError",
    "ContextError",

    # RAG
    "DocumentIndexer",
    "Document",
    "EmbeddingModel",
    "OpenAIEmbeddings",
    "FakeEmbeddings",
    "DocumentChunker",
    "RecursiveCharacterChunker",
    "FixedSizeChunker",
    "SentenceChunker",
    "VectorStore",
    "InMemoryVectorStore",
    "SimilarityRetriever",

    # Code parsing
    "CodeParser",
    "CodeStructure",

    # Utilities
    "KeyManager",
    "ContentSanitizer",
    "SanitizationResult",
    "GitHelper",
    "SmartContextBuilder",
    "AnalysisContext",
    "MetricsCollector",
    "MetricsContext",
    "read_file",
    "read_directory",

    # Plugin interface
    "BasePlugin",
    "PluginConfig",
    "Provider",
    "ToolDefinition",
    "ToolRegistry",
    "ToolCategory",
    "PluginError",
    "ToolExecutionError",

    # Adapters
    "BaseAdapter",
    "ToolConverter",
    "ClaudeCodeAdapter",
    "create_claude_code_adapter",
    "DevinAdapter",
    "create_devin_adapter",

    # Advanced tools (base only)
    "AdvancedTool",
    "ToolResult",
    "ToolPipeline",
    "AdvancedToolConfig",
    "AdvancedSettings",
]
