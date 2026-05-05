# ai-multitool

AI-powered multitool library for CLI tool integration. Provides a comprehensive set of AI capabilities that can be integrated into various CLI tools (Claude Code, Devin, OpenCode, Gemini CLI, Qwen CLI, etc.).

## Overview

ai-multitool is designed as a **Python library** for CLI tool developers, not as a standalone end-user tool. It provides:

- **Multi-Model LLM Support**: Anthropic, OpenAI, and LiteLLM integration
- **RAG (Retrieval-Augmented Generation)**: Document indexing and semantic search
- **Code Analysis**: Tree-sitter based code parsing and structure extraction
- **Git Integration**: Repository context and history
- **Smart Context**: Intelligent context building for better AI responses
- **Secure Key Management**: System keyring integration
- **Content Sanitization**: Automatic sensitive data redaction
- **Metrics Collection**: Usage tracking and analytics

## Installation

```bash
pip install ai-multitool
```

Or install from source:

```bash
git clone https://github.com/BlackWh1te/PyPI.git
cd PyPi
pip install -e .
```

## Quick Start for Plugin Developers

### Basic Usage

```python
from ai_multitool import AnthropicClient, Message, MessageRole

# Create client
client = AnthropicClient(
    api_key="your-api-key",
    model="claude-3-sonnet-20240229"
)

# Make request
response = await client.chat([
    Message(role=MessageRole.USER, content="Hello!")
])
print(response.content)
```

### Using with Pre-built Adapters

#### Claude Code Integration

```python
from ai_multitool import create_claude_code_adapter

# Create adapter
adapter = create_claude_code_adapter(
    api_key="your-anthropic-api-key",
    model="claude-3-sonnet-20240229",
    enable_code_analysis=True,
    enable_git_integration=True,
)

# Get available tools
tools = adapter.get_tool_definitions()

# Execute a tool
result = adapter.execute_tool("parse_code", file_path="main.py")

# Chat with AI
response = await adapter.chat("Analyze this code")
```

#### Devin Integration

```python
from ai_multitool import create_devin_adapter

# Create adapter
adapter = create_devin_adapter(
    api_key="your-api-key",
    provider="anthropic",
    model="claude-3-sonnet-20240229",
    enable_code_analysis=True,
)

# Get tools in OpenAI format
tools = adapter.get_tool_definitions()
```

### Creating Custom Adapters

```python
from ai_multitool import BaseAdapter, PluginConfig, Provider
from ai_multitool import AnthropicClient

class MyCLIAdapter(BaseAdapter):
    def _create_llm_client(self):
        return AnthropicClient(
            api_key=self.config.api_key,
            model=self.config.model,
            timeout=self.config.timeout,
            enable_cache=self.config.enable_cache,
        )

    def get_tool_definitions(self):
        # Return tools in your CLI tool's format
        tools = self.tool_registry.list_tools()
        return [self._convert_to_my_format(t) for t in tools]

# Usage
config = PluginConfig(
    api_key="your-key",
    provider=Provider.ANTHROPIC,
    model="claude-3-sonnet-20240229"
)
adapter = MyCLIAdapter(config)
```

## Library API

### Core LLM

```python
from ai_multitool import (
    BaseLLMClient,
    AnthropicClient,
    OpenAIClient,
    Message,
    MessageRole,
    LLMResponse,
    ChatHistory,
)
```

### RAG (Retrieval-Augmented Generation)

```python
from ai_multitool import (
    DocumentIndexer,
    Document,
    EmbeddingModel,
    OpenAIEmbeddingModel,
    VectorStore,
    InMemoryVectorStore,
    SimilarityRetriever,
    DocumentChunker,
    RecursiveCharacterChunker,
)
```

### Code Analysis

```python
from ai_multitool import (
    CodeParser,
    CodeStructure,
    SmartContextBuilder,
    AnalysisContext,
)
```

### Utilities

```python
from ai_multitool import (
    KeyManager,
    ContentSanitizer,
    GitHelper,
    MetricsCollector,
)
```

### Plugin Interface

```python
from ai_multitool import (
    BasePlugin,
    PluginConfig,
    ToolDefinition,
    ToolRegistry,
    BaseAdapter,
    ToolConverter,
)
```

## Plugin Development

### Creating a Custom Plugin

Extend `BasePlugin` to create a custom plugin:

```python
from ai_multitool import BasePlugin, PluginConfig, ToolDefinition, ToolCategory

class MyPlugin(BasePlugin):
    def _create_llm_client(self):
        # Create and return your LLM client
        pass

    def get_tool_definitions(self):
        # Return tool definitions in your CLI tool's format
        return []

    def execute_tool(self, tool_name, **kwargs):
        # Execute tools
        pass
```

### Registering Custom Tools

```python
from ai_multitool import ToolDefinition, ToolCategory

def my_tool(param: str) -> dict:
    return {"result": f"Processed: {param}"}

tool = ToolDefinition(
    name="my_tool",
    description="My custom tool",
    parameters={
        "type": "object",
        "properties": {
            "param": {"type": "string"}
        },
        "required": ["param"]
    },
    handler=my_tool,
    category=ToolCategory.GENERAL
)

adapter.register_custom_tool(tool)
```

### Tool Format Conversion

```python
from ai_multitool import ToolConverter

# Convert to different formats
openai_format = ToolConverter.to_openai_function(tool)
anthropic_format = ToolConverter.to_anthropic_tool(tool)
generic_format = ToolConverter.to_generic_schema(tool)
```

## Configuration

### PluginConfig Options

```python
from ai_multitool import PluginConfig, Provider

config = PluginConfig(
    api_key="your-api-key",
    provider=Provider.ANTHROPIC,
    model="claude-3-sonnet-20240229",
    max_tokens=4096,
    temperature=0.7,
    enable_cache=True,
    enable_rag=False,
    enable_code_analysis=True,
    enable_git_integration=True,
    timeout=120,
)
```

### Environment Variables

```bash
# API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key

# Model Settings
DEFAULT_MODEL=claude-3-sonnet-20240229
MAX_TOKENS=4096
TEMPERATURE=0.7
```

## Advanced Features

### RAG Integration

```python
from ai_multitool import (
    DocumentIndexer,
    Document,
    OpenAIEmbeddingModel,
    InMemoryVectorStore,
)

# Setup RAG
embedding_model = OpenAIEmbeddingModel(api_key="openai-key")
vector_store = InMemoryVectorStore(dimension=1536)
indexer = DocumentIndexer(
    embedding_model=embedding_model,
    vector_store=vector_store
)

# Index documents
indexer.add_document(Document(
    text="Your documentation...",
    doc_id="doc1",
    metadata={"source": "README.md"}
))

# Enable in adapter
adapter.enable_rag(embedding_model, vector_store)
```

### Code Analysis

```python
from ai_multitool import CodeParser, SmartContextBuilder

parser = CodeParser()
structure = parser.parse_file("main.py")

context_builder = SmartContextBuilder()
context = context_builder.build_context(
    file_path="main.py",
    structure=structure,
    include_git=True
)
```

### Metrics Collection

```python
from ai_multitool import MetricsCollector, MetricsContext

collector = MetricsCollector()

with MetricsContext(collector, "chat"):
    response = await client.chat(messages)

stats = collector.get_stats()
```

## Supported CLI Tools

- ✅ Claude Code
- ✅ Devin
- 🚧 OpenCode (coming soon)
- 🚧 Gemini CLI (coming soon)
- 🚧 Qwen CLI (coming soon)

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Code Style

```bash
black ai_multitool/
ruff check ai_multitool/
mypy ai_multitool/
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please read CONTRIBUTING.md for details.

## Support

For issues and questions, please use the GitHub issue tracker.
