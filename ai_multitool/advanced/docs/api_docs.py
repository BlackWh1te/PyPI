"""API documentation from code."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class AdvancedAPIDocs(AdvancedTool):
    """API documentation from code.
    
    Generates:
    - OpenAPI/Swagger specs
    - API reference docs
    - Endpoint documentation
    - Request/response schemas
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "generate_api_docs",
            "description": "API documentation from code",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "format": {"type": "string", "enum": ["openapi", "swagger", "markdown", "html"], "default": "openapi"}
                },
                "required": ["code"]
            }
        }
    
    async def execute(self, code: str, format: str = "openapi", **kwargs) -> ToolResult:
        start_time = time.time()
        
        try:
            prompt = f"""Generate {format} API documentation from this code:

Code:
{code[:3000]}

Provide JSON:
{{
    "api_spec": "openapi/swagger spec",
    "endpoints": [
        {{"path": "/path", "method": "GET", "description": "what", "parameters": []}}
    ],
    "schemas": {"type": "schema"},
    "documentation": "full docs"
}}"""
            
            response = await self.llm_client.chat([Message(role=MessageRole.USER, content=prompt)])
            
            return ToolResult(
                success=True,
                data={"api_documentation": response.content},
                confidence=0.85,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=response.tokens_used
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
