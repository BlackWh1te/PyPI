"""Base adapter class for CLI tool integration."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable

from ..plugins import BasePlugin, PluginConfig, ToolDefinition, ToolRegistry, ToolCategory
from ..core.llm_client import BaseLLMClient
from ..parsers.code_parser import CodeParser
from ..utils.git_utils import GitHelper
from ..utils.context_builder import SmartContextBuilder
import time


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
    
    def register_advanced_tools(self, advanced_config: Optional[Dict] = None):
        """Register advanced AI tools.
        
        Args:
            advanced_config: Configuration for advanced tools
        """
        try:
            from ..advanced import (
                AdvancedCodeRefactoring,
                AdvancedBugDetection,
                AdvancedCodeSmellDetection,
                AdvancedComplexityAnalysis,
                AdvancedSecurityScan,
                AdvancedCommitGenerator,
                AdvancedPRAssistant,
                AdvancedConflictResolver,
                AdvancedBlameAnalyzer,
                AdvancedSecretScanner,
                AdvancedVulnChecker,
                AdvancedLicenseCheck,
            )
        except ImportError:
            # Advanced tools may not be available
            return
        
        # Register code analysis advanced tools
        if advanced_config and advanced_config.get("code_analysis", {}).get("enabled", False):
            self._register_advanced_code_tools()
        
        # Register Git advanced tools
        if advanced_config and advanced_config.get("git_operations", {}).get("enabled", False):
            self._register_advanced_git_tools()
        
        # Register security advanced tools
        if advanced_config and advanced_config.get("security", {}).get("enabled", False):
            self._register_advanced_security_tools()
    
    def _register_advanced_code_tools(self):
        """Register advanced code analysis tools."""
        from ..advanced.code import (
            AdvancedCodeRefactoring,
            AdvancedBugDetection,
            AdvancedCodeSmellDetection,
            AdvancedComplexityAnalysis,
            AdvancedSecurityScan,
        )
        
        # Register refactor_code tool
        self.tool_registry.register(ToolDefinition(
            name="refactor_code",
            description="AI-powered code refactoring with suggestions",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "aggressive": {"type": "boolean", "default": False}
                },
                "required": []
            },
            handler=lambda **kw: self._execute_advanced_tool("refactor_code", **kw),
            category=ToolCategory.CODE_ANALYSIS
        ))
        
        # Register detect_bugs tool
        self.tool_registry.register(ToolDefinition(
            name="detect_bugs",
            description="AI-powered bug detection with fix suggestions",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "severity": {"type": "string", "default": "all"}
                },
                "required": []
            },
            handler=lambda **kw: self._execute_advanced_tool("detect_bugs", **kw),
            category=ToolCategory.CODE_ANALYSIS
        ))
    
    def _register_advanced_git_tools(self):
        """Register advanced Git tools."""
        from ..advanced.git import (
            AdvancedCommitGenerator,
            AdvancedPRAssistant,
            AdvancedConflictResolver,
            AdvancedBlameAnalyzer,
        )
        
        # Register generate_commit tool
        self.tool_registry.register(ToolDefinition(
            name="generate_commit",
            description="Generate conventional commit messages",
            parameters={
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string", "default": "."},
                    "style": {"type": "string", "default": "conventional"}
                },
                "required": []
            },
            handler=lambda **kw: self._execute_advanced_tool("generate_commit", **kw),
            category=ToolCategory.GIT
        ))
    
    def _register_advanced_security_tools(self):
        """Register advanced security tools."""
        from ..advanced.security import (
            AdvancedSecretScanner,
            AdvancedVulnChecker,
            AdvancedLicenseCheck,
        )
        
        # Register scan_secrets tool
        self.tool_registry.register(ToolDefinition(
            name="scan_secrets",
            description="Scan for secrets and credentials",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "directory": {"type": "string"}
                },
                "required": []
            },
            handler=lambda **kw: self._execute_advanced_tool("scan_secrets", **kw),
            category=ToolCategory.GENERAL
        ))
    
    def _execute_advanced_tool(self, tool_name: str, **kwargs):
        """Execute an advanced tool.
        
        Args:
            tool_name: Name of the advanced tool
            **kwargs: Tool arguments
            
        Returns:
            Tool execution result
        """
        from ..advanced import (
            AdvancedCodeRefactoring,
            AdvancedBugDetection,
            AdvancedCommitGenerator,
            AdvancedSecretScanner,
        )
        
        # Map tool names to classes
        tool_classes = {
            "refactor_code": AdvancedCodeRefactoring,
            "detect_bugs": AdvancedBugDetection,
            "generate_commit": AdvancedCommitGenerator,
            "scan_secrets": AdvancedSecretScanner,
        }
        
        tool_class = tool_classes.get(tool_name)
        if not tool_class:
            raise ValueError(f"Unknown advanced tool: {tool_name}")
        
        # Create tool instance
        tool = tool_class(self.llm_client)
        
        # Execute (run in asyncio if needed)
        import asyncio
        if asyncio.iscoroutinefunction(tool.execute):
            return asyncio.run(tool.execute(**kwargs))
        else:
            return tool.execute(**kwargs)

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
