"""Pytest configuration and shared fixtures."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, MagicMock
import pytest

# Mock API keys for testing
MOCK_ANTHROPIC_API_KEY = "mock-anthropic-key-12345"
MOCK_OPENAI_API_KEY = "mock-openai-key-67890"


@pytest.fixture
def mock_anthropic_api_key():
    """Provide a mock Anthropic API key."""
    return MOCK_ANTHROPIC_API_KEY


@pytest.fixture
def mock_openai_api_key():
    """Provide a mock OpenAI API key."""
    return MOCK_OPENAI_API_KEY


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_python_file(temp_dir):
    """Create a sample Python file for testing."""
    sample_code = '''
def hello_world():
    """Say hello to the world."""
    print("Hello, World!")
    return 42

class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        self.value = 0
    
    def add(self, x):
        """Add a value."""
        self.value += x
        return self.value
    
    def multiply(self, x):
        """Multiply by a value."""
        self.value *= x
        return self.value
'''
    file_path = temp_dir / "sample.py"
    file_path.write_text(sample_code)
    return file_path


@pytest.fixture
def sample_markdown_file(temp_dir):
    """Create a sample markdown file for testing."""
    sample_md = '''
# Sample Document

This is a sample markdown document for testing RAG functionality.

## Features

- Feature 1: Description
- Feature 2: Description

## Code Example

```python
def example():
    return "example"
```
'''
    file_path = temp_dir / "sample.md"
    file_path.write_text(sample_md)
    return file_path


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client for testing."""
    client = Mock()
    client.chat = AsyncMock()
    client.chat.return_value = Mock(content="Mock response")
    return client


@pytest.fixture
def mock_embedding_model():
    """Create a mock embedding model for testing."""
    model = Mock()
    model.embed_text = Mock(return_value=[0.1, 0.2, 0.3])
    return model


@pytest.fixture
def mock_vector_store():
    """Create a mock vector store for testing."""
    store = Mock()
    store.add_vector = Mock()
    store.search = Mock(return_value=[
        (Mock(doc_id="doc1", text="Sample text 1"), 0.9),
        (Mock(doc_id="doc2", text="Sample text 2"), 0.8),
    ])
    return store


@pytest.fixture
def sample_git_repo(temp_dir):
    """Create a sample git repository for testing."""
    import subprocess
    
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_dir, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, capture_output=True)
    
    # Create a sample file and commit
    sample_file = temp_dir / "README.md"
    sample_file.write_text("# Test Repository")
    subprocess.run(["git", "add", "."], cwd=temp_dir, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=temp_dir, capture_output=True)
    
    return temp_dir


@pytest.fixture
def mock_plugin_config():
    """Create a mock plugin configuration."""
    from ai_multitool import PluginConfig, Provider
    
    return PluginConfig(
        api_key=MOCK_ANTHROPIC_API_KEY,
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


@pytest.fixture
def sample_document():
    """Create a sample document for RAG testing."""
    from ai_multitool import Document
    
    return Document(
        text="This is a sample document for testing RAG functionality. It contains multiple sentences.",
        doc_id="doc1",
        metadata={"source": "test.txt", "category": "test"}
    )


@pytest.fixture
def sample_messages():
    """Create sample messages for LLM testing."""
    from ai_multitool import Message, MessageRole
    
    return [
        Message(role=MessageRole.USER, content="Hello, how are you?"),
        Message(role=MessageRole.ASSISTANT, content="I'm doing well, thank you!"),
    ]


# Environment setup for tests
@pytest.fixture(autouse=True)
def setup_environment(monkeypatch):
    """Set up environment variables for testing."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", MOCK_ANTHROPIC_API_KEY)
    monkeypatch.setenv("OPENAI_API_KEY", MOCK_OPENAI_API_KEY)
