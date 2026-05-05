# ai-multitool Public API Design

## Overview
ai-multitool is designed as a Python library that can be integrated into various CLI tools (Claude Code, Devin, OpenCode, Gemini CLI, Qwen CLI, etc.) to provide AI-powered multitool capabilities.

## Public API Surface

### Core LLM Functionality
```python
from ai_multitool import (
    # LLM Clients
    BaseLLMClient,
    AnthropicClient,
    OpenAIClient,

    # Models
    Message,
    MessageRole,
    LLMResponse,
    ModelInfo,
    ChatHistory,

    # Exceptions
    AIMultitoolError,
    APIError,
    AuthenticationError,
    RateLimitError,
)
```

### RAG (Retrieval-Augmented Generation)
```python
from ai_multitool.rag import (
    # Core RAG
    DocumentIndexer,
    Document,
    DocumentChunk,

    # Embeddings
    EmbeddingModel,
    OpenAIEmbeddingModel,

    # Chunkers
    DocumentChunker,
    RecursiveCharacterChunker,
    FixedSizeChunker,

    # Vector Store
    VectorStore,
    InMemoryVectorStore,

    # Retrieval
    SimilarityRetriever,
)
```

### Code Analysis
```python
from ai_multitool.parsers import (
    CodeParser,
    CodeStructure,
)

from ai_multitool.utils import (
    SmartContextBuilder,
    AnalysisContext,
)
```

### Utilities
```python
from ai_multitool.utils import (
    # Key Management
    KeyManager,

    # Content Sanitization
    ContentSanitizer,
    SanitizationResult,

    # Git Integration
    GitHelper,

    # Metrics
    MetricsCollector,
    MetricsContext,
)
```

### Plugin Interface
```python
from ai_multitool.plugins import (
    # Base Plugin
    BasePlugin,
    PluginConfig,

    # Tool Registry
    ToolRegistry,
    ToolDefinition,
)
```

## Plugin Interface Design

### BasePlugin
Abstract base class that CLI tools should implement to integrate ai-multitool:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BasePlugin(ABC):
    """Base class for ai-multitool plugins for CLI tools."""

    def __init__(self, config: PluginConfig):
        self.config = config
        self.llm_client = self._create_llm_client()
        self.rag_indexer = None

    @abstractmethod
    def _create_llm_client(self) -> BaseLLMClient:
        """Create and configure LLM client for the CLI tool."""
        pass

    @abstractmethod
    def get_tool_definitions(self) -> List[ToolDefinition]:
        """Return list of tools available to the CLI tool."""
        pass

    @abstractmethod
    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool by name."""
        pass

    def enable_rag(self, embedding_model: EmbeddingModel, vector_store: VectorStore):
        """Enable RAG capabilities."""
        self.rag_indexer = DocumentIndexer(
            embedding_model=embedding_model,
            vector_store=vector_store
        )
```

### ToolDefinition
Schema for tool definitions:

```python
from pydantic import BaseModel
from typing import Dict, Any, Optional

class ToolDefinition(BaseModel):
    """Definition of a tool that can be called by CLI tools."""
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema for parameters
    handler: callable
    category: Optional[str] = None
    requires_auth: bool = False
```

### PluginConfig
Configuration for plugin:

```python
class PluginConfig(BaseModel):
    """Configuration for ai-multitool plugin."""
    api_key: str
    provider: str  # "anthropic" or "openai"
    model: str
    max_tokens: int = 4096
    temperature: float = 0.7
    enable_cache: bool = True
    enable_rag: bool = False
    enable_code_analysis: bool = True
    enable_git_integration: bool = True
```

## Usage Examples

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

### With RAG
```python
from ai_multitool import AnthropicClient
from ai_multitool.rag import DocumentIndexer, Document, OpenAIEmbeddingModel, InMemoryVectorStore

# Setup RAG
embedding_model = OpenAIEmbeddingModel(api_key="openai-key")
vector_store = InMemoryVectorStore(dimension=1536)
indexer = DocumentIndexer(
    embedding_model=embedding_model,
    vector_store=vector_store
)

# Index documents
indexer.add_document(Document(
    text="Your documentation here...",
    doc_id="doc1",
    metadata={"source": "README.md"}
))

# Retrieve and use in chat
retriever = SimilarityRetriever(vector_store)
context = retriever.retrieve("user query", top_k=3)
```

### Code Analysis
```python
from ai_multitool.parsers import CodeParser
from ai_multitool.utils import SmartContextBuilder

parser = CodeParser()
structure = parser.parse_file("main.py")

context_builder = SmartContextBuilder()
context = context_builder.build_context(
    file_path="main.py",
    structure=structure,
    include_git=True
)
```

## Adapter Pattern for CLI Tools

Each CLI tool (Claude Code, Devin, etc.) should create an adapter that:

1. Implements `BasePlugin`
2. Converts CLI tool's tool calling format to ai-multitool's format
3. Handles authentication using CLI tool's credential system
4. Provides tool definitions in the CLI tool's expected format

Example adapter structure:
```
ai_multitool/adapters/
  ├── __init__.py
  ├── claude_code.py
  ├── devin.py
  ├── opencode.py
  ├── gemini_cli.py
  └── qwen_cli.py
```
