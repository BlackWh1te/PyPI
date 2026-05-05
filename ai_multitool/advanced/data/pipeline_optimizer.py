"""Data engineering and pipeline optimization tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class DataPipelineOptimizer(AdvancedTool):
    """AI-powered data pipeline optimization tool.
    
    Analyzes data pipelines for:
    - ETL optimization
    - Data quality checks
    - Schema evolution
    - Partitioning strategies
    - Incremental processing
    - Data lineage
    - Cost optimization
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for data pipeline optimization."""
        return {
            "name": "optimize_data_pipeline",
            "description": "AI-powered data pipeline optimization for ETL, quality, and cost",
            "parameters": {
                "type": "object",
                "properties": {
                    "pipeline_code": {"type": "string", "description": "Data pipeline code"},
                    "pipeline_file": {"type": "string", "description": "Path to pipeline file"},
                    "framework": {"type": "string", "enum": ["airflow", "dbt", "spark", "pandas", "generic"], "default": "generic"},
                    "focus": {"type": "string", "enum": ["all", "performance", "quality", "cost", "reliability"], "default": "all"},
                    "include_quality_checks": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    
    async def execute(
        self,
        pipeline_code: Optional[str] = None,
        pipeline_file: Optional[str] = None,
        framework: str = "generic",
        focus: str = "all",
        include_quality_checks: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Get pipeline code
            if pipeline_file:
                from ...utils.file_utils import read_file
                code = read_file(pipeline_file)
            else:
                code = pipeline_code or ""
            
            # Build optimization prompt
            prompt = self._build_optimization_prompt(code, framework, focus, include_quality_checks)
            
            # Get AI analysis
            response = await self.llm_client.chat([
                Message(role=MessageRole.USER, content=prompt)
            ])
            
            # Parse response
            optimizations = self._parse_optimizations(response.content)
            
            execution_time = (time.time() - start_time) * 1000
            
            return ToolResult(
                success=True,
                status=ToolStatus.SUCCESS,
                data={
                    "optimizations": optimizations,
                    "total_optimizations": len(optimizations),
                    "framework": framework,
                    "focus_area": focus
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "cost_savings": self._estimate_cost_savings(optimizations),
                    "quality_improvements": len([o for o in optimizations if o.get("category") == "quality"])
                },
                suggestions=[f"{o['category']}: {o['description']}" for o in optimizations],
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
    
    def _build_optimization_prompt(self, code: str, framework: str, focus: str, include_quality_checks: bool) -> str:
        quality_instruction = "Include data quality check recommendations." if include_quality_checks else ""
        
        return f"""Optimize this {framework} data pipeline:

```python
{code}
```

Focus area: {focus}
{quality_instruction}

Provide response in JSON format:
{{
    "optimizations": [
        {{
            "category": "performance|quality|cost|reliability|partitioning",
            "severity": "critical|high|medium|low",
            "description": "What can be improved",
            "current_issue": "Current approach",
            "recommendation": "Suggested improvement",
            "code_example": "Example of optimized code",
            "expected_benefit": "Expected benefit (e.g., '50% faster processing')"
        }}
    ],
    "optimized_pipeline": "Optimized pipeline code",
    "summary": "Overall pipeline optimization summary",
    "confidence": 0.0-1.0
}}"""
    
    def _parse_optimizations(self, response: str) -> List[Dict[str, Any]]:
        import json
        import re
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("optimizations", [])
        except json.JSONDecodeError:
            pass
        
        return []
    
    def _estimate_cost_savings(self, optimizations: List[Dict[str, Any]]) -> str:
        """Estimate potential cost savings."""
        cost_optimizations = [o for o in optimizations if o.get("category") == "cost"]
        
        if not cost_optimizations:
            return "0%"
        
        savings = min(len(cost_optimizations) * 18, 55)  # Max 55% savings
        return f"{savings}%"
