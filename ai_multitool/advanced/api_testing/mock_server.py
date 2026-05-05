"""API Mock Server - AI-powered mock server generation."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class APIMockServer(AdvancedTool):
    """AI-powered mock server generation.
    
    Features:
    - Mock server design
    - Response templates
    - State management
    - Scenario testing
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "api_mock_server",
            "description": "Generate mock server configurations for API testing",
            "category": ToolCategory.API,
            "parameters": {
                "type": "object",
                "properties": {
                    "api_spec": {
                        "type": "string",
                        "description": "API specification or endpoint description"
                    },
                    "framework": {
                        "type": "string",
                        "enum": ["mockoon", "wiremock", "json-server", "msw"],
                        "description": "Mock server framework"
                    },
                    "include_scenarios": {
                        "type": "boolean",
                        "description": "Include test scenarios"
                    }
                },
                "required": ["api_spec"]
            }
        }
    
    async def execute(
        self,
        api_spec: str,
        framework: str = "mockoon",
        include_scenarios: bool = False
    ) -> ToolResult:
        """Execute mock server generation.
        
        Args:
            api_spec: API specification
            framework: Mock server framework
            include_scenarios: Include test scenarios
            
        Returns:
            ToolResult with mock server configuration
        """
        prompt = f"""Generate a mock server configuration for: {api_spec}

Framework: {framework}

Please provide:
1. Mock server configuration
2. Response templates
3. Endpoint mappings
4. Error scenarios
"""
        
        if include_scenarios:
            prompt += "\n5. Test scenarios for different use cases"
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "api_spec": api_spec,
                "framework": framework,
                "configuration": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Use realistic response data",
                "Implement error scenarios",
                "Add stateful behavior for complex flows"
            ],
            confidence=0.85
        )
