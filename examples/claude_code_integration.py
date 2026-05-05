"""Claude Code integration example."""

import asyncio
from ai_multitool import create_claude_code_adapter


async def main():
    """Claude Code integration example."""
    # Create adapter
    adapter = create_claude_code_adapter(
        api_key="your-anthropic-api-key",
        model="claude-3-sonnet-20240229",
        enable_code_analysis=True,
        enable_git_integration=True,
    )

    # Get available tools
    tools = adapter.get_tool_definitions()
    print(f"Available tools: {len(tools)}")
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")

    # Execute a tool
    try:
        result = adapter.execute_tool("parse_code", file_path="example.py")
        print(f"\nParse result: {result}")
    except Exception as e:
        print(f"Tool execution error: {e}")

    # Chat with AI
    try:
        response = await adapter.chat("What can you help me with?")
        print(f"\nAI response: {response}")
    except Exception as e:
        print(f"Chat error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
