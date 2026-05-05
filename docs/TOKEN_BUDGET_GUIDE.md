# Token Budget Control Guide

This guide explains how to control and monitor token usage when using ai-multitool's advanced AI tools.

## Overview

Each advanced tool execution makes an LLM API call that consumes tokens. Without controls, you could accidentally burn through your token budget quickly. This guide shows you how to:

1. Set token budget limits
2. Monitor token usage
3. Configure budget behavior
4. Estimate costs

## Default Configuration

```python
from ai_multitool.advanced.base import AdvancedSettings

# Default settings
AdvancedSettings.set(
    max_tokens_per_session=100000,      # 100K tokens per session
    max_tokens_per_tool=5000,          # 5K tokens per tool execution
    warn_at_percent=0.8,               # Warn at 80% of budget
    enable_token_tracking=True,        # Track token usage
    budget_exceeded_action="warn",      # "warn", "stop", or "continue"
    max_code_lines=1000,               # Max lines of code to analyze
    max_file_size_kb=500               # Max file size in KB
)
```

## Usage Examples

### 1. Set Conservative Budget (Safe for Development)

```python
from ai_multitool.advanced.base import AdvancedSettings

# Set conservative limits for development
AdvancedSettings.set(
    max_tokens_per_session=10000,      # 10K tokens (~$0.03)
    max_tokens_per_tool=2000,          # 2K tokens per tool
    warn_at_percent=0.7,               # Warn at 70%
    budget_exceeded_action="stop"      # Stop when exceeded
)

# Reset at start of session
AdvancedSettings.reset_token_budget()
```

### 2. Use Budget-Checked Execution

```python
from ai_multitool.advanced.performance.profiler import PerformanceProfiler
from ai_multitool.advanced.base import AdvancedSettings

# Configure budget
AdvancedSettings.set(max_tokens_per_session=50000)

# Use execute_with_budget_check instead of execute
profiler = PerformanceProfiler(llm_client=client)
result = await profiler.execute_with_budget_check(
    estimated_tokens=1500,  # Estimate tokens needed
    file_path="app.py",
    focus="cpu"
)

# Check current usage
print(f"Tokens used: {AdvancedSettings.get_tokens_used()}")
```

### 3. Monitor Usage During Session

```python
from ai_multitool.advanced.base import AdvancedSettings

# Reset at start
AdvancedSettings.reset_token_budget()

# Run tools...
result1 = await tool1.execute_with_budget_check(estimated_tokens=2000)
result2 = await tool2.execute_with_budget_check(estimated_tokens=1500)

# Check usage
used = AdvancedSettings.get_tokens_used()
max_budget = AdvancedSettings.get().max_tokens_per_session
percent = (used / max_budget) * 100

print(f"Token usage: {used}/{max_budget} ({percent:.1f}%)")
```

### 4. Different Budgets for Different Environments

```python
from ai_multitool.advanced.base import AdvancedSettings

# Development: Strict limits
if environment == "development":
    AdvancedSettings.set(
        max_tokens_per_session=10000,
        budget_exceeded_action="stop"
    )

# Production: Higher limits with warnings
elif environment == "production":
    AdvancedSettings.set(
        max_tokens_per_session=100000,
        budget_exceeded_action="warn"
    )

# Testing: No limits
elif environment == "testing":
    AdvancedSettings.set(
        enable_token_tracking=False  # Disable tracking
    )
```

## Token Budget Actions

### "warn" (Default)
- Continues execution even if budget exceeded
- Prints warning message
- Adds warning to ToolResult
- **Use when**: You want awareness but don't want to block operations

### "stop"
- Stops execution if budget would be exceeded
- Returns failed ToolResult with error message
- **Use when**: Strict budget control required (development, testing)

### "continue"
- No warnings, no stopping
- Silent execution
- **Use when**: You have unlimited budget or external monitoring

## Cost Estimation

### Claude Sonnet (Approximate Pricing)
- Input: $3 per 1M tokens
- Output: $15 per 1M tokens
- Average tool execution: ~2000 tokens
- Cost per execution: ~$0.006

### Budget Examples

| Budget | Est. Cost | Tool Runs | Use Case |
|--------|-----------|-----------|----------|
| 10K tokens | $0.03 | 5-7 | Development/testing |
| 50K tokens | $0.15 | 25-35 | Small project |
| 100K tokens | $0.30 | 50-70 | Medium project |
| 500K tokens | $1.50 | 250-350 | Large project |
| 1M tokens | $3.00 | 500-700 | Production batch |

## Content Size Limits

To prevent accidental large token consumption:

```python
AdvancedSettings.set(
    max_code_lines=1000,      # Analyze only first 1000 lines
    max_file_size_kb=500      # Reject files > 500KB
)
```

If content exceeds limits, tools will:
- Truncate to limit
- Add warning to result
- Continue with truncated content

## Best Practices

### 1. Always Reset Budget at Session Start
```python
AdvancedSettings.reset_token_budget()
```

### 2. Estimate Tokens Before Execution
```python
# Rough estimation: 1 line of code ≈ 4 tokens
lines = len(code.split('\n'))
estimated = lines * 4 + 500  # +500 for prompt/response overhead

result = await tool.execute_with_budget_check(estimated_tokens=estimated)
```

### 3. Check Usage Periodically
```python
if AdvancedSettings.get_tokens_used() > AdvancedSettings.get().max_tokens_per_session * 0.9:
    print("WARNING: 90% of token budget used!")
```

### 4. Use Caching When Possible
```python
AdvancedSettings.set(cache_enabled=True)  # Enable by default
```

### 5. Start Conservative, Increase as Needed
```python
# Start with strict limits
AdvancedSettings.set(max_tokens_per_session=10000)

# If you need more, increase gradually
AdvancedSettings.set(max_tokens_per_session=25000)
```

## Troubleshooting

### Problem: Tool fails with "Token budget exceeded"
**Solution**: Increase budget or reset:
```python
AdvancedSettings.set(max_tokens_per_session=20000)
AdvancedSettings.reset_token_budget()
```

### Problem: Not seeing token usage
**Solution**: Enable tracking:
```python
AdvancedSettings.set(enable_token_tracking=True)
```

### Problem: Want to run without limits
**Solution**: Disable tracking:
```python
AdvancedSettings.set(enable_token_tracking=False)
```

### Problem: Too many warnings
**Solution**: Adjust warning threshold:
```python
AdvancedSettings.set(warn_at_percent=0.9)  # Warn at 90% instead of 80%
```

## Integration with CLI

When using the CLI, you can set budget via environment variables or config file:

```bash
# Environment variables
export AI_MULTITOOL_MAX_TOKENS=50000
export AI_MULTITOOL_BUDGET_ACTION=stop
```

Or in config file:
```yaml
advanced:
  max_tokens_per_session: 50000
  budget_exceeded_action: stop
  warn_at_percent: 0.8
```

## Summary

- **Default**: 100K tokens per session (~$0.30)
- **Safe for development**: 10K tokens per session (~$0.03)
- **Use `execute_with_budget_check()`** for automatic budget enforcement
- **Monitor usage** with `AdvancedSettings.get_tokens_used()`
- **Reset budget** at start of each session
- **Start conservative**, increase as needed

This ensures you won't accidentally burn through your token budget while still having the flexibility to use AI tools effectively.
