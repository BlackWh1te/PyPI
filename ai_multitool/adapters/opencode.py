"""OpenCode adapter for ai-multitool integration."""

from typing import List, Dict, Any, Optional
from ..adapters.base import BaseAdapter
from ..adapters.utils import ToolConverter
from ..plugins import PluginConfig, Provider
from ..core.llm_client import AnthropicClient, OpenAIClient
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class OpenCodeAdapter(BaseAdapter):
    """Adapter for integrating ai-multitool with OpenCode CLI.

    This adapter provides tools in OpenCode's expected format and
    handles authentication through OpenCode's credential system.
    """

    def __init__(self, config: PluginConfig):
        """Initialize the OpenCode adapter.

        Args:
            config: Plugin configuration
        """
        super().__init__(config)
        self.tool_converter = ToolConverter()

    def _create_llm_client(self) -> AnthropicClient:
        """Create LLM client for OpenCode.

        OpenCode can use either Anthropic or OpenAI.

        Returns:
            LLM client instance
        """
        if self.config.provider == Provider.ANTHROPIC:
            return AnthropicClient(
                api_key=self.config.api_key,
                model=self.config.model,
                timeout=self.config.timeout,
                enable_cache=self.config.enable_cache,
            )
        elif self.config.provider == Provider.OPENAI:
            return OpenAIClient(
                api_key=self.config.api_key,
                model=self.config.model,
                timeout=self.config.timeout,
                enable_cache=self.config.enable_cache,
            )
        else:
            raise ValueError(f"Unsupported provider for OpenCode: {self.config.provider}")

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return tool definitions in OpenCode format.

        OpenCode uses OpenAI's function format.

        Returns:
            List of tool definitions in OpenAI format
        """
        tools = self.tool_registry.list_tools()
        return self.tool_converter.convert_tools(tools, target_format="openai")

    def get_tool_definitions_schema(self) -> Dict[str, Any]:
        """Get tool definitions as a schema dictionary.

        Returns:
            Dictionary mapping tool names to their definitions
        """
        return self.tool_registry.to_schema()

    async def chat_with_tools(
        self,
        message: str,
        tools: Optional[List[str]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Send a chat message with optional tool usage.

        Args:
            message: User message
            tools: Optional list of tool names to make available
            system_prompt: Optional system prompt

        Returns:
            LLM response text
        """
        # Note: This is a simplified implementation
        # In production, you'd want full tool-calling support
        return await self.chat(message, system_prompt=system_prompt)

    def execute_opencode_command(self, command: str, **kwargs) -> Any:
        """Execute an OpenCode-specific command.

        Args:
            command: Command to execute
            **kwargs: Command arguments

        Returns:
            Command result
        """
        # This can be extended with OpenCode-specific commands
        return self.execute_tool(command, **kwargs)


def create_opencode_adapter(
    api_key: str,
    provider: str = "anthropic",
    model: str = "claude-3-sonnet-20240229",
    **kwargs
) -> OpenCodeAdapter:
    """Factory function to create an OpenCode adapter.

    Args:
        api_key: API key for the provider
        provider: Provider to use ("anthropic" or "openai")
        model: Model to use
        **kwargs: Additional configuration options

    Returns:
        Configured OpenCode adapter
    """
    config = PluginConfig(
        api_key=api_key,
        provider=Provider(provider),
        model=model,
        **kwargs
    )
    return OpenCodeAdapter(config)


# Example usage for OpenCode integration
if __name__ == "__main__":
    import asyncio

    async def example():
        # Create adapter with Anthropic
        adapter = create_opencode_adapter(
            api_key="your-anthropic-api-key",
            provider="anthropic",
            model="claude-3-sonnet-20240229",
            enable_code_analysis=True,
            enable_git_integration=True,
        )

        # Get available tools
        tools = adapter.get_tool_definitions()
        logger.info(f"Available tools: {len(tools)}")
        for tool in tools:
            logger.debug(f"  - {tool['function']['name']}: {tool['function']['description']}")

        # Execute a tool
        result = adapter.execute_tool("parse_code", file_path="example.py")
        logger.info(f"Parse result: {result}")

        # Chat with AI
        response = await adapter.chat("What can you help me with?")
        logger.info(f"AI response: {response}")

    asyncio.run(example())
