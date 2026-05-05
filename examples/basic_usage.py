"""Basic usage example for ai-multitool library."""

import asyncio
from ai_multitool import AnthropicClient, Message, MessageRole


async def main():
    """Basic usage example."""
    # Create client
    client = AnthropicClient(
        api_key="your-anthropic-api-key",
        model="claude-3-sonnet-20240229"
    )

    # Simple chat
    response = await client.chat([
        Message(role=MessageRole.USER, content="Hello, how are you?")
    ])

    print(f"Response: {response.content}")
    print(f"Model: {response.model}")
    print(f"Tokens used: {response.tokens_used}")
    print(f"Latency: {response.latency_ms}ms")


if __name__ == "__main__":
    asyncio.run(main())
