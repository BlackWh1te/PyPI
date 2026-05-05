"""Custom exceptions for ai-multitool."""

from typing import Optional, Dict, Any


class AIMultitoolError(Exception):
    """Base exception for all ai-multitool errors."""
    
    def __init__(self, message: str, suggestion: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.suggestion = suggestion
        self.details = details or {}
    
    def __str__(self) -> str:
        result = self.message
        if self.suggestion:
            result += f"\n\n💡 Suggestion: {self.suggestion}"
        if self.details:
            result += f"\n\nDetails: {self.details}"
        return result


class ConfigurationError(AIMultitoolError):
    """Raised when there's a configuration error."""
    pass


class APIKeyError(AIMultitoolError):
    """Raised when API key is missing or invalid."""
    pass


class APIError(AIMultitoolError):
    """Raised when API call fails."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        suggestion: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, suggestion, details)
        self.status_code = status_code
        self.response_body = response_body
    
    def __str__(self) -> str:
        result = self.message
        if self.status_code:
            result += f" (Status: {self.status_code})"
        if self.suggestion:
            result += f"\n\n💡 Suggestion: {self.suggestion}"
        if self.response_body:
            result += f"\n\nResponse: {self.response_body[:200]}..."
        return result


class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        suggestion = f"Wait {retry_after} seconds before retrying" if retry_after else "Wait a few minutes before retrying"
        super().__init__(message, suggestion=suggestion)
        self.retry_after = retry_after


class AuthenticationError(APIError):
    """Raised when authentication fails."""
    
    def __init__(self, provider: str):
        message = f"Authentication failed for {provider}"
        suggestion = f"Check your {provider} API key using 'ai-multitool keys get {provider.lower()}' or set it in .env"
        super().__init__(message, suggestion=suggestion)
        self.provider = provider


class QuotaExceededError(APIError):
    """Raised when API quota is exceeded."""
    
    def __init__(self, provider: str):
        message = f"API quota exceeded for {provider}"
        suggestion = f"Check your {provider} account billing and usage limits"
        super().__init__(message, suggestion=suggestion)
        self.provider = provider


class ModelNotFoundError(APIError):
    """Raised when requested model is not available."""
    
    def __init__(self, model: str, provider: str):
        message = f"Model '{model}' not found for {provider}"
        suggestion = f"Use 'ai-multitool list-models' to see available models"
        super().__init__(message, suggestion=suggestion)
        self.model = model
        self.provider = provider


class FileOperationError(AIMultitoolError):
    """Raised when file operation fails."""
    
    def __init__(self, message: str, file_path: str, suggestion: Optional[str] = None):
        if not suggestion:
            suggestion = f"Check if the file exists and you have read permissions"
        super().__init__(message, suggestion=suggestion)
        self.file_path = file_path


class FileNotFoundError(FileOperationError):
    """Raised when file is not found."""
    
    def __init__(self, file_path: str):
        message = f"File not found: {file_path}"
        super().__init__(message, file_path)
        self.file_path = file_path


class DirectoryNotFoundError(FileOperationError):
    """Raised when directory is not found."""
    
    def __init__(self, dir_path: str):
        message = f"Directory not found: {dir_path}"
        suggestion = "Check if the directory path is correct"
        super().__init__(message, dir_path, suggestion)
        self.dir_path = dir_path


class PermissionError(FileOperationError):
    """Raised when permission is denied."""
    
    def __init__(self, path: str):
        message = f"Permission denied: {path}"
        suggestion = "Check if you have the necessary permissions to access this file/directory"
        super().__init__(message, path, suggestion)
        self.path = path


class GitError(AIMultitoolError):
    """Raised when git operation fails."""
    
    def __init__(self, message: str, suggestion: Optional[str] = None):
        if not suggestion:
            suggestion = "Check if you're in a git repository and git is installed"
        super().__init__(message, suggestion)


class CodeParsingError(AIMultitoolError):
    """Raised when code parsing fails."""
    
    def __init__(self, message: str, file_path: str, suggestion: Optional[str] = None):
        if not suggestion:
            suggestion = "Check if the file is a valid code file"
        super().__init__(message, suggestion, {"file_path": file_path})
        self.file_path = file_path


class SanitizationError(AIMultitoolError):
    """Raised when content sanitization fails."""
    
    def __init__(self, message: str, suggestion: Optional[str] = None):
        if not suggestion:
            suggestion = "Try with --no-sanitize flag if you're sure the content is safe"
        super().__init__(message, suggestion)


class KeyringError(AIMultitoolError):
    """Raised when keyring operation fails."""
    
    def __init__(self, message: str, suggestion: Optional[str] = None):
        if not suggestion:
            suggestion = "Install keyring with: pip install keyring"
        super().__init__(message, suggestion)


class MetricsError(AIMultitoolError):
    """Raised when metrics operation fails."""
    
    def __init__(self, message: str, suggestion: Optional[str] = None):
        if not suggestion:
            suggestion = "Check if ~/.ai-multitool directory is writable"
        super().__init__(message, suggestion)


class ValidationError(AIMultitoolError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, suggestion: Optional[str] = None):
        if field:
            message = f"Validation error for {field}: {message}"
        super().__init__(message, suggestion)
        self.field = field


class NetworkError(AIMultitoolError):
    """Raised when network operation fails."""
    
    def __init__(self, message: str, suggestion: Optional[str] = None):
        if not suggestion:
            suggestion = "Check your internet connection and try again"
        super().__init__(message, suggestion)


class TimeoutError(AIMultitoolError):
    """Raised when operation times out."""
    
    def __init__(self, operation: str, timeout_seconds: int):
        message = f"Operation '{operation}' timed out after {timeout_seconds} seconds"
        suggestion = f"Try increasing the timeout or check if the operation is taking longer than expected"
        super().__init__(message, suggestion)
        self.operation = operation
        self.timeout_seconds = timeout_seconds


class ContextError(AIMultitoolError):
    """Raised when context building fails."""
    
    def __init__(self, message: str, suggestion: Optional[str] = None):
        if not suggestion:
            suggestion = "Try with --no-context flag to disable smart context building"
        super().__init__(message, suggestion)
