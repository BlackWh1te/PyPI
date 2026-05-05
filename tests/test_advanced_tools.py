"""Tests for advanced tools functionality."""

import pytest
from unittest.mock import Mock, AsyncMock
from ai_multitool import (
    AdvancedTool,
    ToolResult,
    ToolPipeline,
    AdvancedToolConfig,
    AdvancedSettings,
    BaseLLMClient,
)


class MockAdvancedTool(AdvancedTool):
    """Mock implementation of AdvancedTool for testing."""
    
    def __init__(self, llm_client: BaseLLMClient, name: str = "mock_tool"):
        super().__init__(llm_client)
        self.name = name
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the mock tool."""
        return ToolResult(success=True, data={"tool": self.name})
    
    def get_tool_definition(self) -> dict:
        """Get tool definition."""
        return {
            "name": self.name,
            "description": "Mock tool for testing",
            "parameters": {}
        }


class TestAdvancedTool:
    """Test advanced tool base class."""
    
    def test_advanced_tool_initialization(self, mock_llm_client):
        """Test advanced tool initialization."""
        tool = MockAdvancedTool(mock_llm_client, "test_tool")
        assert tool.llm_client == mock_llm_client
        assert tool.name == "test_tool"
    
    @pytest.mark.asyncio
    async def test_advanced_tool_execute(self, mock_llm_client):
        """Test advanced tool execution."""
        tool = MockAdvancedTool(mock_llm_client, "test_tool")
        
        result = await tool.execute(param1="value")
        
        assert result.success == True
        assert result.data["tool"] == "test_tool"


class TestToolResult:
    """Test tool result model."""
    
    def test_tool_result_creation(self):
        """Test creating a tool result."""
        result = ToolResult(
            success=True,
            data={"key": "value"},
            metrics={"execution_time": 1.5}
        )
        
        assert result.success == True
        assert result.data["key"] == "value"
        assert result.metrics["execution_time"] == 1.5
    
    def test_tool_result_with_error(self):
        """Test tool result with error."""
        result = ToolResult(
            success=False,
            errors=["Test error"],
            data={}
        )
        
        assert result.success == False
        assert "Test error" in result.errors


class TestToolPipeline:
    """Test tool pipeline."""
    
    def test_pipeline_initialization(self, mock_llm_client):
        """Test pipeline initialization."""
        tool1 = MockAdvancedTool(mock_llm_client, "tool1")
        tool2 = MockAdvancedTool(mock_llm_client, "tool2")
        
        pipeline = ToolPipeline([tool1, tool2])
        
        assert len(pipeline.tools) == 2
    
    @pytest.mark.asyncio
    async def test_pipeline_execute_sequential(self, mock_llm_client):
        """Test executing pipeline sequentially."""
        tool1 = MockAdvancedTool(mock_llm_client, "tool1")
        tool2 = MockAdvancedTool(mock_llm_client, "tool2")
        
        pipeline = ToolPipeline([tool1, tool2])
        results = await pipeline.execute_sequential(param="value")
        
        assert len(results) == 2
        assert all(r.success for r in results)


class TestAdvancedToolConfig:
    """Test advanced tool configuration."""
    
    def test_advanced_tool_config(self):
        """Test advanced tool configuration."""
        config = AdvancedToolConfig(
            cache_enabled=True,
            parallel_execution=True,
            max_workers=4,
            timeout_seconds=120,
            retry_attempts=3,
            retry_delay_ms=1000
        )
        
        assert config.cache_enabled == True
        assert config.timeout_seconds == 120
        assert config.retry_attempts == 3


class TestAdvancedSettings:
    """Test advanced settings."""
    
    def test_advanced_settings(self):
        """Test advanced settings singleton."""
        # Test singleton pattern
        settings1 = AdvancedSettings()
        settings2 = AdvancedSettings()
        assert settings1 is settings2
        
        # Test setting config
        config = AdvancedToolConfig(cache_enabled=False, timeout_seconds=60)
        AdvancedSettings.set(config)
        
        retrieved = AdvancedSettings.get()
        assert retrieved.cache_enabled == False
        assert retrieved.timeout_seconds == 60
        
        # Test setting via kwargs
        AdvancedSettings.set(cache_enabled=True, max_workers=8)
        retrieved = AdvancedSettings.get()
        assert retrieved.cache_enabled == True
        assert retrieved.max_workers == 8

