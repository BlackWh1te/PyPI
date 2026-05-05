"""
ai-multitool: Developer tools library for CLI integration

This library provides 95+ developer tools that can be integrated into
various AI CLI tools (Claude Code, Devin, OpenCode, Gemini CLI, Qwen CLI, etc.).

The tools work standalone and can be called from your AI CLI via adapters.

Example usage:
    from ai_multitool.advanced.api_testing import APITester
    from ai_multitool.adapters import create_claude_code_adapter

    # Use tools directly
    tester = APITester()
    result = tester.test_api("https://api.example.com")

    # Or use with AI CLI via adapter
    adapter = create_claude_code_adapter()
    tools = adapter.get_tools()
"""

__version__ = "0.5.1"

# Core exceptions (needed by tools)
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

# Plugin interface (for tool definitions)
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

# Adapters (for CLI integration)
from .adapters import (
    BaseAdapter,
    ToolConverter,
    ClaudeCodeAdapter,
    create_claude_code_adapter,
    DevinAdapter,
    create_devin_adapter,
    OpenCodeAdapter,
    create_opencode_adapter,
    GeminiAdapter,
    create_gemini_adapter,
    QwenAdapter,
    create_qwen_adapter,
)

# Advanced tools (base classes)
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
    "OpenCodeAdapter",
    "create_opencode_adapter",
    "GeminiAdapter",
    "create_gemini_adapter",
    "QwenAdapter",
    "create_qwen_adapter",

    # Advanced tools (base classes)
    "AdvancedTool",
    "ToolResult",
    "ToolPipeline",
    "AdvancedToolConfig",
    "AdvancedSettings",
]
