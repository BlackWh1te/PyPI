# ai-multitool

AI-powered CLI multitool for developers. A unified interface for interacting with multiple AI models (Claude, GPT, Qwen, etc.) directly from your terminal.

## Features

### ✅ Currently Working (v0.1.0)
- 🤖 **Multi-Model Support**: Interact with Claude and GPT via a single CLI
- 💬 **Chat Interface**: Natural language conversations with AI models
- 🔄 **Streaming Support**: Real-time streaming responses
- ⚡ **Caching**: Response caching for faster repeated queries
- 🛡️ **Retry Logic**: Automatic retry with exponential backoff
- 🚦 **Rate Limiting**: Token bucket rate limiting
- 🎨 **Beautiful Output**: Rich terminal UI with progress indicators
- ⚙️ **Configurable**: Environment-based configuration with Pydantic
- 📋 **Model Discovery**: List available AI models
- 🔧 **Configuration Management**: View and manage settings

### 🚧 Coming Soon
- 📁 **Code Analysis**: Analyze files and directories with AI
- 🔧 **Developer Tools**: File watching, Git integration, code parsing
- 🧠 **Vector Search**: RAG capabilities with vector databases
- 🤖 **Multi-Agent**: Advanced agentic workflows
- 🎯 **Fine-Tuning**: Custom model training and deployment

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

# Chat with AI (requires API key)
ai-multitool chat "Hello, how are you?"
ai-multitool chat "Explain Python decorators" --provider anthropic
ai-multitool chat "What is the capital of France?" --provider openai --stream
```

## Configuration

Create a `.env` file in your project root:

```env
# API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key

# Model Settings
DEFAULT_MODEL=claude-3-sonnet-20240229
MAX_TOKENS=4096
TEMPERATURE=0.7

# CLI Settings
OUTPUT_FORMAT=rich
LOG_LEVEL=INFO
WATCH_DEBOUNCE=0.5
```

## Usage Examples

### Chat with AI

```bash
# Basic chat (uses default provider and model)
ai-multitool chat "Write a Python function to sort a list"

# Specify provider
ai-multitool chat "Explain recursion" --provider anthropic

# Specify model
ai-multitool chat "What is REST API?" --model gpt-4-turbo-preview

# Stream response
ai-multitool chat "Tell me a short story" --stream

# Adjust temperature
ai-multitool chat "Be creative" --temperature 0.9
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

## Project Structure

```
ai-multitool/
├── ai_multitool/
│   ├── __init__.py
│   ├── cli/              # CLI interface
│   ├── core/             # AI/LLM integration
│   ├── config/           # Configuration management
│   ├── utils/            # Utility functions
│   └── agents/           # AI agents and tools
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
