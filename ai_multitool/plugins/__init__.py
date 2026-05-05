"""Plugin interface for integrating ai-multitool with CLI tools."""

from .base import BasePlugin, PluginConfig
from .tools import ToolDefinition, ToolRegistry
from .exceptions import PluginError, ToolExecutionError

__all__ = [
    "BasePlugin",
    "PluginConfig",
    "ToolDefinition",
    "ToolRegistry",
    "PluginError",
    "ToolExecutionError",
]
