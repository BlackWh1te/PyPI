"""Base adapter class for CLI tool integration."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable

from ..plugins import BasePlugin, PluginConfig, ToolDefinition, ToolRegistry, ToolCategory
from ..core.llm_client import BaseLLMClient
from ..parsers.code_parser import CodeParser
from ..utils.git_utils import GitHelper
from ..utils.context_builder import SmartContextBuilder


class BaseAdapter(BasePlugin):
    """Base adapter class for CLI tool integration.

    Extends BasePlugin with common functionality for code analysis,
    git integration, and tool registration.
    """

    def __init__(self, config: PluginConfig):
        """Initialize the adapter.

        Args:
            config: Plugin configuration
        """
        super().__init__(config)
        self.tool_registry = ToolRegistry()
        self.code_parser = CodeParser() if config.enable_code_analysis else None
        self.git_helper = GitHelper() if config.enable_git_integration else None
        self.context_builder = SmartContextBuilder() if config.enable_code_analysis else None

        # Register default tools
        self._register_default_tools()

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
            List of tool definitions in CLI tool's format
        """
        pass

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
        try:
            return self.tool_registry.execute(tool_name, **kwargs)
        except KeyError as e:
            from ..plugins.exceptions import ToolNotFoundError
            raise ToolNotFoundError(tool_name) from e
        except Exception as e:
            from ..plugins.exceptions import ToolExecutionError
            raise ToolExecutionError(tool_name, str(e)) from e

    def _register_default_tools(self):
        """Register default tools based on configuration."""
        if self.config.enable_code_analysis:
            self._register_code_analysis_tools()

        if self.config.enable_git_integration:
            self._register_git_tools()

    def _register_code_analysis_tools(self):
        """Register code analysis tools."""

        def parse_code_file(file_path: str) -> Dict[str, Any]:
            """Parse a code file and return its structure."""
            if not self.code_parser:
                return {"error": "Code parser not enabled"}

            structure = self.code_parser.parse_file(file_path)
            return {
                "file_path": structure.file_path,
                "language": structure.language,
                "functions": structure.functions,
                "classes": structure.classes,
                "imports": structure.imports,
                "complexity_score": structure.complexity_score,
            }

        def analyze_code_context(file_path: str, include_git: bool = True) -> Dict[str, Any]:
            """Analyze code with full context."""
            if not self.context_builder:
                return {"error": "Context builder not enabled"}

            structure = self.code_parser.parse_file(file_path) if self.code_parser else None
            context = self.context_builder.build_context(
                file_path=file_path,
                structure=structure,
                include_git=include_git and bool(self.git_helper)
            )
            return context.to_dict() if hasattr(context, 'to_dict') else context

        self.tool_registry.register(ToolDefinition(
            name="parse_code",
            description="Parse a code file and extract its structure (functions, classes, imports)",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the code file to parse"
                    }
                },
                "required": ["file_path"]
            },
            handler=parse_code_file,
            category=ToolCategory.CODE_ANALYSIS,
            requires_auth=False,
            async_handler=False
        ))

        self.tool_registry.register(ToolDefinition(
            name="analyze_code",
            description="Analyze code with full context including git history and related files",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the code file to analyze"
                    },
                    "include_git": {
                        "type": "boolean",
                        "description": "Include git context",
                        "default": True
                    }
                },
                "required": ["file_path"]
            },
            handler=analyze_code_context,
            category=ToolCategory.CODE_ANALYSIS,
            requires_auth=False,
            async_handler=False
        ))

    def _register_git_tools(self):
        """Register git integration tools."""

        def get_git_info(repo_path: str = ".") -> Dict[str, Any]:
            """Get git repository information."""
            if not self.git_helper:
                return {"error": "Git helper not enabled"}

            return {
                "branch": self.git_helper.get_branch(repo_path),
                "commits": self.git_helper.get_recent_commits(repo_path, limit=5),
                "status": self.git_helper.get_status(repo_path),
            }

        self.tool_registry.register(ToolDefinition(
            name="get_git_info",
            description="Get git repository information (branch, commits, status)",
            parameters={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to the git repository",
                        "default": "."
                    }
                },
                "required": []
            },
            handler=get_git_info,
            category=ToolCategory.GIT,
            requires_auth=False,
            async_handler=False
        ))

    def register_custom_tool(self, tool: ToolDefinition):
        """Register a custom tool.

        Args:
            tool: Tool definition to register
        """
        self.tool_registry.register(tool)

    def get_tool_registry(self) -> ToolRegistry:
        """Get the tool registry.

        Returns:
            Tool registry instance
        """
        return self.tool_registry
