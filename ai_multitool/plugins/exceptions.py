"""Plugin-specific exceptions."""

from ..core.exceptions import AIMultitoolError


class PluginError(AIMultitoolError):
    """Base exception for plugin errors."""

    def __init__(self, message: str, details: str = ""):
        super().__init__(message, details)
        self.message = message
        self.details = details


class ToolExecutionError(PluginError):
    """Exception raised when tool execution fails."""

    def __init__(self, tool_name: str, reason: str, details: str = ""):
        message = f"Tool '{tool_name}' execution failed: {reason}"
        super().__init__(message, details)
        self.tool_name = tool_name
        self.reason = reason


class ToolNotFoundError(PluginError):
    """Exception raised when a requested tool is not found."""

    def __init__(self, tool_name: str, details: str = ""):
        message = f"Tool '{tool_name}' not found in registry"
        super().__init__(message, details)
        self.tool_name = tool_name


class PluginConfigError(PluginError):
    """Exception raised when plugin configuration is invalid."""

    def __init__(self, config_key: str, reason: str, details: str = ""):
        message = f"Invalid plugin configuration for '{config_key}': {reason}"
        super().__init__(message, details)
        self.config_key = config_key
        self.reason = reason
