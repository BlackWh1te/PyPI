"""Test Data Generator - AI-powered test data generation."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class TestDataGenerator(AdvancedTool):
    """AI-powered test data generation.
    
    Features:
    - Synthetic data generation
    - Edge case data creation
    - Mock data generation
    - Test fixture creation
    - Data anonymization
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "test_data_generator",
            "description": "Generate test data with AI-powered analysis",
            "category": ToolCategory.TESTING,
            "parameters": {
                "type": "object",
                "properties": {
                    "schema": {
                        "type": "string",
                        "description": "Data schema or structure description"
                    },
                    "data_type": {
                        "type": "string",
                        "enum": ["json", "csv", "sql", "xml", "yaml"],
                        "description": "Output data format"
                    },
                    "record_count": {
                        "type": "integer",
                        "description": "Number of records to generate"
                    },
                    "include_edge_cases": {
                        "type": "boolean",
                        "description": "Include edge case data"
                    }
                },
                "required": ["schema", "data_type"]
            }
        }
    
    async def execute(
        self,
        schema: str,
        data_type: str,
        record_count: int = 10,
        include_edge_cases: bool = False
    ) -> ToolResult:
        """Execute test data generation.
        
        Args:
            schema: Data schema description
            data_type: Output format
            record_count: Number of records
            include_edge_cases: Include edge cases
            
        Returns:
            ToolResult with generated test data
        """
        prompt = f"""Generate test data based on the following schema

Schema: {schema}
Data Type: {data_type}
Record Count: {record_count}
Include Edge Cases: {include_edge_cases}

Please provide:
1. Generated test data in {data_type} format
2. Data validation examples
3. Edge case scenarios (if requested)
4. Data relationships (if applicable)
5. Sample usage code
6. Data generation script (if complex)
"""
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "schema": schema,
                "data_type": data_type,
                "record_count": record_count,
                "include_edge_cases": include_edge_cases,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Use factories for complex object creation",
                "Generate realistic data for better testing",
                "Include boundary values in edge cases",
                "Use Faker libraries for realistic dummy data"
            ],
            confidence=0.85
        )
