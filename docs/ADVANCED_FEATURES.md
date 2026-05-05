# Advanced Features & Improvements for ai-multitool

## 1. Error Handling & Resilience

### Comprehensive Error Handling Strategy

```python
class ErrorHandler:
    """Centralized error handling with context recovery"""

    ERROR_CATEGORIES = {
        "auth": (AuthenticationError, "Authentication failed - check API keys"),
        "rate_limit": (RateLimitError, "Rate limit exceeded - waiting..."),
        "network": (NetworkError, "Network error - retrying..."),
        "timeout": (TimeoutError, "Request timed out"),
        "validation": (ValidationError, "Invalid input"),
        "content_filter": (ContentFilterError, "Content filtered by safety policies"),
    }

    @classmethod
    def handle_error(cls, error: Exception, context: Dict[str, Any]) -> ErrorRecovery:
        """Handle error with appropriate recovery strategy"""
        for category, (error_type, message) in cls.ERROR_CATEGORIES.items():
            if isinstance(error, error_type):
                return cls._get_recovery_strategy(category, error, context)

        # Unknown error
        return ErrorRecovery(
            action="abort",
            message=f"Unexpected error: {str(error)}",
            can_retry=False
        )

    @classmethod
    def _get_recovery_strategy(cls, category: str, error: Exception, context: Dict) -> ErrorRecovery:
        strategies = {
            "auth": ErrorRecovery(action="abort", message="Check API keys in .env", can_retry=False),
            "rate_limit": ErrorRecovery(action="wait", message="Waiting 60s...", can_retry=True, wait_time=60),
            "network": ErrorRecovery(action="retry", message="Retrying...", can_retry=True, max_retries=3),
            "timeout": ErrorRecovery(action="retry", message="Retrying with longer timeout...", can_retry=True),
            "validation": ErrorRecovery(action="abort", message=f"Invalid input: {str(error)}", can_retry=False),
            "content_filter": ErrorRecovery(action="warn", message="Content was filtered", can_retry=False),
        }
        return strategies.get(category, strategies["network"])
```

### Circuit Breaker Pattern

```python
class CircuitBreaker:
    """Circuit breaker for API calls to prevent cascading failures"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
        self._lock = asyncio.Lock()

    async def call(self, func: Callable, *args, **kwargs):
        async with self._lock:
            if self.state == "open":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "half-open"
                else:
                    raise CircuitBreakerOpenError("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            async with self._lock:
                self.failure_count = 0
                self.state = "closed"
            return result
        except Exception as e:
            async with self._lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.failure_count >= self.failure_threshold:
                    self.state = "open"
            raise
```

## 2. Security & Privacy

### API Key Management

```python
class SecureKeyManager:
    """Secure API key storage and retrieval"""

    def __init__(self, keyring_service: str = "ai-multitool"):
        self.keyring = keyring
        self.service = keyring_service

    def set_key(self, provider: str, api_key: str):
        """Store API key securely in system keyring"""
        keyring.set_password(self.service, provider, api_key)

    def get_key(self, provider: str) -> Optional[str]:
        """Retrieve API key from system keyring"""
        try:
            return keyring.get_password(self.service, provider)
        except keyring.errors.KeyringError:
            return None

    def delete_key(self, provider: str):
        """Delete API key from keyring"""
        keyring.delete_password(self.service, provider)

    @classmethod
    def mask_key(cls, key: str, visible_chars: int = 4) -> str:
        """Mask API key for display"""
        if len(key) <= visible_chars:
            return "*" * len(key)
        return key[:visible_chars] + "*" * (len(key) - visible_chars)
```

### Content Sanitization

```python
class ContentSanitizer:
    """Sanitize content to prevent prompt injection and data leakage"""

    PATTERNS_TO_REMOVE = [
        r"password\s*[:=]\s*\S+",  # Password patterns
        r"api[_-]?key\s*[:=]\s*\S+",  # API key patterns
        r"secret\s*[:=]\s*\S+",  # Secret patterns
        r"token\s*[:=]\s*\S+",  # Token patterns
        r"credit[_-]?card\s*[:=]\s*\S+",  # Credit card patterns
    ]

    PATTERNS_TO_BLOCK = [
        r"ignore\s+(previous|all)\s+instructions",
        r"system\s*:\s*",
        r"assistant\s*:\s*",
        r"<\|.*?\|>",  # Special tokens
    ]

    @classmethod
    def sanitize(cls, content: str) -> tuple[str, List[str]]:
        """Sanitize content and return cleaned version + detected issues"""
        issues = []

        # Check for blocked patterns
        for pattern in cls.PATTERNS_TO_BLOCK:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"Blocked pattern detected: {pattern}")

        # Remove sensitive patterns
        cleaned = content
        for pattern in cls.PATTERNS_TO_REMOVE:
            matches = re.findall(pattern, cleaned, re.IGNORECASE)
            if matches:
                issues.append(f"Sensitive pattern detected and removed: {pattern}")
                cleaned = re.sub(pattern, "***REDACTED***", cleaned, flags=re.IGNORECASE)

        return cleaned, issues

    @classmethod
    def validate_input(cls, content: str, max_length: int = 100000) -> tuple[bool, str]:
        """Validate input content"""
        if len(content) > max_length:
            return False, f"Content too long (max {max_length} chars)"

        if not content.strip():
            return False, "Content cannot be empty"

        cleaned, issues = cls.sanitize(content)
        if issues:
            return False, f"Content contains blocked patterns: {', '.join(issues)}"

        return True, ""
```

### Audit Logging

```python
class AuditLogger:
    """Audit logger for security and compliance"""

    def __init__(self, log_file: str = "audit.log"):
        self.log_file = log_file
        self._ensure_log_file()

    def log_event(self, event_type: str, details: Dict[str, Any]):
        """Log security-relevant events"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details,
            "user": os.getenv("USER", "unknown"),
            "hostname": socket.gethostname(),
        }

        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def log_api_call(self, provider: str, model: str, tokens: int, success: bool):
        """Log API call for cost tracking"""
        self.log_event("api_call", {
            "provider": provider,
            "model": model,
            "tokens": tokens,
            "success": success,
        })

    def log_key_access(self, provider: str):
        """Log when API keys are accessed"""
        self.log_event("key_access", {
            "provider": provider,
        })

    def log_content_filter(self, reason: str):
        """Log when content is filtered"""
        self.log_event("content_filter", {
            "reason": reason,
        })
```

## 3. Performance Optimization

### Connection Pooling

```python
class ConnectionPoolManager:
    """Manage connection pools for HTTP clients"""

    def __init__(self, max_connections: int = 100, max_keepalive: int = 20):
        self.max_connections = max_connections
        self.max_keepalive = max_keepalive
        self.pools: Dict[str, httpx.AsyncClient] = {}

    async def get_client(self, base_url: str) -> httpx.AsyncClient:
        """Get or create connection pool for base URL"""
        if base_url not in self.pools:
            limits = httpx.Limits(
                max_connections=self.max_connections,
                max_keepalive_connections=self.max_keepalive
            )
            self.pools[base_url] = httpx.AsyncClient(
                limits=limits,
                timeout=httpx.Timeout(120.0)
            )
        return self.pools[base_url]

    async def close_all(self):
        """Close all connection pools"""
        for client in self.pools.values():
            await client.aclose()
        self.pools.clear()
```

### Intelligent Caching Strategy

```python
class IntelligentCache:
    """Multi-tier caching with smart eviction"""

    def __init__(self):
        self.l1_cache: Dict[str, Any] = {}  # In-memory L1
        self.l2_cache: Optional[DiskCache] = None  # Disk L2 (optional)
        self.access_counts: Dict[str, int] = {}
        self.access_times: Dict[str, float] = {}

    async def get(self, key: str) -> Optional[Any]:
        """Get from cache with tier fallback"""
        # Check L1
        if key in self.l1_cache:
            self._record_access(key)
            return self.l1_cache[key]

        # Check L2
        if self.l2_cache:
            value = self.l2_cache.get(key)
            if value is not None:
                # Promote to L1
                self.l1_cache[key] = value
                self._record_access(key)
                return value

        return None

    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set in cache with tier selection"""
        self._record_access(key)

        # Always set in L1
        self.l1_cache[key] = value

        # Set in L2 if available
        if self.l2_cache:
            self.l2_cache.set(key, value, expire=ttl)

        # Evict if L1 is too large
        if len(self.l1_cache) > 1000:
            self._evict_lru()

    def _record_access(self, key: str):
        self.access_counts[key] = self.access_counts.get(key, 0) + 1
        self.access_times[key] = time.time()

    def _evict_lru(self):
        """Evict least recently used item"""
        lru_key = min(self.access_times.items(), key=lambda x: x[1])[0]
        del self.l1_cache[lru_key]
        del self.access_counts[lru_key]
        del self.access_times[lru_key]
```

### Batch Processing

```python
class BatchProcessor:
    """Process multiple requests in batches for efficiency"""

    def __init__(self, batch_size: int = 10, delay_ms: int = 100):
        self.batch_size = batch_size
        self.delay_ms = delay_ms

    async def process_batch(
        self,
        items: List[Any],
        process_func: Callable,
        *args,
        **kwargs
    ) -> List[Any]:
        """Process items in batches"""
        results = []

        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]

            # Process batch concurrently
            batch_tasks = [process_func(item, *args, **kwargs) for item in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            results.extend(batch_results)

            # Rate limiting between batches
            if i + self.batch_size < len(items):
                await asyncio.sleep(self.delay_ms / 1000)

        return results
```

## 4. Monitoring & Observability

### Metrics Collection

```python
class MetricsCollector:
    """Collect and track performance metrics"""

    def __init__(self):
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.counters: Dict[str, int] = defaultdict(int)
        self._lock = asyncio.Lock()

    async def record_latency(self, operation: str, latency_ms: float):
        async with self._lock:
            self.metrics[f"{operation}_latency"].append(latency_ms)

    async def increment_counter(self, metric: str, value: int = 1):
        async with self._lock:
            self.counters[metric] += value

    async def record_tokens(self, provider: str, model: str, tokens: int):
        async with self._lock:
            self.counters[f"{provider}_{model}_tokens"] += tokens

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        summary = {"counters": dict(self.counters)}

        for metric, values in self.metrics.items():
            if values:
                summary[metric] = {
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values),
                }

        return summary

    def reset(self):
        """Reset all metrics"""
        self.metrics.clear()
        self.counters.clear()
```

### Health Checks

```python
class HealthChecker:
    """Health check system for dependencies"""

    def __init__(self):
        self.checks: Dict[str, Callable] = {}

    def register_check(self, name: str, check_func: Callable):
        """Register a health check"""
        self.checks[name] = check_func

    async def run_all_checks(self) -> Dict[str, bool]:
        """Run all health checks"""
        results = {}
        for name, check_func in self.checks.items():
            try:
                result = await check_func()
                results[name] = bool(result)
            except Exception:
                results[name] = False
        return results

    async def check_api_connectivity(self, provider: str, api_key: str) -> bool:
        """Check if API is accessible"""
        # Implement provider-specific connectivity check
        return True

    async def check_disk_space(self, path: str, min_gb: float = 1.0) -> bool:
        """Check available disk space"""
        stat = shutil.disk_usage(path)
        return stat.free >= min_gb * 1024**3
```

## 5. Advanced AI Features

### Function Calling / Tool Use

```python
class ToolExecutor:
    """Execute function calls from AI responses"""

    def __init__(self):
        self.tools: Dict[str, Callable] = {}

    def register_tool(self, name: str, func: Callable, schema: Dict):
        """Register a tool for function calling"""
        self.tools[name] = {
            "func": func,
            "schema": schema
        }

    async def execute_tool(self, tool_call: FunctionCall) -> Any:
        """Execute a tool call"""
        if tool_call.name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_call.name}")

        tool = self.tools[tool_call.name]
        result = await tool["func"](**tool_call.arguments)
        return result

    def get_tool_schemas(self) -> List[Dict]:
        """Get all tool schemas for the AI"""
        return [tool["schema"] for tool in self.tools.values()]
```

### RAG (Retrieval-Augmented Generation)

```python
class RAGSystem:
    """Retrieval-augmented generation for context-aware responses"""

    def __init__(self, embedding_model: str = "text-embedding-ada-002"):
        self.embedding_model = embedding_model
        self.vector_store: Optional[VectorStore] = None

    async def initialize(self):
        """Initialize vector store"""
        self.vector_store = ChromaVectorStore()

    async def add_document(self, content: str, metadata: Dict[str, Any]):
        """Add document to vector store"""
        embedding = await self._embed(content)
        self.vector_store.add(embedding, content, metadata)

    async def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        """Retrieve relevant documents"""
        query_embedding = await self._embed(query)
        results = self.vector_store.search(query_embedding, top_k)
        return [r["content"] for r in results]

    async def _embed(self, text: str) -> List[float]:
        """Generate embedding for text"""
        # Use OpenAI embeddings or local model
        response = await openai.Embedding.acreate(
            model=self.embedding_model,
            input=text
        )
        return response["data"][0]["embedding"]

    async def generate_with_context(
        self,
        query: str,
        llm_client: BaseLLMClient,
        top_k: int = 5
    ) -> str:
        """Generate response with retrieved context"""
        context_docs = await self.retrieve(query, top_k)
        context = "\n\n".join(context_docs)

        prompt = f"""Context:
{context}

Question: {query}

Answer:"""

        response = await llm_client.chat([Message(role="user", content=prompt)])
        return response.content
```

### Multi-Agent Orchestration

```python
class AgentOrchestrator:
    """Orchestrate multiple AI agents for complex tasks"""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}

    def register_agent(self, name: str, agent: BaseAgent):
        """Register an agent"""
        self.agents[name] = agent

    async def execute_workflow(
        self,
        workflow: List[AgentStep],
        context: Dict[str, Any]
    ) -> WorkflowResult:
        """Execute a multi-agent workflow"""
        results = []
        current_context = context

        for step in workflow:
            agent = self.agents[step.agent_name]
            result = await agent.execute(step.task, current_context)

            results.append(result)
            current_context = {**current_context, **result.output}

            # Check for workflow termination
            if result.terminate:
                break

        return WorkflowResult(
            steps_completed=len(results),
            outputs=[r.output for r in results],
            final_context=current_context
        )

class BaseAgent(ABC):
    """Base class for AI agents"""

    @abstractmethod
    async def execute(self, task: str, context: Dict[str, Any]) -> AgentResult:
        pass

class CodeReviewAgent(BaseAgent):
    """Agent specialized in code review"""

    async def execute(self, task: str, context: Dict[str, Any]) -> AgentResult:
        code = context.get("code", "")
        review_prompt = f"Review this code:\n{code}\n\n{task}"

        response = await self.llm_client.chat([
            Message(role="system", content="You are an expert code reviewer."),
            Message(role="user", content=review_prompt)
        ])

        return AgentResult(
            output={"review": response.content},
            terminate=False
        )
```

## 6. Plugin System

```python
class PluginManager:
    """Plugin system for extensibility"""

    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, Plugin] = {}
        self.hooks: Dict[str, List[Callable]] = defaultdict(list)

    def load_plugins(self):
        """Load all plugins from plugin directory"""
        if not os.path.exists(self.plugin_dir):
            return

        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py"):
                module_name = filename[:-3]
                self._load_plugin(module_name)

    def _load_plugin(self, module_name: str):
        """Load a single plugin"""
        spec = importlib.util.spec_from_file_location(
            module_name,
            os.path.join(self.plugin_dir, f"{module_name}.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "register"):
            plugin = module.register()
            self.plugins[plugin.name] = plugin

    def register_hook(self, hook_name: str, callback: Callable):
        """Register a callback for a hook"""
        self.hooks[hook_name].append(callback)

    async def execute_hook(self, hook_name: str, *args, **kwargs):
        """Execute all callbacks for a hook"""
        for callback in self.hooks[hook_name]:
            await callback(*args, **kwargs)
```

## 7. Advanced CLI Features

### Interactive Mode with Autocomplete

```python
class InteractiveShell:
    """Interactive shell with autocomplete and history"""

    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client
        self.history = ChatHistory()
        self.completer = CommandCompleter()

    async def start(self):
        """Start interactive shell"""
        print("ai-multitool Interactive Shell")
        print("Type 'help' for commands, 'exit' to quit\n")

        while True:
            try:
                # Read input with prompt
                user_input = await self._read_input("> ")

                if user_input.lower() in ["exit", "quit"]:
                    break

                if user_input.lower() == "help":
                    self._show_help()
                    continue

                # Process command
                response = await self._process_input(user_input)

                # Display response
                self._display_response(response)

            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                print(f"Error: {e}")

    async def _process_input(self, user_input: str) -> str:
        """Process user input and get AI response"""
        self.history.add_message(Message(role="user", content=user_input))

        response = await self.llm_client.chat(
            self.history.get_context_messages()
        )

        self.history.add_message(Message(role="assistant", content=response.content))
        return response.content

    def _display_response(self, response: str):
        """Display response with formatting"""
        console.print(Panel(response, title="AI Response"))

class CommandCompleter:
    """Command autocomplete"""

    COMMANDS = ["chat", "analyze", "config", "help", "exit", "clear", "history"]

    def complete(self, text: str, state: int) -> Optional[str]:
        """Complete command"""
        options = [cmd for cmd in self.COMMANDS if cmd.startswith(text)]
        if state < len(options):
            return options[state]
        return None
```

### Progress Tracking for Long Operations

```python
class ProgressTracker:
    """Track progress of long-running operations"""

    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
        self.progress = rich.progress.Progress(
            "[progress.description]{task.description}",
            rich.progress.BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            rich.progress.TimeRemainingColumn(),
        )

    def update(self, n: int = 1):
        """Update progress"""
        self.current += n
        self.progress.update(self.task_id, completed=self.current)

    def __enter__(self):
        self.task_id = self.progress.add_task(
            self.description,
            total=self.total
        )
        self.progress.start()
        return self

    def __exit__(self, *args):
        self.progress.stop()

    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds"""
        return time.time() - self.start_time

    @property
    def eta(self) -> float:
        """Get estimated time remaining"""
        if self.current == 0:
            return 0
        rate = self.current / self.elapsed
        remaining = self.total - self.current
        return remaining / rate if rate > 0 else 0
```

## 8. Configuration Management

### Hierarchical Configuration

```python
class ConfigManager:
    """Hierarchical configuration with multiple sources"""

    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.sources: List[ConfigSource] = []

    def add_source(self, source: ConfigSource):
        """Add a configuration source"""
        self.sources.append(source)

    async def load(self):
        """Load configuration from all sources"""
        for source in self.sources:
            source_config = await source.load()
            self._merge_config(source_config)

    def _merge_config(self, new_config: Dict[str, Any]):
        """Merge new config (later sources override earlier)"""
        self.config = deep_merge(self.config, new_config)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)

class EnvConfigSource(ConfigSource):
    """Configuration from environment variables"""

    async def load(self) -> Dict[str, Any]:
        config = {}
        for key, value in os.environ.items():
            if key.startswith("AI_MULTITOOL_"):
                config_key = key[len("AI_MULTITOOL_"):].lower()
                config[config_key] = value
        return config

class FileConfigSource(ConfigSource):
    """Configuration from file (TOML, YAML, JSON)"""

    def __init__(self, path: str):
        self.path = path

    async def load(self) -> Dict[str, Any]:
        if not os.path.exists(self.path):
            return {}

        ext = os.path.splitext(self.path)[1]
        if ext == ".toml":
            import toml
            return toml.load(self.path)
        elif ext in [".yaml", ".yml"]:
            import yaml
            with open(self.path) as f:
                return yaml.safe_load(f)
        elif ext == ".json":
            with open(self.path) as f:
                return json.load(f)
        return {}
```

## 9. Testing Infrastructure

### Comprehensive Test Suite

```python
class TestSuite:
    """Comprehensive test suite for ai-multitool"""

    @pytest.mark.asyncio
    async def test_llm_client_retry_logic():
        """Test retry logic on failures"""
        client = AnthropicClient("test_key", "claude-3-sonnet")
        # Mock failures and verify retries

    @pytest.mark.asyncio
    async def test_rate_limiter():
        """Test rate limiting"""
        limiter = RateLimiter(rate=10, per=60)
        # Test that rate limit is enforced

    @pytest.mark.asyncio
    async def test_cache_hit():
        """Test cache hits"""
        cache = ResponseCache()
        # Test cache set and get

    @pytest.mark.asyncio
    async def test_content_sanitization():
        """Test content sanitization"""
        # Test that sensitive patterns are removed
        # Test that blocked patterns are detected

    @pytest.mark.asyncio
    async def test_circuit_breaker():
        """Test circuit breaker"""
        breaker = CircuitBreaker(failure_threshold=3)
        # Test that circuit opens after failures
        # Test that circuit closes after recovery timeout

    def test_cli_commands():
        """Test CLI commands"""
        # Test all CLI commands with various inputs
        # Test error handling
```

## 10. Deployment & Distribution

### PyPI Package Configuration

```toml
[project]
name = "ai-multitool"
version = "0.1.0"
description = "AI-powered CLI multitool for developers"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
keywords = ["ai", "cli", "llm", "anthropic", "openai", "developer-tools"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Utilities",
]

[project.urls]
Homepage = "https://github.com/yourusername/ai-multitool"
Documentation = "https://ai-multitool.readthedocs.io"
Repository = "https://github.com/yourusername/ai-multitool"
"Bug Tracker" = "https://github.com/yourusername/ai-multitool/issues"

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]
all = [
    "ai-multitool[dev]",
    "chromadb>=0.4.0",  # For RAG
    "keyring>=24.0.0",  # For secure key storage
]
```

### Docker Support

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY ai_multitool/ ./ai_multitool/
COPY pyproject.toml .

# Install in development mode
RUN pip install -e .

# Set up entrypoint
ENTRYPOINT ["ai-multitool"]
CMD ["--help"]
```

### CI/CD Pipeline

```yaml
name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"

    - name: Run tests
      run: |
        pytest --cov=ai_multitool --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3

  lint:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"

    - name: Install dependencies
      run: |
        pip install -e ".[dev]"

    - name: Run Black
      run: black --check ai_multitool/

    - name: Run Ruff
      run: ruff check ai_multitool/

    - name: Run MyPy
      run: mypy ai_multitool/

  build:
    needs: [test, lint]
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"

    - name: Build package
      run: |
        pip install build
        python -m build

    - name: Publish to PyPI
      if: github.event_name == 'push' && github.ref == 'refs/heads/main'
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

This comprehensive set of advanced features will make ai-multitool a production-ready, enterprise-grade AI CLI tool with:
- Robust error handling and resilience
- Strong security and privacy protections
- Excellent performance through caching and optimization
- Full observability with metrics and health checks
- Advanced AI capabilities (RAG, function calling, multi-agent)
- Extensible plugin system
- Rich interactive CLI experience
- Comprehensive testing
- Easy deployment and distribution
