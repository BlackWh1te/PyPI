"""Tests for plugin interface functionality."""

import pytest
from unittest.mock import Mock, AsyncMock
from ai_multitool import (
    BasePlugin,
    PluginConfig,
    ToolDefinition,
    ToolRegistry,
    ToolCategory,
    PluginError,
    ToolExecutionError,
    Provider,
)
from ai_multitool.core.exceptions import ValidationError


class TestPluginConfig:
    """Test plugin configuration."""
    
    def test_config_creation(self, mock_anthropic_api_key):
        """Test creating plugin configuration."""
        config = PluginConfig(
            api_key=mock_anthropic_api_key,
            provider=Provider.ANTHROPIC,
            model="claude-3-sonnet-20240229"
        )
        
        assert config.api_key == mock_anthropic_api_key
        assert config.provider == Provider.ANTHROPIC
        assert config.model == "claude-3-sonnet-20240229"
    
    def test_config_validation_error(self):
        """Test configuration validation."""
        with pytest.raises(ValidationError):
            PluginConfig(
                api_key="",  # Empty API key
                provider=Provider.ANTHROPIC,
                model="claude-3-sonnet-20240229"
            )
    
    def test_config_with_optional_fields(self, mock_anthropic_api_key):
        """Test configuration with optional fields."""
        config = PluginConfig(
            api_key=mock_anthropic_api_key,
            provider=Provider.ANTHROPIC,
            model="claude-3-sonnet-20240229",
            max_tokens=4096,
            temperature=0.7,
            enable_cache=True,
            timeout=120
        )
        
        assert config.max_tokens == 4096
        assert config.temperature == 0.7
        assert config.enable_cache == True
        assert config.timeout == 120


class TestToolDefinition:
    """Test tool definition."""
    
    def test_tool_definition_creation(self):
        """Test creating a tool definition."""
        tool = ToolDefinition(
            name="test_tool",
            description="A test tool",
            parameters={
                "type": "object",
                "properties": {
                    "param1": {"type": "string"}
                },
                "required": ["param1"]
            },
            handler=lambda x: {"result": x},
            category=ToolCategory.GENERAL
        )
        
        assert tool.name == "test_tool"
        assert tool.category == ToolCategory.GENERAL
    
    def test_tool_definition_execution(self):
        """Test executing a tool."""
        def test_handler(param1):
            return {"result": param1}
        
        tool = ToolDefinition(
            name="test_tool",
            description="A test tool",
            parameters={
                "type": "object",
                "properties": {
                    "param1": {"type": "string"}
                },
                "required": ["param1"]
            },
            handler=test_handler,
            category=ToolCategory.GENERAL
        )
        
        result = tool.execute(param1="test_value")
        assert result["result"] == "test_value"
    
    def test_tool_definition_error_handling(self):
        """Test tool error handling."""
        def failing_handler():
            raise ValueError("Test error")
        
        tool = ToolDefinition(
            name="failing_tool",
            description="A failing tool",
            parameters={},
            handler=failing_handler,
            category=ToolCategory.GENERAL
        )
        
        with pytest.raises(ToolExecutionError):
            tool.execute()


class TestToolRegistry:
    """Test tool registry."""
    
    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = ToolRegistry()
        assert len(registry.tools) == 0
    
    def test_register_tool(self):
        """Test registering a tool."""
        registry = ToolRegistry()
        
        tool = ToolDefinition(
            name="test_tool",
            description="Test",
            parameters={},
            handler=lambda: {},
            category=ToolCategory.GENERAL
        )
        
        registry.register(tool)
        
        assert len(registry.tools) == 1
        assert "test_tool" in registry.tools
    
    def test_register_duplicate_tool(self):
        """Test registering duplicate tool raises error."""
        registry = ToolRegistry()
        
        tool = ToolDefinition(
            name="test_tool",
            description="Test",
            parameters={},
            handler=lambda: {},
            category=ToolCategory.GENERAL
        )
        
        registry.register(tool)
        
        with pytest.raises(PluginError):
            registry.register(tool)
    
    def test_get_tool(self):
        """Test getting a tool from registry."""
        registry = ToolRegistry()
        
        tool = ToolDefinition(
            name="test_tool",
            description="Test",
            parameters={},
            handler=lambda: {},
            category=ToolCategory.GENERAL
        )
        
        registry.register(tool)
        retrieved = registry.get("test_tool")
        
        assert retrieved.name == "test_tool"
    
    def test_list_tools(self):
        """Test listing all tools."""
        registry = ToolRegistry()
        
        for i in range(3):
            tool = ToolDefinition(
                name=f"tool_{i}",
                description=f"Tool {i}",
                parameters={},
                handler=lambda: {},
                category=ToolCategory.GENERAL
            )
            registry.register(tool)
        
        tools = registry.list_tools()
        assert len(tools) == 3
    
    def test_list_tools_by_category(self):
        """Test listing tools by category."""
        registry = ToolRegistry()
        
        tool1 = ToolDefinition(
            name="code_tool",
            description="Code tool",
            parameters={},
            handler=lambda: {},
            category=ToolCategory.CODE_ANALYSIS
        )
        
        tool2 = ToolDefinition(
            name="general_tool",
            description="General tool",
            parameters={},
            handler=lambda: {},
            category=ToolCategory.GENERAL
        )
        
        registry.register(tool1)
        registry.register(tool2)
        
        code_tools = registry.list_tools(category=ToolCategory.CODE_ANALYSIS)
        assert len(code_tools) == 1
        assert code_tools[0].name == "code_tool"
    
    def test_unregister_tool(self):
        """Test unregistering a tool."""
        registry = ToolRegistry()
        
        tool = ToolDefinition(
            name="test_tool",
            description="Test",
            parameters={},
            handler=lambda: {},
            category=ToolCategory.GENERAL
        )
        
        registry.register(tool)
        assert len(registry.tools) == 1
        
        registry.unregister("test_tool")
        assert len(registry.tools) == 0


class TestBasePlugin:
    """Test base plugin."""
    
    def test_plugin_initialization(self, mock_plugin_config):
        """Test plugin initialization."""
        plugin = BasePlugin(mock_plugin_config)
        assert plugin.config == mock_plugin_config
        assert plugin.tool_registry is not None
    
    def test_plugin_get_tool_definitions(self, mock_plugin_config):
        """Test getting tool definitions from plugin."""
        plugin = BasePlugin(mock_plugin_config)
        
        tool = ToolDefinition(
            name="test_tool",
            description="Test",
            parameters={},
            handler=lambda: {},
            category=ToolCategory.GENERAL
        )
        
        plugin.tool_registry.register(tool)
        definitions = plugin.get_tool_definitions()
        
        assert len(definitions) == 1
        assert definitions[0].name == "test_tool"
    
    def test_plugin_execute_tool(self, mock_plugin_config):
        """Test executing a tool through plugin."""
        plugin = BasePlugin(mock_plugin_config)
        
        def test_handler(param):
            return {"result": param}
        
        tool = ToolDefinition(
            name="test_tool",
            description="Test",
            parameters={
                "type": "object",
                "properties": {"param": {"type": "string"}},
                "required": ["param"]
            },
            handler=test_handler,
            category=ToolCategory.GENERAL
        )
        
        plugin.tool_registry.register(tool)
        result = plugin.execute_tool("test_tool", param="test_value")
        
        assert result["result"] == "test_value"
    
    def test_plugin_execute_nonexistent_tool(self, mock_plugin_config):
        """Test executing non-existent tool raises error."""
        plugin = BasePlugin(mock_plugin_config)
        
        with pytest.raises(ToolExecutionError):
            plugin.execute_tool("nonexistent_tool")


class TestToolCategory:
    """Test tool category enum."""
    
    def test_category_values(self):
        """Test category enum values."""
        assert ToolCategory.GENERAL.value == "general"
        assert ToolCategory.CODE_ANALYSIS.value == "code_analysis"
        assert ToolCategory.GIT_OPERATIONS.value == "git_operations"
        assert ToolCategory.RAG.value == "rag"
        assert ToolCategory.SECURITY.value == "security"
    
    def test_category_from_string(self):
        """Test creating category from string."""
        category = ToolCategory("general")
        assert category == ToolCategory.GENERAL


class TestPluginExceptions:
    """Test plugin exceptions."""
    
    def test_plugin_error(self):
        """Test plugin error."""
        error = PluginError("Test error message")
        assert str(error) == "Test error message"
    
    def test_tool_execution_error(self):
        """Test tool execution error."""
        error = ToolExecutionError("Tool failed", tool_name="test_tool")
        assert "test_tool" in str(error)


class TestProvider:
    """Test provider enum."""
    
    def test_provider_values(self):
        """Test provider enum values."""
        assert Provider.ANTHROPIC.value == "anthropic"
        assert Provider.OPENAI.value == "openai"
        assert Provider.LITELLM.value == "litellm"
    
    def test_provider_from_string(self):
        """Test creating provider from string."""
        provider = Provider("anthropic")
        assert provider == Provider.ANTHROPIC


class TestCustomPlugin:
    """Test creating a custom plugin."""
    
    def test_custom_plugin_inheritance(self, mock_plugin_config):
        """Test creating a custom plugin by inheriting from BasePlugin."""
        
        class CustomPlugin(BasePlugin):
            def __init__(self, config):
                super().__init__(config)
                self.custom_value = "custom"
            
            def custom_method(self):
                return self.custom_value
        
        plugin = CustomPlugin(mock_plugin_config)
        assert plugin.custom_value == "custom"
        assert plugin.custom_method() == "custom"
    
    def test_custom_plugin_with_custom_tools(self, mock_plugin_config):
        """Test custom plugin with custom tools."""
        
        class CustomPlugin(BasePlugin):
            def _register_custom_tools(self):
                # Register custom tools
                pass
        
        plugin = CustomPlugin(mock_plugin_config)
        assert plugin is not None
