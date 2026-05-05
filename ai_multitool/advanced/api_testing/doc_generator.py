"""API Doc Generator - AI-powered OpenAPI/Swagger spec generation."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class APIDocGenerator(AdvancedTool):
    """AI-powered API documentation generation.
    
    Features:
    - OpenAPI/Swagger spec generation
    - API docs from code
    - Interactive API docs
    - API versioning
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "api_doc_generator",
            "description": "Generate OpenAPI/Swagger specifications and API documentation",
            "category": ToolCategory.API,
            "parameters": {
                "type": "object",
                "properties": {
                    "code_file": {
                        "type": "string",
                        "description": "Code file with API endpoints"
                    },
                    "framework": {
                        "type": "string",
                        "enum": ["fastapi", "flask", "express", "django", "spring"],
                        "description": "Framework used"
                    },
                    "version": {
                        "type": "string",
                        "description": "API version"
                    },
                    "include_examples": {
                        "type": "boolean",
                        "description": "Include request/response examples"
                    }
                },
                "required": ["code_file"]
            }
        }
    
    async def execute(
        self,
        code_file: str,
        framework: str = "fastapi",
        version: str = "1.0.0",
        include_examples: bool = False
    ) -> ToolResult:
        """Execute API documentation generation.
        
        Args:
            code_file: Code file with API endpoints
            framework: Framework used
            version: API version
            include_examples: Include examples
            
        Returns:
            ToolResult with OpenAPI specification
        """
        prompt = f"""Generate OpenAPI/Swagger specification for: {code_file}

Framework: {framework}
API Version: {version}

Please provide:
1. OpenAPI 3.0 specification
2. Endpoint definitions
3. Request/response schemas
4. Authentication requirements
"""
        
        if include_examples:
            prompt += "\n5. Request and response examples"
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "code_file": code_file,
                "framework": framework,
                "version": version,
                "specification": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Use OpenAPI tools for validation",
                "Add detailed descriptions for each endpoint",
                "Include authentication schemes"
            ],
            confidence=0.85
        )
