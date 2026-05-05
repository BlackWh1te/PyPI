"""Advanced AI-powered tools for CLI integration.

This module provides advanced features including:
- Advanced code analysis (refactoring, bug detection, code smells)
- Advanced Git operations (commit generation, PR assistance)
- Advanced RAG (multi-modal, hybrid search, re-ranking)
- Advanced AI features (function calling, agents, workflows)
- Advanced security (secret scanning, vulnerability checking)
- Advanced testing (test generation, coverage analysis)
- Advanced documentation (auto-doc, API docs)
- Advanced project analysis (architecture, dependencies)
- Advanced collaboration (code review, issue triage)
"""

from .base import (
    AdvancedTool,
    ToolResult,
    ToolPipeline,
    AdvancedToolConfig,
    AdvancedSettings,
)

__all__ = [
    "AdvancedTool",
    "ToolResult",
    "ToolPipeline",
    "AdvancedToolConfig",
    "AdvancedSettings",
]
