"""Tool definitions and registry for plugin integration."""

from typing import Dict, Any, Callable, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class ToolCategory(str, Enum):
    """Categories for tools."""
    CODE_ANALYSIS = "code_analysis"
    RAG = "rag"
    GIT = "git"
    FILE_OPERATIONS = "file_operations"
    GENERAL = "general"


class ToolDefinition(BaseModel):
    """Definition of a tool that can be called by CLI tools."""
    name: str = Field(..., description="Unique name for the tool")
    description: str = Field(..., description="Human-readable description")
    parameters: Dict[str, Any] = Field(..., description="JSON Schema for parameters")
    handler: Callable = Field(..., description="Function to execute the tool")
    category: Optional[ToolCategory] = Field(default=ToolCategory.GENERAL, description="Tool category")
    requires_auth: bool = Field(default=False, description="Whether tool requires authentication")
    async_handler: bool = Field(default=False, description="Whether handler is async")

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ToolRegistry:
    """Registry for managing available tools."""

    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool.

        Args:
            tool: Tool definition to register

        Raises:
            ValueError: If tool with same name already exists
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' already registered")
        self._tools[tool.name] = tool

    def unregister(self, tool_name: str) -> None:
        """Unregister a tool.

        Args:
            tool_name: Name of tool to unregister
        """
        self._tools.pop(tool_name, None)

    def get(self, tool_name: str) -> Optional[ToolDefinition]:
        """Get a tool by name.

        Args:
            tool_name: Name of tool to get

        Returns:
            Tool definition or None if not found
        """
        return self._tools.get(tool_name)

    def list_tools(self, category: Optional[ToolCategory] = None) -> List[ToolDefinition]:
        """List all registered tools.

        Args:
            category: Optional category filter

        Returns:
            List of tool definitions
        """
        tools = list(self._tools.values())
        if category:
            tools = [t for t in tools if t.category == category]
        return tools

    def get_tool_names(self) -> List[str]:
        """Get list of all tool names.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def execute(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool by name.

        Args:
            tool_name: Name of tool to execute
            **kwargs: Tool arguments

        Returns:
            Tool execution result

        Raises:
            KeyError: If tool not found
        """
        tool = self.get(tool_name)
        if not tool:
            raise KeyError(f"Tool '{tool_name}' not found")

        if tool.async_handler:
            # Note: This is a simplified async handling
            # In production, you'd want proper async/await support
            import asyncio
            return asyncio.run(tool.handler(**kwargs))
        else:
            return tool.handler(**kwargs)

    def to_schema(self) -> Dict[str, Any]:
        """Export tools as a schema for CLI tool integration.

        Returns:
            Dictionary representation of all tools
        """
        return {
            tool.name: {
                "description": tool.description,
                "parameters": tool.parameters,
                "category": tool.category.value if tool.category else None,
                "requires_auth": tool.requires_auth,
            }
            for tool in self._tools.values()
        }
