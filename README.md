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
git clone https://github.com/BlackWh1te/PyPi.git
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

#### OpenCode Integration

```python
from ai_multitool import create_opencode_adapter

# Create adapter
adapter = create_opencode_adapter(
    api_key="your-api-key",
    provider="anthropic",
    model="claude-3-sonnet-20240229",
    enable_code_analysis=True,
)

# Get tools in OpenAI format
tools = adapter.get_tool_definitions()
```

#### Gemini CLI Integration

```python
from ai_multitool import create_gemini_adapter

# Create adapter
adapter = create_gemini_adapter(
    api_key="your-api-key",
    provider="anthropic",
    model="claude-3-sonnet-20240229",
    enable_code_analysis=True,
)

# Get tools in OpenAI format
tools = adapter.get_tool_definitions()
```

#### Qwen CLI Integration

```python
from ai_multitool import create_qwen_adapter

# Create adapter
adapter = create_qwen_adapter(
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

ai-multitool includes 32 advanced tools across 9 categories for sophisticated AI-powered development workflows.

### Advanced Code Analysis

```python
from ai_multitool import (
    AdvancedCodeRefactoring,
    AdvancedBugDetection,
    AdvancedCodeSmellDetection,
    AdvancedComplexityAnalysis,
    AdvancedSecurityScan,
)

# Code refactoring with AI suggestions
refactoring = AdvancedCodeRefactoring(client)
result = await refactoring.execute(
    file_path="main.py",
    aggressive=False,
    focus_areas=["readability", "performance"]
)

# Bug detection with severity analysis
bug_detection = AdvancedBugDetection(client)
result = await bug_detection.execute(
    file_path="main.py",
    severity="all",
    include_fixes=True
)

# Security vulnerability scanning
security_scan = AdvancedSecurityScan(client)
result = await security_scan.execute(
    file_path="main.py",
    check_types=["injection", "xss", "auth"]
)
```

### Advanced Git Operations

```python
from ai_multitool import (
    AdvancedCommitGenerator,
    AdvancedPRAssistant,
    AdvancedConflictResolver,
    AdvancedBlameAnalyzer,
)

# Generate conventional commit messages
commit_gen = AdvancedCommitGenerator(client)
result = await commit_gen.execute(
    repo_path=".",
    style="conventional"
)

# PR review and suggestions
pr_assistant = AdvancedPRAssistant(client)
result = await pr_assistant.execute(
    pr_number=123,
    focus_areas=["logic", "security", "style"]
)

# Resolve merge conflicts with AI
conflict_resolver = AdvancedConflictResolver(client)
result = await conflict_resolver.execute(
    repo_path=".",
    conflict_files=["src/main.py"]
)
```

### Advanced Security

```python
from ai_multitool import (
    AdvancedSecretScanner,
    AdvancedVulnChecker,
    AdvancedLicenseCheck,
)

# Scan for secrets and credentials
secret_scanner = AdvancedSecretScanner(client)
result = await secret_scanner.execute(
    repo_path=".",
    scan_patterns=["api_key", "password", "token"]
)

# Check for known vulnerabilities
vuln_checker = AdvancedVulnChecker(client)
result = await vuln_checker.execute(
    dependencies_file="requirements.txt",
    severity_threshold="high"
)

# License compliance checking
license_check = AdvancedLicenseCheck(client)
result = await license_check.execute(
    repo_path=".",
    allowed_licenses=["MIT", "Apache-2.0", "BSD-3-Clause"]
)
```

### Advanced RAG

```python
from ai_multitool import (
    MultiModalRAG,
    HybridSearchRAG,
    ReRankingRAG,
    CitationRAG,
)

# Multi-modal RAG with text and code
multimodal_rag = MultiModalRAG(client, embedding_model, vector_store)
result = await multimodal_rag.query(
    query="How does authentication work?",
    content_types=["text", "code"]
)

# Hybrid search with keyword + semantic
hybrid_rag = HybridSearchRAG(client, embedding_model, vector_store)
result = await hybrid_rag.query(
    query="database connection",
    alpha=0.7  # Balance between semantic and keyword
)

# RAG with citation sources
citation_rag = CitationRAG(client, embedding_model, vector_store)
result = await citation_rag.query(
    query="error handling patterns",
    include_citations=True
)
```

### Advanced AI Features

```python
from ai_multitool import (
    FunctionCalling,
    AgentOrchestrator,
    WorkflowEngine,
    ContextWindowManager,
)

# Function calling with tools
function_calling = FunctionCalling(client)
result = await function_calling.execute(
    tools=[tool1, tool2, tool3],
    user_query="Analyze the code and suggest improvements"
)

# Multi-agent orchestration
agent_orchestrator = AgentOrchestrator(client)
result = await agent_orchestrator.execute(
    agents=["coder", "reviewer", "tester"],
    task="Implement and test user authentication"
)

# Context window optimization
context_manager = ContextWindowManager(client)
result = await context_manager.optimize_context(
    messages=long_conversation,
    target_tokens=4000
)
```

### Advanced Testing

```python
from ai_multitool import (
    TestGenerator,
    CoverageAnalyzer,
    MutationTester,
)

# Generate tests from code
test_gen = TestGenerator(client)
result = await test_gen.execute(
    file_path="main.py",
    test_framework="pytest",
    coverage_target=80
)

# Analyze test coverage
coverage = CoverageAnalyzer(client)
result = await coverage.execute(
    test_path="tests/",
    source_path="src/"
)

# Mutation testing for robustness
mutation = MutationTester(client)
result = await mutation.execute(
    test_path="tests/",
    mutation_threshold=0.8
)
```

### Advanced Documentation

```python
from ai_multitool import (
    AutoDocGenerator,
    APIDocGenerator,
    ReadmeGenerator,
)

# Generate inline documentation
auto_doc = AutoDocGenerator(client)
result = await auto_doc.execute(
    file_path="main.py",
    style="google"
)

# Generate API documentation
api_doc = APIDocGenerator(client)
result = await api_doc.execute(
    module_path="src/",
    output_format="markdown"
)

# Generate README from code
readme_gen = ReadmeGenerator(client)
result = await readme_gen.execute(
    repo_path=".",
    sections=["installation", "usage", "api"]
)
```

### Advanced Project Analysis

```python
from ai_multitool import (
    ArchitectureAnalyzer,
    DependencyAnalyzer,
    ProjectHealthChecker,
)

# Analyze software architecture
arch_analyzer = ArchitectureAnalyzer(client)
result = await arch_analyzer.execute(
    repo_path=".",
    analysis_depth="deep"
)

# Analyze dependencies
dep_analyzer = DependencyAnalyzer(client)
result = await dep_analyzer.execute(
    repo_path=".",
    check_updates=True,
    check_vulnerabilities=True
)

# Check overall project health
health_check = ProjectHealthChecker(client)
result = await health_check.execute(
    repo_path=".",
    checks=["code_quality", "test_coverage", "documentation"]
)
```

### Advanced Collaboration

```python
from ai_multitool import (
    CodeReviewAssistant,
    IssueTriageAssistant,
    PlanningAssistant,
)

# AI-assisted code review
review_assistant = CodeReviewAssistant(client)
result = await review_assistant.execute(
    pr_number=123,
    focus_areas=["security", "performance", "maintainability"]
)

# Triage and categorize issues
issue_triage = IssueTriageAssistant(client)
result = await issue_triage.execute(
    issue_numbers=[1, 2, 3],
    auto_label=True
)

# Sprint planning assistance
planning = PlanningAssistant(client)
result = await planning.execute(
    backlog_items=[item1, item2, item3],
    team_capacity=40
)
```

### Advanced File Operations

```python
from ai_multitool import (
    BatchProcessor,
    SmartDiffAnalyzer,
)

# Batch process files
batch = BatchProcessor(client)
result = await batch.execute(
    file_pattern="**/*.py",
    operation="refactor",
    options={"aggressive": False}
)

# Intelligent diff analysis
diff_analyzer = SmartDiffAnalyzer(client)
result = await diff_analyzer.execute(
    file_path="main.py",
    compare_with="HEAD~1"
)
```

### Using Advanced Tools with Adapters

Advanced tools can be enabled in adapters via configuration:

```python
from ai_multitool import create_claude_code_adapter, PluginConfig

config = PluginConfig(
    api_key="your-key",
    provider=Provider.ANTHROPIC,
    advanced_tools={
        "code_refactoring": True,
        "bug_detection": True,
        "commit_generator": True,
        "security_scan": True,
    }
)

adapter = create_claude_code_adapter(config)
# Advanced tools are now available in get_tool_definitions()
```

See `examples/advanced_features.py` for complete usage examples.

## Supported CLI Tools

- ✅ Claude Code
- ✅ Devin
- ✅ OpenCode
- ✅ Gemini CLI
- ✅ Qwen CLI

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

Contributions are welcome! Please read the documentation in the `docs/` directory for details.

## Support

For issues and questions, please use the GitHub issue tracker.
