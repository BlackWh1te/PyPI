# Error Conditions and Troubleshooting

This document describes common error conditions in ai-multitool and how to resolve them.

---

## Core Exceptions

### APIError
**Description:** Base exception for API-related errors.

**Common Causes:**
- Network connectivity issues
- API endpoint unavailable
- Invalid API requests

**Resolution:**
- Check internet connection
- Verify API endpoint is available
- Check API key validity
- Review request parameters

---

### AuthenticationError
**Description:** Authentication failed (invalid API key or credentials).

**Common Causes:**
- Invalid or expired API key
- Incorrect API key format
- API key not set

**Resolution:**
```python
# Set API key using key manager
from ai_multitool import KeyManager
manager = KeyManager()
manager.set_key("anthropic", "your-api-key")

# Or set via environment variable
export ANTHROPIC_API_KEY="your-api-key"
```

---

### RateLimitError
**Description:** Rate limit exceeded (too many requests).

**Common Causes:**
- Exceeding API rate limits
- Too many concurrent requests

**Resolution:**
- Implement retry logic with exponential backoff
- Reduce request frequency
- Use caching to reduce API calls

**Example:**
```python
import time

try:
    response = await llm_client.chat(messages)
except RateLimitError as e:
    retry_after = getattr(e, 'retry_after', 2)
    time.sleep(retry_after)
    # Retry request
```

---

### QuotaExceededError
**Description:** API quota exceeded (monthly/daily limits).

**Common Causes:**
- Exceeded monthly token limit
- Exceeded daily request limit

**Resolution:**
- Check API quota in provider dashboard
- Upgrade plan if needed
- Implement caching to reduce API usage

---

### ModelNotFoundError
**Description:** Requested model not available or invalid.

**Common Causes:**
- Invalid model name
- Model not available in current region
- Model deprecated

**Resolution:**
```python
# Use valid model names
valid_models = ["claude-3-sonnet-20240229", "claude-3-opus-20240229"]
llm_client = AnthropicClient(api_key="...", model=valid_models[0])
```

---

### TimeoutError
**Description:** Request timed out.

**Common Causes:**
- Slow network
- Large response
- Server processing delay

**Resolution:**
```python
# Increase timeout
llm_client = AnthropicClient(api_key="...", timeout=300)  # 5 minutes
```

---

### NetworkError
**Description:** Network-related error.

**Common Causes:**
- No internet connection
- DNS resolution failure
- Firewall blocking requests

**Resolution:**
- Check internet connection
- Verify DNS settings
- Check firewall rules
- Use proxy if needed

---

### ConfigurationError
**Description:** Invalid configuration.

**Common Causes:**
- Missing required configuration
- Invalid configuration values
- Configuration file corruption

**Resolution:**
```python
# Validate configuration
from ai_multitool.plugins import PluginConfig

try:
    config = PluginConfig(
        api_key="your-key",
        model="claude-3-sonnet-20240229",
        temperature=0.7
    )
except ValueError as e:
    print(f"Invalid configuration: {e}")
```

---

### ValidationError
**Description:** Input validation failed.

**Common Causes:**
- Invalid input format
- Missing required fields
- Out-of-range values

**Resolution:**
```python
# Example: VectorStore validation
from ai_multitool import InMemoryVectorStore

try:
    store = InMemoryVectorStore(dimension=1536, max_chunks=10000)
    store.add(chunks, embeddings)
except ValidationError as e:
    print(f"Validation error: {e}")
    print(f"Field: {e.field}")
```

---

## Metrics Exceptions

### MetricsError
**Description:** Metrics collection or storage error.

**Common Causes:**
- Corrupted metrics file
- Permission denied writing to metrics file
- Invalid metrics data

**Resolution:**
```python
# Delete corrupted metrics file
import os
metrics_file = os.path.expanduser("~/.ai-multitool/metrics.json")
if os.path.exists(metrics_file):
    os.remove(metrics_file)

# Metrics will be recreated on next use
```

---

## RAG Exceptions

### RetrievalError
**Description:** Error during document retrieval.

**Common Causes:**
- No documents indexed
- Invalid query
- Embedding generation failed

**Resolution:**
```python
# Ensure documents are indexed
indexer.index_directory("path/to/docs", pattern="*.md")

# Check vector store has documents
if store.count() == 0:
    print("No documents indexed. Please index documents first.")
```

---

## Plugin Exceptions

### ToolExecutionError
**Description:** Tool execution failed.

**Common Causes:**
- Tool not found in registry
- Tool parameters invalid
- Tool implementation error

**Resolution:**
```python
# Check tool is registered
if tool_name not in tool_registry.tools:
    print(f"Tool '{tool_name}' not found")
    print(f"Available tools: {list(tool_registry.tools.keys())}")
```

---

### ToolNotFoundError
**Description:** Requested tool not found in registry.

**Common Causes:**
- Tool not registered
- Incorrect tool name
- Tool not enabled in configuration

**Resolution:**
```python
# Register tool
tool_registry.register(tool_definition)

# Check tool is enabled
if not config.enable_code_analysis:
    print("Code analysis tools are disabled in configuration")
```

---

### PluginConfigError
**Description:** Invalid plugin configuration.

**Common Causes:**
- Invalid configuration key
- Invalid configuration value
- Missing required configuration

**Resolution:**
```python
# Validate configuration before use
from ai_multitool.plugins import PluginConfig

try:
    config = PluginConfig(
        api_key="your-key",
        temperature=0.7  # Must be 0.0 to 2.0
        max_tokens=4096  # Must be positive
    )
except ValueError as e:
    print(f"Configuration error: {e}")
```

---

## Code Parsing Exceptions

### CodeParsingError
**Description:** Error parsing code file.

**Common Causes:**
- Invalid file path
- File not found
- Unsupported file type
- Parse error in code

**Resolution:**
```python
from ai_multitool import CodeParser

parser = CodeParser()
try:
    structure = parser.parse_file("path/to/file.py")
except CodeParsingError as e:
    print(f"Failed to parse file: {e}")
```

---

## Common Error Scenarios

### Scenario 1: Memory Error When Adding Chunks
**Error:** `MemoryError: Cannot add X chunks: would exceed max capacity`

**Cause:** Attempting to add more chunks than the max_chunks limit

**Resolution:**
```python
# Option 1: Increase max_chunks limit
store = InMemoryVectorStore(max_chunks=20000)

# Option 2: Process in batches
for batch in chunks_batch:
    store.add(batch, embeddings_batch)
```

---

### Scenario 2: Circular Reference Warning
**Error:** `RuntimeError: LLM client has been garbage collected`

**Cause:** Weak reference was garbage collected

**Resolution:**
```python
# Keep a strong reference to the LLM client
llm_client = AnthropicClient(api_key="...")
tool = AdvancedTool(llm_client=llm_client)

# Don't let llm_client go out of scope
```

---

### Scenario 3: Configuration Validation Error
**Error:** `ValueError: temperature must be between 0.0 and 2.0`

**Cause:** Temperature value outside valid range

**Resolution:**
```python
# Use valid temperature range (0.0 to 2.0)
config = PluginConfig(
    api_key="your-key",
    temperature=0.7  # Valid: 0.0 to 2.0
)
```

---

### Scenario 4: Cache Key Generation Error
**Error:** Hash-related error in cache

**Cause:** Invalid message format

**Resolution:**
```python
# Ensure messages are properly formatted
from ai_multitool.core.models import Message, MessageRole

messages = [
    Message(role=MessageRole.USER, content="Your message here")
]
```

---

## Debugging Tips

1. **Enable Debug Logging**
```python
from ai_multitool.utils.logging_config import setup_logging
setup_logging(log_level="DEBUG")
```

2. **Check Metrics**
```python
from ai_multitool import MetricsCollector

collector = MetricsCollector()
stats = collector.get_stats()
print(f"Total calls: {stats['total_calls']}")
print(f"Success rate: {stats['successful_calls'] / stats['total_calls'] * 100:.1f}%")
```

3. **Validate Configuration Early**
```python
from ai_multitool.plugins import PluginConfig

try:
    config = PluginConfig(
        api_key=os.getenv("API_KEY"),
        temperature=float(os.getenv("TEMPERATURE", "0.7"))
    )
except ValueError as e:
    sys.exit(1)  # Exit with error
```

4. **Test with Small Datasets**
```python
# Start with small dataset to test functionality
store = InMemoryVectorStore(max_chunks=100)  # Small limit for testing
```

---

## Getting Help

If you encounter an error not documented here:

1. Check the exception type and message
2. Review the code around the error
3. Enable debug logging
4. Check the GitHub issues for similar problems
5. Create a new issue with:
   - Error message and traceback
   - Code snippet that reproduces the error
   - Environment details (Python version, OS, etc.)
