"""Claude Code adapter for ai-multitool integration."""

from typing import List, Dict, Any, Optional
from ..adapters.base import BaseAdapter
from ..adapters.utils import ToolConverter
from ..plugins import PluginConfig, Provider
from ..core.llm_client import AnthropicClient, OpenAIClient
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class ClaudeCodeAdapter(BaseAdapter):
    """Adapter for integrating ai-multitool with Claude Code.

    This adapter provides tools in Claude Code's expected format and
    handles authentication through Claude Code's credential system.
    """

    def __init__(self, config: PluginConfig):
        """Initialize the Claude Code adapter.

        Args:
            config: Plugin configuration
        """
        super().__init__(config)
        self.tool_converter = ToolConverter()

    def _create_llm_client(self) -> AnthropicClient:
        """Create Anthropic client for Claude Code.

        Returns:
            Anthropic client instance
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
            raise ValueError(f"Unsupported provider for Claude Code: {self.config.provider}")

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return tool definitions in Claude Code format.

        Claude Code uses Anthropic's tool format.

        Returns:
            List of tool definitions in Anthropic format
        """
        tools = self.tool_registry.list_tools()
        return self.tool_converter.convert_tools(tools, target_format="anthropic")

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


def create_claude_code_adapter(
    api_key: str,
    model: str = "claude-3-sonnet-20240229",
    **kwargs
) -> ClaudeCodeAdapter:
    """Factory function to create a Claude Code adapter.

    Args:
        api_key: API key for Anthropic
        model: Model to use
        **kwargs: Additional configuration options

    Returns:
        Configured Claude Code adapter
    """
    config = PluginConfig(
        api_key=api_key,
        provider=Provider.ANTHROPIC,
        model=model,
        **kwargs
    )
    return ClaudeCodeAdapter(config)


# Example usage for Claude Code integration
if __name__ == "__main__":
    import asyncio

    async def example():
        # Create adapter
        adapter = create_claude_code_adapter(
            api_key="your-anthropic-api-key",
            model="claude-3-sonnet-20240229",
            enable_code_analysis=True,
            enable_git_integration=True,
        )

        # Get available tools
        tools = adapter.get_tool_definitions()
        logger.info(f"Available tools: {len(tools)}")
        for tool in tools:
            logger.debug(f"  - {tool['name']}: {tool['description']}")

        # Execute a tool
        result = adapter.execute_tool("parse_code", file_path="example.py")
        logger.info(f"Parse result: {result}")

        # Chat with AI
        response = await adapter.chat("What can you help me with?")
        logger.info(f"AI response: {response}")

    asyncio.run(example())
