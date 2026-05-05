"""Schema Diff Generator - AI-powered database schema difference analysis."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class SchemaDiffGenerator(AdvancedTool):
    """AI-powered database schema difference analysis.
    
    Features:
    - Schema comparison
    - Change detection
    - Impact analysis
    - Breaking change identification
    - Migration path suggestions
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "schema_diff_generator",
            "description": "Generate schema differences with AI-powered analysis",
            "category": ToolCategory.DATABASE,
            "parameters": {
                "type": "object",
                "properties": {
                    "schema_a": {
                        "type": "string",
                        "description": "First schema (baseline)"
                    },
                    "schema_b": {
                        "type": "string",
                        "description": "Second schema (new version)"
                    },
                    "database_type": {
                        "type": "string",
                        "enum": ["postgresql", "mysql", "sqlite", "mongodb", "sqlserver"],
                        "description": "Database type"
                    },
                    "include_impact": {
                        "type": "boolean",
                        "description": "Include impact analysis"
                    }
                },
                "required": ["schema_a", "schema_b", "database_type"]
            }
        }
    
    async def execute(
        self,
        schema_a: str,
        schema_b: str,
        database_type: str,
        include_impact: bool = True
    ) -> ToolResult:
        """Execute schema diff generation.
        
        Args:
            schema_a: First schema
            schema_b: Second schema
            database_type: Database type
            include_impact: Include impact analysis
            
        Returns:
            ToolResult with schema differences
        """
        prompt = f"""Compare two database schemas and generate differences

Database Type: {database_type}

Schema A (Baseline):
```
{schema_a}
```

Schema B (New Version):
```
{schema_b}
```

Please provide:
1. Added tables and columns
2. Removed tables and columns
3. Modified columns (type changes, constraints)
4. Index changes
5. Relationship changes
6. Breaking changes identified
"""
        
        if include_impact:
            prompt += """
7. Impact analysis on existing queries
8. Impact on application code
9. Data migration requirements
10. Risk assessment
"""
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "database_type": database_type,
                "include_impact": include_impact,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Review breaking changes carefully",
                "Test schema changes with representative data",
                "Plan data migration for structural changes",
                "Update application code for schema changes"
            ],
            confidence=0.85
        )
