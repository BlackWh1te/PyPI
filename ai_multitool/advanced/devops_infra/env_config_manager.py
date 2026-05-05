"""Environment Config Manager - AI-powered environment configuration management."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class EnvConfigManager(AdvancedTool):
    """AI-powered environment configuration management.
    
    Features:
    - Environment variable management
    - Configuration validation
    - Secret detection
    - Environment-specific configs
    - Config migration
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "env_config_manager",
            "description": "Manage environment configurations with AI-powered analysis",
            "category": ToolCategory.DEVOPS,
            "parameters": {
                "type": "object",
                "properties": {
                    "config_file": {
                        "type": "string",
                        "description": "Configuration file content or path"
                    },
                    "environment": {
                        "type": "string",
                        "enum": ["development", "staging", "production", "test"],
                        "description": "Target environment"
                    },
                    "config_type": {
                        "type": "string",
                        "enum": ["env", "yaml", "json", "toml", "ini"],
                        "description": "Configuration file type"
                    },
                    "validate_secrets": {
                        "type": "boolean",
                        "description": "Check for exposed secrets"
                    }
                },
                "required": ["config_file", "environment"]
            }
        }
    
    async def execute(
        self,
        config_file: str,
        environment: str,
        config_type: str = "env",
        validate_secrets: bool = True
    ) -> ToolResult:
        """Execute environment configuration management.
        
        Args:
            config_file: Configuration file content
            environment: Target environment
            config_type: Configuration type
            validate_secrets: Check for secrets
            
        Returns:
            ToolResult with configuration analysis
        """
        prompt = f"""Analyze environment configuration for {environment}

Configuration Type: {config_type}
Validate Secrets: {validate_secrets}

Configuration:
```
{config_file}
```

Please provide:
1. Configuration structure analysis
2. Missing required variables
3. Exposed secrets (if validation enabled)
4. Environment-specific recommendations
5. Security best practices
6. Configuration validation rules
7. Suggestions for config organization
8. Migration tips between environments
"""
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "environment": environment,
                "config_type": config_type,
                "validate_secrets": validate_secrets,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Use secret management for sensitive values",
                "Validate configurations at startup",
                "Document all environment variables",
                "Use different configs per environment"
            ],
            confidence=0.85
        )
