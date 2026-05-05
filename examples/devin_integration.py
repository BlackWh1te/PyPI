"""Devin integration example."""

import asyncio
from ai_multitool import create_devin_adapter


async def main():
    """Devin integration example."""
    # Create adapter with Anthropic
    adapter = create_devin_adapter(
        api_key="your-anthropic-api-key",
        provider="anthropic",
        model="claude-3-sonnet-20240229",
        enable_code_analysis=True,
        enable_git_integration=True,
    )

    # Get available tools in OpenAI format
    tools = adapter.get_tool_definitions()
    print(f"Available tools: {len(tools)}")
    for tool in tools:
        print(f"  - {tool['function']['name']}: {tool['function']['description']}")

    # Execute a tool
    try:
        result = adapter.execute_tool("parse_code", file_path="example.py")
        print(f"\nParse result: {result}")
    except Exception as e:
        print(f"Tool execution error: {e}")

    # Chat with AI
    try:
        response = await adapter.chat("Analyze this codebase")
        print(f"\nAI response: {response}")
    except Exception as e:
        print(f"Chat error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
