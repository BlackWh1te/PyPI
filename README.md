# ai-multitool

AI-powered CLI multitool for developers. A unified interface for interacting with multiple AI models (Claude, GPT, etc.) with advanced features like code analysis, RAG, and more.

## Features

### ✅ Core Features (v0.1.0)
- 🤖 **Multi-Model Support**: Interact with Claude and GPT via a single CLI
- 💬 **Chat Interface**: Natural language conversations with AI models
- 🔄 **Streaming Support**: Real-time streaming responses
- ⚡ **Caching**: Response caching for faster repeated queries
- 🛡️ **Retry Logic**: Automatic retry with exponential backoff
- 🚦 **Rate Limiting**: Token bucket rate limiting
- 🎨 **Beautiful Output**: Rich terminal UI with progress indicators
- ⚙️ **Configurable**: Environment-based configuration with Pydantic

### ✅ Advanced Features (v0.1.0+)
- 📁 **Code Analysis**: Analyze files and directories with AI
- 🔍 **Code Parsing**: Tree-sitter based code structure extraction
- 🌳 **Git Integration**: Repository context and history
- 🧠 **Smart Context**: Intelligent context building for better analysis
- 🔐 **Secure Key Management**: System keyring for API keys
- 🛡️ **Content Sanitization**: Automatic sensitive data redaction
- 📊 **Metrics Collection**: Usage tracking and statistics
- 🧠 **RAG (Retrieval-Augmented Generation)**: Document indexing and semantic search
- 📚 **Document Indexing**: Index your docs for context-aware AI responses

## Installation

```bash
# Clone the repository
git clone https://github.com/BlackWh1te/PyPI.git
cd PyPi

# Install in development mode
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

## Quick Start

```bash
# Check version
ai-multitool version

# List available models
ai-multitool list-models

# View configuration
ai-multitool config

# Set API keys securely
ai-multitool keys set anthropic
ai-multitool keys set openai

# Chat with AI
ai-multitool chat "Hello, how are you?"
ai-multitool chat "Explain Python decorators" --provider anthropic
ai-multitool chat "What is the capital of France?" --provider openai --stream
```

## Configuration

Create a `.env` file in your project root:

```env
# API Keys (or use 'ai-multitool keys set' for secure storage)
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key

# Model Settings
DEFAULT_MODEL=claude-3-sonnet-20240229
MAX_TOKENS=4096
TEMPERATURE=0.7

# CLI Settings
OUTPUT_FORMAT=rich
LOG_LEVEL=INFO
```

## Usage Examples

### Chat with AI

```bash
# Basic chat
ai-multitool chat "Write a Python function to sort a list"

# Specify provider
ai-multitool chat "Explain recursion" --provider anthropic

# Specify model
ai-multitool chat "What is REST API?" --model gpt-4-turbo-preview

# Stream response
ai-multitool chat "Tell me a short story" --stream

# Adjust temperature
ai-multitool chat "Be creative" --temperature 0.9

# Chat with RAG context (requires indexed documents)
ai-multitool chat "How does authentication work?" --rag
ai-multitool chat "Explain the API endpoints" --rag --rag-index ./my-index
```

### Code Analysis

```bash
# Analyze a file
ai-multitool analyze ./src/main.py

# Analyze a directory
ai-multitool analyze ./src

# Show code structure without AI
ai-multitool analyze ./src --structure

# Analyze with git context
ai-multitool analyze ./src --git

# Analyze with RAG documentation context
ai-multitool analyze ./src --rag-context

# Disable smart context builder
ai-multitool analyze ./src --no-context
```

### RAG - Document Indexing & Search

```bash
# Index a directory of documents
ai-multitool rag index ./docs --pattern "*.md"

# Index with custom chunking
ai-multitool rag index ./docs --chunk-size 1500 --chunk-overlap 300

# Save to custom location
ai-multitool rag index ./docs --output ./my-index

# Search indexed documents
ai-multitool rag search "how to install the tool"

# Search with custom index
ai-multitool rag search "authentication" --index ./my-index --top-k 10

# View index statistics
ai-multitool rag stats
ai-multitool rag stats --index ./my-index
```

### API Key Management

```bash
# Store API keys securely in system keyring
ai-multitool keys set anthropic
ai-multitool keys set openai

# Retrieve stored keys
ai-multitool keys get anthropic
ai-multitool keys get openai

# List all stored keys
ai-multitool keys list

# Delete a key
ai-multitool keys delete anthropic

# Migrate keys from .env to keyring
ai-multitool keys migrate
```

### Usage Statistics

```bash
# View usage statistics (last 30 days)
ai-multitool stats

# View statistics for custom time range
ai-multitool stats --days 7

# Show more recent calls
ai-multitool stats --recent 20

# Clear all metrics
ai-multitool clear-stats
```

### Configuration

```bash
# View all configuration
ai-multitool config

# View specific setting
ai-multitool config default_model

# List available models
ai-multitool list-models
```

## RAG Workflow

1. **Index your documentation:**
```bash
ai-multitool rag index ./docs --pattern "*.md"
```

2. **Search your docs:**
```bash
ai-multitool rag search "installation guide"
```

3. **Use RAG in chat:**
```bash
ai-multitool chat "How do I configure the tool?" --rag
```

4. **Use RAG in code analysis:**
```bash
ai-multitool analyze ./src --rag-context
```

## Project Structure

```
ai-multitool/
├── ai_multitool/
│   ├── __init__.py
│   ├── cli/              # CLI interface
│   │   └── main.py
│   ├── core/             # AI/LLM integration
│   │   ├── llm_client.py
│   │   ├── models.py
│   │   └── exceptions.py
│   ├── config/           # Configuration management
│   │   └── settings.py
│   ├── utils/            # Utility functions
│   │   ├── file_utils.py
│   │   ├── git_utils.py
│   │   ├── context_builder.py
│   │   ├── key_manager.py
│   │   ├── sanitizer.py
│   │   ├── metrics.py
│   │   └── rag_helper.py
│   ├── parsers/          # Code parsing
│   │   └── code_parser.py
│   └── rag/              # RAG features
│       ├── embeddings.py
│       ├── chunkers.py
│       ├── vector_store.py
│       ├── indexer.py
│       └── retriever.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black ai_multitool/

# Lint code
ruff check ai_multitool/

# Type check
mypy ai_multitool/
```

## License

MIT License - see LICENSE file for details.
