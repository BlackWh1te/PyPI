"""Plugin interface for integrating ai-multitool with CLI tools."""

from .base import BasePlugin, PluginConfig, Provider
from .tools import ToolDefinition, ToolRegistry, ToolCategory
from .exceptions import PluginError, ToolExecutionError

__all__ = [
    "BasePlugin",
    "PluginConfig",
    "Provider",
    "ToolDefinition",
    "ToolRegistry",
    "ToolCategory",
    "PluginError",
    "ToolExecutionError",
]
