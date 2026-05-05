# Changelog

All notable changes to ai-multitool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

### Changed
- Initial project structure setup

### Fixed
- Fixed formatting issues in list-models command

## [0.1.0] - 2025-05-05

### Added
- Initial project structure
- Basic CLI skeleton with Typer
- Configuration module with Pydantic
- Requirements.txt with core dependencies
- pyproject.toml for package configuration
- README.md with project documentation
- .env.example for configuration template
- .gitignore for Python projects

### Changed
- Initial commit
