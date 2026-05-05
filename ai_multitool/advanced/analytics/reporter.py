"""Analytics and reporting tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class AnalyticsReporter(AdvancedTool):
    """AI-powered analytics reporting tool.
    
    Analyzes data for:
    - Report generation
    - Dashboard design
    - KPI selection
    - Data visualization
    - Trend analysis
    - Anomaly detection
    - Insight generation
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for analytics reporting."""
        return {
            "name": "generate_analytics",
            "description": "AI-powered analytics reporting with dashboard design and KPI selection",
            "parameters": {
                "type": "object",
                "properties": {
                    "data_description": {"type": "string", "description": "Description of data"},
                    "metrics": {"type": "array", "items": {"type": "string"}, "description": "Available metrics"},
                    "goal": {"type": "string", "description": "Business goal (e.g., 'increase sales', 'reduce churn')"},
                    "focus": {"type": "string", "enum": ["all", "kpis", "visualization", "insights", "dashboard"], "default": "all"},
                    "include_sql": {"type": "boolean", "default": True}
                },
                "required": ["data_description"]
            }
        }
    
    async def execute(
        self,
        data_description: str,
        metrics: Optional[List[str]] = None,
        goal: Optional[str] = None,
        focus: str = "all",
        include_sql: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Build analytics prompt
            prompt = self._build_analytics_prompt(data_description, metrics, goal, focus, include_sql)
            
            # Optimize prompt
            prompt = self._optimize_prompt(prompt)
            
            # Check cache
            cache_key = self._get_cache_key(desc=data_description, metrics=metrics, goal=goal, focus=focus)
            cached_result = await self._get_cached(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Get AI analysis
            response = await self.llm_client.chat([
                Message(role=MessageRole.USER, content=prompt)
            ])
            
            # Parse response
            recommendations = self._parse_recommendations(response.content)
            
            execution_time = (time.time() - start_time) * 1000
            
            result = ToolResult(
                success=True,
                status=ToolStatus.SUCCESS,
                data={
                    "recommendations": recommendations,
                    "total_recommendations": len(recommendations),
                    "goal": goal,
                    "focus_area": focus
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "kpis_count": len([r for r in recommendations if r.get("category") == "kpis"])
                },
                suggestions=[f"{r['category']}: {r['description']}" for r in recommendations],
                confidence=0.80,
                execution_time_ms=execution_time,
                tokens_used=response.tokens_used
            )
            
            # Cache result
            await self._set_cached(cache_key, result)
            
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ToolResult(
                success=False,
                status=ToolStatus.FAILED,
                errors=[str(e)],
                execution_time_ms=execution_time
            )
    
    def _build_analytics_prompt(self, desc: str, metrics: List[str], goal: str, focus: str, include_sql: bool) -> str:
        metrics_str = ", ".join(metrics) if metrics else "not specified"
        sql_instruction = "Include SQL queries." if include_sql else ""
        
        return f"""Generate analytics for {desc} (metrics: {metrics_str}, goal: {goal or 'not set'})
Focus: {focus}
{sql_instruction}
JSON: {{"recs":[{{"category","desc","kpi","viz_type","sql"}}],"summary"}}"""
    
    def _parse_recommendations(self, response: str) -> List[Dict[str, Any]]:
        import json
        import re
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("recs", [])
        except json.JSONDecodeError:
            pass
        
        return []
