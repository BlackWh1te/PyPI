"""API Contract Tester - AI-powered API contract testing."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class APIContractTester(AdvancedTool):
    """AI-powered API contract testing.
    
    Features:
    - Contract validation
    - Schema compliance
    - Version compatibility
    - Breaking change detection
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "api_contract_tester",
            "description": "Test API contracts and validate schema compliance",
            "category": ToolCategory.API,
            "parameters": {
                "type": "object",
                "properties": {
                    "openapi_spec": {
                        "type": "string",
                        "description": "OpenAPI specification file"
                    },
                    "implementation": {
                        "type": "string",
                        "description": "Implementation code or endpoint"
                    },
                    "check_type": {
                        "type": "string",
                        "enum": ["compliance", "compatibility", "breaking_changes"],
                        "description": "Type of contract check"
                    }
                },
                "required": ["openapi_spec", "check_type"]
            }
        }
    
    async def execute(
        self,
        openapi_spec: str,
        check_type: str = "compliance",
        implementation: Optional[str] = None
    ) -> ToolResult:
        """Execute contract testing.
        
        Args:
            openapi_spec: OpenAPI specification
            check_type: Type of check
            implementation: Implementation code
            
        Returns:
            ToolResult with contract test results
        """
        prompt = f"""Test API contract for: {openapi_spec}

Check Type: {check_type}
"""
        
        if implementation:
            prompt += f"\nImplementation: {implementation}"
        
        prompt += """

Please provide:
1. Contract validation results
2. Schema compliance issues
3. Potential breaking changes
4. Recommendations for fixes
"""
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "openapi_spec": openapi_spec,
                "check_type": check_type,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Use automated contract testing tools",
                "Version your API properly",
                "Document breaking changes clearly"
            ],
            confidence=0.85
        )
