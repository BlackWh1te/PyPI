# Changelog

All notable changes to ai-multitool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
