# Local-Only Quick Start Guide

Complete privacy-first setup using local AI models. No API keys, no cloud services, your code never leaves your machine.

## Prerequisites

- Python 3.10 or higher
- Ollama (local AI model runner)

## Installation

### 1. Install ai-multitool with local support

```bash
pip install ai-multitool[local]
```

This installs ai-multitool with Ollama support for local AI models.

### 2. Install Ollama

Download and install Ollama from [https://ollama.com](https://ollama.com)

Ollama runs local AI models on your machine. It's free, open-source, and works offline.

### 3. Pull a Model

```bash
ollama pull llama3.2
```

Recommended models:
- `llama3.2` - Fast, efficient, good for general use
- `llama3.2:3b` - Smaller, faster, good for limited RAM
- `codellama` - Specialized for code
- `mistral` - Good balance of speed and quality

### 4. Start Ollama Server

```bash
ollama serve
```

Keep this running in a separate terminal window.

## Verify Setup

```bash
ai-multitool doctor
```

This checks:
- Python version
- Ollama installation and server status
- Available models
- Configuration

You should see:
```
✓ Python Version: 3.x.x
✓ Platform: win32/linux/darwin
✓ ollama - Installed
✓ Ollama server running - X model(s) available
```

## Explore Available Tools

```bash
ai-multitool discover --local-only
```

This shows all 95 developer tools that work completely offline:
- API Testing (5 tools)
- Code Quality (5 tools)
- CI/CD (5 tools)
- DevOps Infrastructure (5 tools)
- Database & Monitoring (5 tools)
- Advanced Features (5 tools)
- Developer Experience (5 tools)
- And 28 more categories

All of these work without any API keys or cloud services.

## Test AI Chat

```bash
ai-multitool chat "Hello, how are you?"
```

This uses your local Ollama model. No API key needed, completely offline.

## Use Tools Directly

```python
from ai_multitool.advanced.api_testing import APITester
from ai_multitool.advanced.code_quality import CodeLinter

# Test an API
tester = APITester()
result = tester.test_api("https://api.example.com/users")

# Lint code
linter = CodeLinter()
issues = linter.lint_code("path/to/your/code.py")
```

All tools work locally without cloud services.

## Use with AI CLI Tools

The 95 tools integrate with your favorite AI CLI:

### Claude Code
```python
from ai_multitool.adapters import create_claude_code_adapter

adapter = create_claude_code_adapter()
tools = adapter.get_tools()  # No API key needed for discovery
```

### Devin
```python
from ai_multitool.adapters import create_devin_adapter

adapter = create_devin_adapter()
tools = adapter.get_tools()
```

### OpenCode, Gemini CLI, Qwen CLI
Similar adapters available for all 5 supported CLI tools.

## Common Workflows

### Security Audit
```python
from ai_multitool.advanced.code_quality import SASTScanner
from ai_multitool.advanced.devops_infra import ContainerSecurityScanner

scanner = SASTScanner()
vulnerabilities = scanner.scan_code("path/to/code")

container_scanner = ContainerSecurityScanner()
issues = container_scanner.scan_image("myapp:latest")
```

### Code Review
```python
from ai_multitool.advanced.code_quality import CodeLinter
from ai_multitool.advanced.dev_experience import CodeReviewBot

linter = CodeLinter()
lint_issues = linter.lint_code("path/to/code")

review_bot = CodeReviewBot()
review = review_bot.review_code("path/to/code")
```

### API Testing
```python
from ai_multitool.advanced.api_testing import APITester, APILoadTester

tester = APITester()
test_result = tester.test_api("https://api.example.com/users")

load_tester = APILoadTester()
load_result = load_tester.load_test("https://api.example.com/users", concurrent_users=100)
```

## Troubleshooting

### Ollama Server Not Running
```bash
# Start Ollama
ollama serve

# In another terminal, test
ai-multitool doctor
```

### No Models Available
```bash
# Pull a model
ollama pull llama3.2

# List available models
ollama list
```

### Python Version Too Old
```bash
# Check version
python --version

# Upgrade Python or use virtual environment with Python 3.10+
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install ai-multitool[local]
```

### Windows Color Issues
The library automatically forces color support on Windows. If you still have issues:

```bash
# Set environment variable
set FORCE_COLOR=1

# Or in PowerShell
$env:FORCE_COLOR="1"
```

## Next Steps

1. **Explore Tools**: Run `ai-multitool discover --local-only` to see all available tools
2. **Read Documentation**: Check `docs/` directory for detailed tool documentation
3. **Try Examples**: Look at example code in the repository
4. **Integrate with CLI**: Use adapters to integrate with your AI CLI tool

## Privacy Guarantees

- ✓ No API keys required for 95 tools
- ✓ No data sent to cloud services
- ✓ Works completely offline
- ✓ Your code never leaves your machine
- ✓ Open source, MIT licensed
- ✓ No telemetry, no tracking

## Support

For issues or questions:
- Run `ai-multitool doctor` to diagnose problems
- Check the main README.md
- Open an issue on GitHub

## Why Local-Only?

- **Privacy**: Your code and data stay on your machine
- **Security**: No external API calls, no attack surface
- **Cost**: No API bills, no token limits
- **Reliability**: Works offline, no network dependency
- **Compliance**: Meet strict data residency requirements
- **Speed**: No network latency, local inference
- **Control**: Use any model you want, no vendor lock-in

This is the future of AI development tools.
