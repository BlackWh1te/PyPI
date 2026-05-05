"""Adapters for integrating ai-multitool with specific CLI tools."""

from .base import BaseAdapter
from .utils import ToolConverter
from .claude_code import ClaudeCodeAdapter, create_claude_code_adapter
from .devin import DevinAdapter, create_devin_adapter
from .opencode import OpenCodeAdapter, create_opencode_adapter
from .gemini import GeminiAdapter, create_gemini_adapter
from .qwen import QwenAdapter, create_qwen_adapter

__all__ = [
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
]
