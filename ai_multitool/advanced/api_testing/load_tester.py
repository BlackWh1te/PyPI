"""API Load Tester - AI-powered API load testing."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class APILoadTester(AdvancedTool):
    """AI-powered API load testing.
    
    Features:
    - Load test design
    - Performance benchmarking
    - Bottleneck identification
    - Scalability analysis
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "api_load_tester",
            "description": "Design and analyze API load tests",
            "category": ToolCategory.API,
            "parameters": {
                "type": "object",
                "properties": {
                    "api_endpoint": {
                        "type": "string",
                        "description": "API endpoint to load test"
                    },
                    "expected_rps": {
                        "type": "integer",
                        "description": "Expected requests per second"
                    },
                    "test_duration": {
                        "type": "string",
                        "description": "Test duration (e.g., '5m', '1h')"
                    },
                    "include_script": {
                        "type": "boolean",
                        "description": "Include load test script"
                    }
                },
                "required": ["api_endpoint", "expected_rps"]
            }
        }
    
    async def execute(
        self,
        api_endpoint: str,
        expected_rps: int,
        test_duration: str = "5m",
        include_script: bool = False
    ) -> ToolResult:
        """Execute load test analysis.
        
        Args:
            api_endpoint: API endpoint to test
            expected_rps: Expected requests per second
            test_duration: Test duration
            include_script: Include load test script
            
        Returns:
            ToolResult with load test recommendations
        """
        prompt = f"""Design a load test for API endpoint: {api_endpoint}

Expected RPS: {expected_rps}
Test Duration: {test_duration}

Please provide:
1. Load test strategy
2. Test scenarios and user journeys
3. Performance metrics to monitor
4. Bottleneck identification methods
5. Scalability recommendations
"""
        
        if include_script:
            prompt += "\n6. Load test script (using k6, JMeter, or locust)"
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "api_endpoint": api_endpoint,
                "expected_rps": expected_rps,
                "test_duration": test_duration,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Start with baseline performance test",
                "Gradually increase load to find breaking point",
                "Monitor database and cache hit rates"
            ],
            confidence=0.85
        )
