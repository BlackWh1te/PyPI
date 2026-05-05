"""Database schema analysis and optimization tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class SchemaAnalyzer(AdvancedTool):
    """AI-powered database schema analysis tool.
    
    Analyzes database schemas for:
    - Normalization issues
    - Index optimization
    - Foreign key relationships
    - Data type efficiency
    - Query performance implications
    - Schema evolution recommendations
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for schema analysis."""
        return {
            "name": "analyze_schema",
            "description": "AI-powered database schema analysis with optimization recommendations",
            "parameters": {
                "type": "object",
                "properties": {
                    "schema_file": {"type": "string", "description": "Path to schema file (SQL, ORM models, etc.)"},
                    "schema_content": {"type": "string", "description": "Schema definition content"},
                    "database_type": {"type": "string", "enum": ["postgresql", "mysql", "sqlite", "mongodb", "generic"], "default": "generic"},
                    "focus": {"type": "string", "enum": ["all", "normalization", "indexes", "performance", "relationships"], "default": "all"},
                    "include_migrations": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    
    async def execute(
        self,
        schema_file: Optional[str] = None,
        schema_content: Optional[str] = None,
        database_type: str = "generic",
        focus: str = "all",
        include_migrations: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Get schema
            if schema_file:
                from ...utils.file_utils import read_file
                schema = read_file(schema_file)
            else:
                schema = schema_content or ""
            
            # Build analysis prompt
            prompt = self._build_analysis_prompt(schema, database_type, focus, include_migrations)
            
            # Get AI analysis
            response = await self.llm_client.chat([
                Message(role=MessageRole.USER, content=prompt)
            ])
            
            # Parse response
            recommendations = self._parse_recommendations(response.content)
            
            execution_time = (time.time() - start_time) * 1000
            
            return ToolResult(
                success=True,
                status=ToolStatus.SUCCESS,
                data={
                    "recommendations": recommendations,
                    "total_recommendations": len(recommendations),
                    "database_type": database_type,
                    "focus_area": focus
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "critical_issues": len([r for r in recommendations if r.get("severity") == "critical"]),
                    "performance_impact": self._assess_performance_impact(recommendations)
                },
                suggestions=[f"{r['category']}: {r['description']}" for r in recommendations],
                confidence=0.82,
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
    
    def _build_analysis_prompt(self, schema: str, database_type: str, focus: str, include_migrations: bool) -> str:
        migration_instruction = "Provide migration scripts for changes." if include_migrations else ""
        
        return f"""Analyze this {database_type} database schema:

```sql
{schema}
```

Focus area: {focus}
{migration_instruction}

Provide response in JSON format:
{{
    "recommendations": [
        {{
            "category": "normalization|indexes|performance|relationships|data_types",
            "severity": "critical|high|medium|low",
            "table": "table name",
            "description": "What the issue is",
            "impact": "Performance or maintenance impact",
            "recommendation": "How to fix it",
            "migration": "SQL migration script (if include_migrations)"
        }}
    ],
    "summary": "Overall schema assessment",
    "confidence": 0.0-1.0
}}"""
    
    def _parse_recommendations(self, response: str) -> List[Dict[str, Any]]:
        import json
        import re
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("recommendations", [])
        except json.JSONDecodeError:
            pass
        
        return []
    
    def _assess_performance_impact(self, recommendations: List[Dict[str, Any]]) -> str:
        """Assess overall performance impact."""
        critical_count = len([r for r in recommendations if r.get("severity") == "critical"])
        high_count = len([r for r in recommendations if r.get("severity") == "high"])
        
        if critical_count > 0:
            return "severe"
        elif high_count > 2:
            return "significant"
        elif high_count > 0:
            return "moderate"
        else:
            return "minimal"
