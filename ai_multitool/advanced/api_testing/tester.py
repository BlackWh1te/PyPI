"""API Tester - AI-powered API request testing and validation."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class APITester(AdvancedTool):
    """AI-powered API request testing and validation.
    
    Features:
    - API request testing
    - Response validation
    - Error detection
    - Performance analysis
    - Security checks
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "api_tester",
            "description": "Test and validate API requests with AI-powered analysis",
            "category": ToolCategory.API,
            "parameters": {
                "type": "object",
                "properties": {
                    "api_endpoint": {
                        "type": "string",
                        "description": "API endpoint URL or OpenAPI spec file"
                    },
                    "test_type": {
                        "type": "string",
                        "enum": ["request", "response", "security", "performance"],
                        "description": "Type of API test to perform"
                    },
                    "http_method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                        "description": "HTTP method to test"
                    },
                    "include_examples": {
                        "type": "boolean",
                        "description": "Include test examples in output"
                    }
                },
                "required": ["api_endpoint", "test_type"]
            }
        }
    
    async def execute(
        self,
        api_endpoint: str,
        test_type: str = "request",
        http_method: str = "GET",
        include_examples: bool = False
    ) -> ToolResult:
        """Execute API testing.
        
        Args:
            api_endpoint: API endpoint URL or OpenAPI spec file
            test_type: Type of test (request, response, security, performance)
            http_method: HTTP method to test
            include_examples: Include test examples
            
        Returns:
            ToolResult with test results and recommendations
        """
        prompt = f"""Analyze and test the API endpoint: {api_endpoint}

Test Type: {test_type}
HTTP Method: {http_method}

Please provide:
1. Test scenarios for this endpoint
2. Expected response structure
3. Potential issues to check
4. Security considerations
5. Performance recommendations
"""
        
        if include_examples:
            prompt += "\n6. Example test cases with curl/httpie commands"
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "api_endpoint": api_endpoint,
                "test_type": test_type,
                "http_method": http_method,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Implement automated tests for this endpoint",
                "Add response validation checks",
                "Monitor API performance metrics"
            ],
            confidence=0.85
        )
