"""Configuration management using Pydantic Settings"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # API Keys
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    openai_api_key: str = Field(default="", description="OpenAI API key")

    # Model Configuration
    default_model: str = Field(
        default="claude-3-sonnet-20240229",
        description="Default AI model to use",
    )
    max_tokens: int = Field(default=4096, description="Maximum tokens for AI responses")
    temperature: float = Field(default=0.7, description="Temperature for AI responses")

    # CLI Configuration
    output_format: str = Field(
        default="rich", description="Output format: rich, json, plain"
    )
    log_level: str = Field(default="INFO", description="Logging level")

    # File Watching
    watch_debounce: float = Field(
        default=0.5, description="Debounce time for file watching (seconds)"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def get_anthropic_key(self) -> str:
        """Get Anthropic API key from settings or keyring"""
        if self.anthropic_api_key:
            return self.anthropic_api_key
        
        # Try keyring as fallback
        try:
            from ai_multitool.utils.key_manager import get_key_manager
            key_manager = get_key_manager()
            key = key_manager.get_anthropic_key()
            if key:
                return key
        except Exception:
            pass
        
        return ""
    
    def get_openai_key(self) -> str:
        """Get OpenAI API key from settings or keyring"""
        if self.openai_api_key:
            return self.openai_api_key
        
        # Try keyring as fallback
        try:
            from ai_multitool.utils.key_manager import get_key_manager
            key_manager = get_key_manager()
            key = key_manager.get_openai_key()
            if key:
                return key
        except Exception:
            pass
        
        return ""


def get_settings() -> Settings:
    """Get application settings"""
    return Settings()


# Global settings instance
settings = get_settings()
