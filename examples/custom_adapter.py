"""Custom adapter example for a hypothetical CLI tool."""

import asyncio
from ai_multitool import (
    BaseAdapter,
    PluginConfig,
    Provider,
    AnthropicClient,
    ToolDefinition,
    ToolCategory,
    ToolConverter,
)


class MyCLIAdapter(BaseAdapter):
    """Custom adapter for My CLI Tool."""

    def _create_llm_client(self):
        """Create Anthropic client."""
        return AnthropicClient(
            api_key=self.config.api_key,
            model=self.config.model,
            timeout=self.config.timeout,
            enable_cache=self.config.enable_cache,
        )

    def get_tool_definitions(self):
        """Return tool definitions in custom format."""
        tools = self.tool_registry.list_tools()
        # Convert to custom format
        custom_tools = []
        for tool in tools:
            custom_tools.append({
                "toolId": tool.name,
                "description": tool.description,
                "inputSchema": tool.parameters,
                "category": tool.category.value if tool.category else "general",
            })
        return custom_tools


async def main():
    """Custom adapter example."""
    # Create adapter
    config = PluginConfig(
        api_key="your-anthropic-api-key",
        provider=Provider.ANTHROPIC,
        model="claude-3-sonnet-20240229",
        enable_code_analysis=True,
        enable_git_integration=True,
    )

    adapter = MyCLIAdapter(config)

    # Add custom tool
    def my_custom_tool(message: str) -> dict:
        """Custom tool for my CLI."""
        return {"status": "processed", "message": message}

    custom_tool = ToolDefinition(
        name="my_custom_tool",
        description="My CLI's custom tool",
        parameters={
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            },
            "required": ["message"]
        },
        handler=my_custom_tool,
        category=ToolCategory.GENERAL,
    )

    adapter.register_custom_tool(custom_tool)

    # Get tools in custom format
    tools = adapter.get_tool_definitions()
    print(f"Available tools: {len(tools)}")
    for tool in tools:
        print(f"  - {tool['toolId']}: {tool['description']}")

    # Execute custom tool
    result = adapter.execute_tool("my_custom_tool", message="Hello from custom tool!")
    print(f"\nCustom tool result: {result}")

    # Chat with AI
    response = await adapter.chat("What can you do?")
    print(f"\nAI response: {response}")


if __name__ == "__main__":
    asyncio.run(main())
