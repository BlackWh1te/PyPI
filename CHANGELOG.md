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

### Changed
- Updated README with current working features
- Added usage examples for analyze command
- Enhanced analyze command to include code structure context in AI prompts

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
