# Changelog

All notable changes to ai-multitool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **OpenCode Adapter**: Full support for OpenCode CLI integration with `OpenCodeAdapter` and `create_opencode_adapter()`
- **Gemini CLI Adapter**: Full support for Gemini CLI integration with `GeminiAdapter` and `create_gemini_adapter()`
- **Qwen CLI Adapter**: Full support for Qwen CLI integration with `QwenAdapter` and `create_qwen_adapter()`
- All new adapters support both Anthropic and OpenAI providers
- Updated README.md with integration examples for all 5 supported CLI tools

### Changed
- **Documentation Reorganization**: Moved all .md files (except README.md) to docs/ directory for better project organization
- Updated MANIFEST.in to include docs/ directory and docs/CHANGELOG.md
- Updated README.md to reference docs/ directory instead of CONTRIBUTING.md
- Updated release.py to use docs/CHANGELOG.md instead of root CHANGELOG.md
- Added readme-content-type to pyproject.toml for proper PyPI rendering
- Updated supported CLI tools section to show all 5 tools as fully supported (✅)

## [0.3.0] - 2025-05-05

### Added
- **26 New Advanced Tools**: Expanded from 34 to 60 tools across 30+ categories
- **Performance Tools**: PerformanceProfiler for AI-powered performance profiling
- **Database Tools**: SchemaAnalyzer for database schema optimization
- **API Tools**: APIDesigner for RESTful API design with OpenAPI
- **Cloud Tools**: DockerOptimizer for Docker optimization
- **Logging Tools**: LogAnalyzer for log analysis and debugging
- **ML Tools**: ModelOptimizer for ML model optimization
- **DevOps Tools**: PipelineAnalyzer for CI/CD pipeline analysis
- **Monitoring Tools**: AlertOptimizer for monitoring alert optimization
- **Mobile Tools**: MobileAppAnalyzer for mobile app performance/UX
- **Frontend Tools**: ComponentAnalyzer for frontend component analysis
- **Crypto Tools**: CryptoKeyManager for cryptographic key management
- **Network Tools**: NetworkProtocolAnalyzer for network protocol optimization
- **Data Tools**: DataPipelineOptimizer for data pipeline optimization
- **Web Tools**: WebScraper for web scraping with selector generation
- **SEO Tools**: SEOOptimizer for SEO optimization
- **Accessibility Tools**: AccessibilityAuditor for WCAG compliance auditing
- **Backup Tools**: BackupStrategy for backup strategy design
- **Analytics Tools**: AnalyticsReporter for analytics reporting and dashboards
- **Automation Tools**: WorkflowDesigner for workflow automation design
- **Compliance Tools**: ComplianceAuditor for GDPR/HIPAA/SOC2 compliance
- **Infrastructure Tools**: InfrastructureProvisioner for cloud infrastructure provisioning
- **Messaging Tools**: QueueAnalyzer for message queue analysis
- **Storage Tools**: StorageOptimizer for storage tier selection and lifecycle
- **Search Tools**: SearchAnalyzer for search schema design and query optimization
- **Email Tools**: EmailAnalyzer for email content optimization and deliverability
- **Legal Tools**: ContractAnalyzer for legal contract analysis and risk assessment
- **IoT Tools**: IoTDeviceManager for IoT device management and security
- **Token Budget Controls**: Comprehensive token consumption tracking and limits
  - Max tokens per session: 100,000 (configurable)
  - Max tokens per tool: 5,000 (configurable)
  - Warning threshold: 80% of budget
  - Budget exceeded action: warn/stop/continue (configurable)
  - Response caching: 40-60% token reduction for repeated operations
  - Prompt optimization: automatic compression and truncation
  - Thread-safe budget checking for concurrent operations
- **Prompt Optimizer**: New utility module for prompt compression and optimization
- **Memory Fixes**: Fixed memory issues causing PC freezing with large directories
- **File Limits**: Added file limits to directory indexing for better memory management
- **Path Validation**: Enhanced security with path validation for file operations
- **Cache Memory Limits**: Added memory limits for response caching
- **Token Count Fallback**: Added fallback estimation for token counting

### Changed
- Updated all existing advanced tools to use token budget controls
- Updated documentation with new tools and token budget guide
- Updated ai_multitool/advanced/__init__.py with new category imports
- Improved memory usage monitoring across the application

## [0.2.0] - 2025-05-05

### Added
- **Major Refactor**: Transformed from standalone CLI tool to Python library for CLI tool integration
- Plugin interface with `BasePlugin` for CLI tool integration
- Adapter system with `BaseAdapter` for easy CLI tool integration
- Pre-built adapters for Claude Code and Devin
- Tool registry and tool definition system
- Tool format converter (OpenAI, Anthropic, Generic formats)
- Public Python API exposed in `__init__.py`
- Plugin configuration with `PluginConfig`
- Custom exception classes for plugin errors
- Adapter utilities for tool format conversion
- Example adapters for Claude Code and Devin integration
- Comprehensive plugin integration documentation (PLUGIN_INTEGRATION.md)
- Library API design documentation (LIBRARY_API_DESIGN.md)
- Example scripts for different use cases (examples/ directory)
- Examples: basic usage, Claude Code integration, Devin integration, custom adapter, RAG usage, code analysis
- **Advanced Features**: 32 advanced tools across 9 categories for sophisticated AI-powered development workflows
  - Advanced Code Analysis (5 tools): CodeRefactoring, BugDetection, CodeSmellDetection, ComplexityAnalysis, SecurityScan
  - Advanced Git Operations (4 tools): CommitGenerator, PRAssistant, ConflictResolver, BlameAnalyzer
  - Advanced Security (3 tools): SecretScanner, VulnChecker, LicenseCheck
  - Advanced RAG (4 tools): MultiModalRAG, HybridSearchRAG, ReRankingRAG, CitationRAG
  - Advanced AI (4 tools): FunctionCalling, AgentOrchestrator, WorkflowEngine, ContextWindowManager
  - Advanced Testing (3 tools): TestGenerator, CoverageAnalyzer, MutationTester
  - Advanced Documentation (3 tools): AutoDocGenerator, APIDocGenerator, ReadmeGenerator
  - Advanced Project Analysis (3 tools): ArchitectureAnalyzer, DependencyAnalyzer, ProjectHealthChecker
  - Advanced Collaboration (3 tools): CodeReviewAssistant, IssueTriageAssistant, PlanningAssistant
  - Advanced File Operations (2 tools): BatchProcessor, SmartDiffAnalyzer
- Advanced tools integration into adapter system with opt-in configuration
- Advanced features example script (examples/advanced_features.py)
- Advanced features documentation in README with usage examples for all 32 tools
- Advanced implementation status tracking (ADVANCED_IMPLEMENTATION_STATUS.md)

### Changed
- **Breaking Change**: Project is now a library, not a standalone CLI tool
- Updated README to focus on plugin developers rather than end users
- Updated version to 0.2.0
- Updated pyproject.toml description and keywords to reflect library nature
- Updated project classifiers to include library categories
- CLI entry point maintained as optional/demo interface
- All core functionality now accessible via public API

### Deprecated
- Standalone CLI usage is deprecated in favor of library usage
- Direct CLI commands should use adapters instead

## [Unreleased]

### Added
- File reading utility with code file detection
- Analyze command with file and directory support
- Smart content truncation for large files
- Directory analysis (up to 10 code files)
- Code parsing module with tree-sitter integration
- Code structure extraction (functions, classes, imports)
- --structure flag for analyze command to show code structure without AI
- Support for multiple programming languages (Python, JavaScript, TypeScript, Java, C/C++, Go, Rust, Ruby, PHP, Swift, Kotlin, Scala)
- Complexity scoring for code files
- LICENSE file (MIT) for open source distribution
- MANIFEST.in for proper PyPI package distribution
- Git integration for repository context
- Git context includes branch, commit info, status, modified files, and recent commits
- --git flag to control git context inclusion in analyze command
- git_utils.py module for git operations (branch, commits, status, diff, file history)
- Smart context builder for enhanced code analysis
- context_builder.py module for intelligent context aggregation
- File statistics (lines, chars, size) in analysis context
- Related file detection for better context
- Dependency/import extraction from code
- --context flag to enable/disable smart context builder (default: True)
- Comprehensive analysis context including structure, git, stats, and related files
- Secure API key management using system keyring
- key_manager.py module for secure key storage and retrieval
- keys CLI command with subcommands: set, get, delete, list, migrate
- Settings now check keyring as fallback for API keys
- Improved security by supporting OS-level keyring storage
- Content sanitization for security and privacy
- sanitizer.py module for detecting and redacting sensitive data
- Detection of prompt injection attempts
- Automatic redaction of emails, phone numbers, API keys, credit cards, SSNs
- Detection of hardcoded secrets in code (passwords, API keys, tokens)
- File safety checking to skip potentially unsafe files (.env, .pem, .key, etc.)
- --sanitize flag to enable/disable content sanitization (default: True)
- Binary content detection to prevent sending non-text data to AI
- Metrics collection and monitoring for usage analytics
- metrics.py module for tracking API calls and performance
- stats CLI command to view usage statistics
- clear-stats CLI command to clear all metrics
- MetricsContext for automatic timing and recording of API calls
- Local metrics storage in ~/.ai-multitool/metrics.json
- Statistics by provider, model, and command type
- Cache hit tracking and latency monitoring
- Recent calls history with status indicators
- Integrated metrics collection into chat and analyze commands
- Comprehensive error handling system with custom exceptions
- exceptions.py module with 15+ specific exception classes
- Custom exceptions for API, auth, rate limit, quota, file operations, git, parsing, sanitization, keyring, metrics, validation, network, timeout, and context errors
- Each exception includes helpful suggestions for recovery
- Improved error handling in LLM client with specific exception mapping
- Validation for API keys, messages, and provider inputs
- Graceful handling of API errors with appropriate retry logic
- Error handler function for nice CLI error display
- Try-except blocks in chat and analyze commands
- User-friendly error messages with recovery suggestions
- Keyboard interrupt handling
- Detailed error information with status codes and response bodies

### Changed
- Updated README with current working features
- Added usage examples for analyze command
- Enhanced analyze command to include code structure context in AI prompts
- Enhanced analyze command to include git repository context in AI prompts
- Enhanced analyze command to use smart context builder for richer AI context
- Updated API key retrieval to use keyring fallback in settings
- Enhanced analyze command with automatic content sanitization
- Integrated automatic metrics collection into chat and analyze commands
- Improved error handling across LLM client and CLI commands

## [0.1.0] - 2025-05-05

### Added
- Core LLM client module with Anthropic and OpenAI integration
- Response models (Message, LLMResponse, ChatHistory, ModelInfo)
- Streaming support for AI responses
- Retry logic with exponential backoff
- Rate limiting (token bucket algorithm)
- Response caching with TTL
- Chat command with real AI integration
- Support for multiple AI providers (Anthropic, OpenAI)
- Model selection and temperature control
- Streaming response support
- list-models command to show available AI models
- config command to view/set configuration
- Rich terminal UI with progress indicators
- Configuration management with Pydantic Settings
- Initial project structure
- Basic CLI skeleton with Typer
- Requirements.txt with core dependencies
- pyproject.toml for package configuration
- README.md with project documentation
- .env.example for configuration template
- .gitignore for Python projects

### Changed
- Initial commit

### Fixed
- Fixed formatting issues in list-models command
