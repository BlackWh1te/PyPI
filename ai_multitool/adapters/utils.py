"""Utilities for adapter implementations."""

from typing import Dict, Any, List
from ..plugins import ToolDefinition, ToolCategory


class ToolConverter:
    """Converter for transforming tool definitions between formats.

    Different CLI tools may expect different tool definition formats.
    This class provides conversion utilities.
    """

    @staticmethod
    def to_openai_function(tool: ToolDefinition) -> Dict[str, Any]:
        """Convert tool definition to OpenAI function format.

        Args:
            tool: Tool definition to convert

        Returns:
            OpenAI function format
        """
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            }
        }

    @staticmethod
    def to_anthropic_tool(tool: ToolDefinition) -> Dict[str, Any]:
        """Convert tool definition to Anthropic tool format.

        Args:
            tool: Tool definition to convert

        Returns:
            Anthropic tool format
        """
        return {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.parameters,
        }

    @staticmethod
    def to_generic_schema(tool: ToolDefinition) -> Dict[str, Any]:
        """Convert tool definition to generic schema format.

        Args:
            tool: Tool definition to convert

        Returns:
            Generic schema format
        """
        return {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
            "category": tool.category.value if tool.category else "general",
            "requires_auth": tool.requires_auth,
        }

    @staticmethod
    def convert_tools(
        tools: List[ToolDefinition],
        target_format: str = "generic"
    ) -> List[Dict[str, Any]]:
        """Convert multiple tools to a target format.

        Args:
            tools: List of tool definitions
            target_format: Target format ("openai", "anthropic", "generic")

        Returns:
            List of converted tool definitions

        Raises:
            ValueError: If target format is not supported
        """
        converters = {
            "openai": ToolConverter.to_openai_function,
            "anthropic": ToolConverter.to_anthropic_tool,
            "generic": ToolConverter.to_generic_schema,
        }

        if target_format not in converters:
            raise ValueError(f"Unsupported target format: {target_format}")

        converter = converters[target_format]
        return [converter(tool) for tool in tools]

    @staticmethod
    def filter_tools_by_category(
        tools: List[ToolDefinition],
        category: ToolCategory
    ) -> List[ToolDefinition]:
        """Filter tools by category.

        Args:
            tools: List of tool definitions
            category: Category to filter by

        Returns:
            Filtered list of tools
        """
        return [t for t in tools if t.category == category]
