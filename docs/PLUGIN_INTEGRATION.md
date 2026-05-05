# Plugin Integration Guide

This guide explains how to integrate ai-multitool into your CLI tool.

## Architecture Overview

ai-multitool provides a plugin-based architecture:

```
Your CLI Tool
    ↓
Adapter (implements BasePlugin)
    ↓
ai-multitool Library
    ├── LLM Clients (Anthropic, OpenAI)
    ├── RAG System
    ├── Code Analysis
    ├── Git Integration
    └── Utilities
```

## Integration Steps

### Step 1: Install ai-multitool

```bash
pip install ai-multitool
```

### Step 2: Create an Adapter

Extend `BaseAdapter` to create an adapter for your CLI tool:

```python
from ai_multitool import BaseAdapter, PluginConfig, Provider
from ai_multitool import AnthropicClient, OpenAIClient

class MyCLIAdapter(BaseAdapter):
    """Adapter for My CLI Tool"""

    def _create_llm_client(self):
        """Create LLM client based on provider"""
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

    def get_tool_definitions(self):
        """Return tool definitions in your CLI tool's format"""
        tools = self.tool_registry.list_tools()
        # Convert to your CLI tool's expected format
        return [self._convert_to_my_format(t) for t in tools]

    def _convert_to_my_format(self, tool):
        """Convert ai-multitool tool to your CLI tool's format"""
        return {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
        }
```

### Step 3: Configure the Plugin

```python
from ai_multitool import PluginConfig, Provider

config = PluginConfig(
    api_key="your-api-key",
    provider=Provider.ANTHROPIC,
    model="claude-3-sonnet-20240229",
    max_tokens=4096,
    temperature=0.7,
    enable_cache=True,
    enable_code_analysis=True,
    enable_git_integration=True,
)

adapter = MyCLIAdapter(config)
```

### Step 4: Integrate with Your CLI Tool

#### Tool Registration

Register tools with your CLI tool's tool registry:

```python
# Get tool definitions
tools = adapter.get_tool_definitions()

# Register with your CLI tool
for tool in tools:
    my_cli_tool.register_tool(tool)
```

#### Tool Execution

Execute tools when called by your CLI tool:

```python
def handle_tool_call(tool_name, arguments):
    """Handle tool call from CLI tool"""
    try:
        result = adapter.execute_tool(tool_name, **arguments)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

#### Chat Integration

Integrate chat functionality:

```python
async def handle_chat(message, tools=None):
    """Handle chat request"""
    if tools:
        # Enable tool calling
        response = await adapter.chat_with_tools(
            message=message,
            tools=tools,
            system_prompt="You are a helpful AI assistant."
        )
    else:
        response = await adapter.chat(message)
    return response
```

## Tool Format Conversion

Different CLI tools expect different tool definition formats. Use `ToolConverter`:

```python
from ai_multitool import ToolConverter

# OpenAI format (used by Devin, some others)
openai_tools = ToolConverter.convert_tools(tools, target_format="openai")

# Anthropic format (used by Claude Code)
anthropic_tools = ToolConverter.convert_tools(tools, target_format="anthropic")

# Generic format
generic_tools = ToolConverter.convert_tools(tools, target_format="generic")
```

## Custom Tools

Add custom tools specific to your CLI tool:

```python
from ai_multitool import ToolDefinition, ToolCategory

def my_custom_tool(param: str) -> dict:
    """Custom tool for my CLI tool"""
    return {"result": f"Processed: {param}"}

tool = ToolDefinition(
    name="my_custom_tool",
    description="My CLI tool's custom functionality",
    parameters={
        "type": "object",
        "properties": {
            "param": {
                "type": "string",
                "description": "Input parameter"
            }
        },
        "required": ["param"]
    },
    handler=my_custom_tool,
    category=ToolCategory.GENERAL,
    requires_auth=False,
)

adapter.register_custom_tool(tool)
```

## RAG Integration

Enable RAG for document-aware responses:

```python
from ai_multitool import (
    OpenAIEmbeddingModel,
    InMemoryVectorStore,
    Document,
)

# Setup RAG components
embedding_model = OpenAIEmbeddingModel(api_key="openai-key")
vector_store = InMemoryVectorStore(dimension=1536)

# Index your documentation
adapter.enable_rag(embedding_model, vector_store)

# Add documents
indexer = adapter.rag_indexer
indexer.add_document(Document(
    text="Your CLI tool's documentation...",
    doc_id="docs_1",
    metadata={"source": "README.md"}
))
```

## Authentication

### Using API Keys Directly

```python
config = PluginConfig(
    api_key="your-api-key",
    provider=Provider.ANTHROPIC,
    model="claude-3-sonnet-20240229",
)
```

### Using Keyring

```python
from ai_multitool import KeyManager

key_manager = KeyManager()
api_key = key_manager.get_key("anthropic")

config = PluginConfig(
    api_key=api_key,
    provider=Provider.ANTHROPIC,
)
```

### Environment Variables

```bash
export ANTHROPIC_API_KEY=your-key
export OPENAI_API_KEY=your-key
```

```python
import os
from ai_multitool import PluginConfig

config = PluginConfig(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    provider=Provider.ANTHROPIC,
)
```

## Error Handling

Handle plugin errors gracefully:

```python
from ai_multitool import (
    PluginError,
    ToolExecutionError,
    ToolNotFoundError,
    AuthenticationError,
    RateLimitError,
)

try:
    result = adapter.execute_tool("parse_code", file_path="main.py")
except AuthenticationError as e:
    # Handle authentication failure
    print(f"Authentication failed: {e}")
except RateLimitError as e:
    # Handle rate limiting
    print(f"Rate limited: {e}")
except ToolNotFoundError as e:
    # Handle unknown tool
    print(f"Tool not found: {e.tool_name}")
except ToolExecutionError as e:
    # Handle tool execution failure
    print(f"Tool execution failed: {e.reason}")
except PluginError as e:
    # Handle general plugin errors
    print(f"Plugin error: {e.message}")
```

## Metrics Collection

Track usage with metrics:

```python
from ai_multitool import MetricsCollector, MetricsContext

collector = MetricsCollector()

# Wrap operations with metrics context
with MetricsContext(collector, "chat"):
    response = await adapter.chat("Hello")

# Get statistics
stats = collector.get_stats()
print(f"Total calls: {stats['total_calls']}")
print(f"Average latency: {stats['avg_latency_ms']}ms")
```

## Testing Your Integration

### Unit Tests

```python
import pytest
from ai_multitool import PluginConfig, Provider
from my_adapter import MyCLIAdapter

@pytest.fixture
def adapter():
    config = PluginConfig(
        api_key="test-key",
        provider=Provider.ANTHROPIC,
        model="claude-3-sonnet-20240229",
    )
    return MyCLIAdapter(config)

def test_tool_execution(adapter):
    result = adapter.execute_tool("parse_code", file_path="test.py")
    assert "language" in result
```

### Integration Tests

```python
async def test_chat_integration(adapter):
    response = await adapter.chat("Hello")
    assert response is not None
    assert len(response) > 0
```

## Best Practices

1. **Configuration Management**
   - Use environment variables for API keys
   - Provide sensible defaults
   - Validate configuration on startup

2. **Error Handling**
   - Catch and handle specific exceptions
   - Provide user-friendly error messages
   - Log errors for debugging

3. **Tool Design**
   - Keep tools focused and single-purpose
   - Provide clear descriptions
   - Validate input parameters

4. **Performance**
   - Enable caching for repeated calls
   - Use streaming for long responses
   - Monitor metrics for optimization

5. **Security**
   - Never log API keys
   - Use keyring for credential storage
   - Sanitize sensitive data

## Example: Full Integration

```python
import os
from ai_multitool import (
    BaseAdapter,
    PluginConfig,
    Provider,
    AnthropicClient,
    ToolConverter,
    MetricsCollector,
)

class MyCLIAdapter(BaseAdapter):
    def __init__(self, api_key=None):
        config = PluginConfig(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
            provider=Provider.ANTHROPIC,
            model="claude-3-sonnet-20240229",
            enable_code_analysis=True,
            enable_git_integration=True,
        )
        super().__init__(config)
        self.metrics = MetricsCollector()

    def _create_llm_client(self):
        return AnthropicClient(
            api_key=self.config.api_key,
            model=self.config.model,
            timeout=self.config.timeout,
            enable_cache=self.config.enable_cache,
        )

    def get_tool_definitions(self):
        tools = self.tool_registry.list_tools()
        # Convert to my CLI tool's format
        return ToolConverter.convert_tools(tools, target_format="generic")

    async def chat_with_metrics(self, message):
        with MetricsContext(self.metrics, "chat"):
            return await self.chat(message)

# Usage
adapter = MyCLIAdapter()
tools = adapter.get_tool_definitions()

# Register with CLI tool
for tool in tools:
    register_tool_with_cli(tool)

# Handle tool calls
def on_tool_call(tool_name, args):
    try:
        with MetricsContext(adapter.metrics, f"tool_{tool_name}"):
            result = adapter.execute_tool(tool_name, **args)
        return result
    except Exception as e:
        handle_error(e)
```

## Troubleshooting

### Import Errors

If you get import errors:
```bash
pip install -e ai-multitool
```

### Authentication Errors

Check your API key is valid:
```python
from ai_multitool import KeyManager
key_manager = KeyManager()
key = key_manager.get_key("anthropic")
print(f"Key set: {bool(key)}")
```

### Tool Not Found

Ensure tools are registered:
```python
print(adapter.get_tool_registry().get_tool_names())
```

### Performance Issues

Enable caching and check metrics:
```python
config = PluginConfig(..., enable_cache=True)
stats = adapter.metrics.get_stats()
print(stats)
```

## Support

For issues specific to your integration:
1. Check the error messages
2. Review this guide
3. Check the main README
4. Open a GitHub issue with details
