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
- Advanced performance analysis (profiling, optimization)
- Advanced database analysis (schema optimization)
- Advanced API design (REST, GraphQL, OpenAPI)
- Advanced cloud tools (Docker optimization)
- Advanced logging (log analysis, debugging)
- Advanced ML tools (model optimization)
- Advanced DevOps (CI/CD pipeline analysis)
- Advanced monitoring (alert optimization)
- Advanced mobile (app analysis)
- Advanced frontend (component analysis)
- Advanced crypto (key management)
- Advanced network (protocol analysis)
- Advanced data (pipeline optimization)

Individual advanced tools can be imported directly from their submodules when needed.
For example:
    from ai_multitool.advanced.code.refactoring import AdvancedCodeRefactoring
    from ai_multitool.advanced.git.commit_gen import AdvancedCommitGenerator
    from ai_multitool.advanced.performance.profiler import PerformanceProfiler
    from ai_multitool.advanced.database.schema_analyzer import SchemaAnalyzer
    from ai_multitool.advanced.devops.pipeline_analyzer import PipelineAnalyzer
    from ai_multitool.advanced.monitoring.alert_optimizer import AlertOptimizer
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
