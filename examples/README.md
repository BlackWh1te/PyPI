# ai-multitool Examples

This directory contains example scripts demonstrating how to use ai-multitool.

## Examples

### basic_usage.py
Basic usage of the LLM client for simple chat interactions.

```bash
python examples/basic_usage.py
```

### claude_code_integration.py
Example of integrating ai-multitool with Claude Code using the pre-built adapter.

```bash
python examples/claude_code_integration.py
```

### devin_integration.py
Example of integrating ai-multitool with Devin using the pre-built adapter.

```bash
python examples/devin_integration.py
```

### custom_adapter.py
Example of creating a custom adapter for your own CLI tool.

```bash
python examples/custom_adapter.py
```

### rag_usage.py
Example of using RAG (Retrieval-Augmented Generation) for document-aware AI responses.

```bash
python examples/rag_usage.py
```

### code_analysis.py
Example of using code parsing and smart context building.

```bash
python examples/code_analysis.py
```

## Running the Examples

1. Install ai-multitool:
```bash
pip install ai-multitool
```

2. Set your API keys:
```bash
export ANTHROPIC_API_KEY=your-key
export OPENAI_API_KEY=your-key
```

3. Run an example:
```bash
python examples/basic_usage.py
```

Note: You'll need to replace the placeholder API keys in the example files with your actual keys.

## Notes

- The examples use placeholder API keys - replace them with your actual keys
- Some examples require specific files (e.g., code_analysis.py needs example.py)
- All async examples use asyncio.run() for execution
- Error handling is minimal in examples - add proper error handling for production use
