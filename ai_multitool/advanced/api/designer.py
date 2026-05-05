"""API design and documentation tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class APIDesigner(AdvancedTool):
    """AI-powered API design tool.
    
    Helps design RESTful APIs including:
    - Endpoint structure
    - Request/response schemas
    - Authentication strategies
    - Rate limiting design
    - Error handling patterns
    - Versioning strategies
    - OpenAPI/Swagger spec generation
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for API design."""
        return {
            "name": "design_api",
            "description": "AI-powered API design with OpenAPI specification generation",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "API purpose and requirements"},
                    "resources": {"type": "array", "items": {"type": "string"}, "description": "List of resources/entities"},
                    "operations": {"type": "array", "items": {"type": "string"}, "description": "CRUD operations needed"},
                    "authentication": {"type": "string", "enum": ["none", "api_key", "jwt", "oauth2", "basic"], "default": "jwt"},
                    "style": {"type": "string", "enum": ["rest", "graphql", "grpc"], "default": "rest"},
                    "include_swagger": {"type": "boolean", "default": True}
                },
                "required": ["description"]
            }
        }
    
    async def execute(
        self,
        description: str,
        resources: Optional[List[str]] = None,
        operations: Optional[List[str]] = None,
        authentication: str = "jwt",
        style: str = "rest",
        include_swagger: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Build design prompt
            prompt = self._build_design_prompt(description, resources, operations, authentication, style, include_swagger)
            
            # Get AI analysis
            response = await self.llm_client.chat([
                Message(role=MessageRole.USER, content=prompt)
            ])
            
            # Parse response
            api_design = self._parse_api_design(response.content)
            
            execution_time = (time.time() - start_time) * 1000
            
            return ToolResult(
                success=True,
                status=ToolStatus.SUCCESS,
                data={
                    "api_design": api_design,
                    "endpoints": api_design.get("endpoints", []),
                    "authentication": authentication,
                    "api_style": style
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "total_endpoints": len(api_design.get("endpoints", [])),
                    "complexity_score": self._calculate_complexity(api_design)
                },
                suggestions=api_design.get("suggestions", []),
                confidence=0.85,
                execution_time_ms=execution_time,
                tokens_used=response.tokens_used
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ToolResult(
                success=False,
                status=ToolStatus.FAILED,
                errors=[str(e)],
                execution_time_ms=execution_time
            )
    
    def _build_design_prompt(self, description: str, resources: List[str], operations: List[str], 
                            authentication: str, style: str, include_swagger: bool) -> str:
        resources_str = ", ".join(resources) if resources else "to be determined"
        operations_str = ", ".join(operations) if operations else "standard CRUD"
        swagger_instruction = "Include OpenAPI/Swagger specification." if include_swagger else ""
        
        return f"""Design a {style} API with the following requirements:

Description: {description}
Resources: {resources_str}
Operations: {operations_str}
Authentication: {authentication}
{swagger_instruction}

Provide response in JSON format:
{{
    "endpoints": [
        {{
            "path": "/api/resource",
            "method": "GET|POST|PUT|DELETE",
            "description": "Endpoint purpose",
            "parameters": [
                {{
                    "name": "param_name",
                    "type": "string|integer|boolean",
                    "location": "query|path|body",
                    "required": true|false,
                    "description": "Parameter description"
                }}
            ],
            "responses": {{
                "200": {{
                    "description": "Success response",
                    "schema": "Response schema"
                }}
            }}
        }}
    ],
    "authentication": {{
        "type": "authentication type",
        "description": "How authentication works"
    }},
    "swagger_spec": "OpenAPI specification (if include_swagger)",
    "suggestions": ["Design suggestions"],
    "summary": "Overall API design summary",
    "confidence": 0.0-1.0
}}"""
    
    def _parse_api_design(self, response: str) -> Dict[str, Any]:
        import json
        import re
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return data
        except json.JSONDecodeError:
            pass
        
        return {"endpoints": [], "suggestions": []}
    
    def _calculate_complexity(self, api_design: Dict[str, Any]) -> str:
        """Calculate API complexity based on endpoints."""
        endpoint_count = len(api_design.get("endpoints", []))
        
        if endpoint_count < 5:
            return "simple"
        elif endpoint_count < 15:
            return "moderate"
        else:
            return "complex"
