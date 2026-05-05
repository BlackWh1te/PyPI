"""Adapters for integrating ai-multitool with specific CLI tools."""

from .base import BaseAdapter
from .utils import ToolConverter
from .claude_code import ClaudeCodeAdapter, create_claude_code_adapter
from .devin import DevinAdapter, create_devin_adapter

__all__ = [
    "BaseAdapter",
    "ToolConverter",
    "ClaudeCodeAdapter",
    "create_claude_code_adapter",
    "DevinAdapter",
    "create_devin_adapter",
]
