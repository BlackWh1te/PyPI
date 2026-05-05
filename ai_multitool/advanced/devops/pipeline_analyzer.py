"""DevOps and CI/CD pipeline analysis tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class PipelineAnalyzer(AdvancedTool):
    """AI-powered CI/CD pipeline analysis tool.
    
    Analyzes CI/CD pipelines for:
    - Build optimization
    - Test strategy improvement
    - Deployment safety
    - Pipeline efficiency
    - Security best practices
    - Cost optimization
    - Parallelization opportunities
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for pipeline analysis."""
        return {
            "name": "analyze_pipeline",
            "description": "AI-powered CI/CD pipeline analysis with optimization recommendations",
            "parameters": {
                "type": "object",
                "properties": {
                    "pipeline_file": {"type": "string", "description": "Path to pipeline file (GitHub Actions, GitLab CI, Jenkinsfile, etc.)"},
                    "pipeline_content": {"type": "string", "description": "Pipeline configuration content"},
                    "platform": {"type": "string", "enum": ["github", "gitlab", "jenkins", "circleci", "azure", "generic"], "default": "generic"},
                    "focus": {"type": "string", "enum": ["all", "performance", "security", "cost", "reliability"], "default": "all"},
                    "include_caching": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    
    async def execute(
        self,
        pipeline_file: Optional[str] = None,
        pipeline_content: Optional[str] = None,
        platform: str = "generic",
        focus: str = "all",
        include_caching: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Get pipeline content
            if pipeline_file:
                from ...utils.file_utils import read_file
                pipeline = read_file(pipeline_file)
            else:
                pipeline = pipeline_content or ""
            
            # Build analysis prompt
            prompt = self._build_analysis_prompt(pipeline, platform, focus, include_caching)
            
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
                    "platform": platform,
                    "focus_area": focus
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "critical_issues": len([r for r in recommendations if r.get("severity") == "critical"]),
                    "estimated_time_savings": self._estimate_time_savings(recommendations)
                },
                suggestions=[f"{r['category']}: {r['description']}" for r in recommendations],
                confidence=0.84,
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
    
    def _build_analysis_prompt(self, pipeline: str, platform: str, focus: str, include_caching: bool) -> str:
        caching_instruction = "Include caching strategy recommendations." if include_caching else ""
        
        return f"""Analyze this {platform} CI/CD pipeline:

```yaml
{pipeline}
```

Focus area: {focus}
{caching_instruction}

Provide response in JSON format:
{{
    "recommendations": [
        {{
            "category": "performance|security|cost|reliability|best_practices",
            "severity": "critical|high|medium|low",
            "description": "What can be improved",
            "current_issue": "Current approach",
            "recommendation": "Suggested improvement",
            "code_example": "Example of optimized pipeline step",
            "expected_benefit": "Expected benefit (e.g., '30% faster builds')"
        }}
    ],
    "optimized_pipeline": "Optimized pipeline configuration",
    "summary": "Overall pipeline analysis summary",
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
    
    def _estimate_time_savings(self, recommendations: List[Dict[str, Any]]) -> str:
        """Estimate potential build time savings."""
        perf_recommendations = [r for r in recommendations if r.get("category") == "performance"]
        
        if not perf_recommendations:
            return "0%"
        
        savings = min(len(perf_recommendations) * 12, 50)  # Max 50% savings
        return f"{savings}%"
