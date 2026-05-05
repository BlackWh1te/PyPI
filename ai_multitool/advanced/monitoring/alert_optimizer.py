"""Monitoring and alerting optimization tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class AlertOptimizer(AdvancedTool):
    """AI-powered monitoring and alerting optimization tool.
    
    Analyzes monitoring configurations for:
    - Alert fatigue reduction
    - Threshold optimization
    - Metric selection
    - Dashboard design
    - Incident response
    - Alert routing
    - Notification strategies
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for alert optimization."""
        return {
            "name": "optimize_alerts",
            "description": "AI-powered monitoring and alerting optimization to reduce alert fatigue",
            "parameters": {
                "type": "object",
                "properties": {
                    "alert_config": {"type": "string", "description": "Alert configuration file or content"},
                    "metrics": {"type": "array", "items": {"type": "string"}, "description": "List of metrics being monitored"},
                    "current_issues": {"type": "string", "description": "Current alerting problems (e.g., 'too many false positives')"},
                    "platform": {"type": "string", "enum": ["prometheus", "datadog", "grafana", "cloudwatch", "newrelic", "generic"], "default": "generic"},
                    "focus": {"type": "string", "enum": ["all", "thresholds", "metrics", "routing", "fatigue"], "default": "all"}
                },
                "required": []
            }
        }
    
    async def execute(
        self,
        alert_config: Optional[str] = None,
        metrics: Optional[List[str]] = None,
        current_issues: Optional[str] = None,
        platform: str = "generic",
        focus: str = "all",
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Build analysis prompt
            prompt = self._build_optimization_prompt(alert_config, metrics, current_issues, platform, focus)
            
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
                    "platform": platform,
                    "focus_area": focus
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "noise_reduction": self._estimate_noise_reduction(optimizations),
                    "alert_coverage": self._assess_coverage(optimizations)
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
    
    def _build_optimization_prompt(self, alert_config: str, metrics: List[str], current_issues: str, platform: str, focus: str) -> str:
        metrics_str = ", ".join(metrics) if metrics else "not specified"
        issues_str = f"\nCurrent Issues: {current_issues}" if current_issues else ""
        config_str = f"\nAlert Config:\n```\n{alert_config}\n```" if alert_config else ""
        
        return f"""Optimize this {platform} monitoring and alerting setup:

Metrics: {metrics_str}
{config_str}
{issues_str}

Focus area: {focus}

Provide response in JSON format:
{{
    "optimizations": [
        {{
            "category": "thresholds|metrics|routing|fatigue|coverage",
            "severity": "critical|high|medium|low",
            "description": "What can be improved",
            "current_issue": "Current problematic pattern",
            "recommendation": "Suggested improvement",
            "code_example": "Example of optimized alert rule",
            "expected_benefit": "Expected benefit (e.g., '50% fewer false positives')"
        }}
    ],
    "optimized_config": "Optimized alert configuration",
    "summary": "Overall optimization summary",
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
    
    def _estimate_noise_reduction(self, optimizations: List[Dict[str, Any]]) -> str:
        """Estimate potential alert noise reduction."""
        fatigue_optimizations = [o for o in optimizations if o.get("category") == "fatigue"]
        
        if not fatigue_optimizations:
            return "0%"
        
        reduction = min(len(fatigue_optimizations) * 25, 80)  # Max 80% reduction
        return f"{reduction}%"
    
    def _assess_coverage(self, optimizations: List[Dict[str, Any]]) -> str:
        """Assess alert coverage improvement."""
        coverage_optimizations = [o for o in optimizations if o.get("category") == "coverage"]
        
        if not coverage_optimizations:
            return "no change"
        
        return "improved"
