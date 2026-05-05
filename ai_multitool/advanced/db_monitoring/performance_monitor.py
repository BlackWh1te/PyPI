"""Performance Monitor - AI-powered performance monitoring and analysis."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class PerformanceMonitor(AdvancedTool):
    """AI-powered performance monitoring and analysis.
    
    Features:
    - Performance metrics analysis
    - Bottleneck identification
    - Trend analysis
    - Capacity planning
    - Optimization recommendations
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "performance_monitor",
            "description": "Monitor and analyze performance with AI-powered analysis",
            "category": ToolCategory.MONITORING,
            "parameters": {
                "type": "object",
                "properties": {
                    "metrics_data": {
                        "type": "string",
                        "description": "Performance metrics data"
                    },
                    "metric_type": {
                        "type": "string",
                        "enum": ["cpu", "memory", "io", "network", "database", "application", "all"],
                        "description": "Type of metrics"
                    },
                    "time_period": {
                        "type": "string",
                        "description": "Time period for analysis (e.g., '1h', '24h', '7d')"
                    },
                    "include_forecast": {
                        "type": "boolean",
                        "description": "Include performance forecast"
                    }
                },
                "required": ["metrics_data", "metric_type"]
            }
        }
    
    async def execute(
        self,
        metrics_data: str,
        metric_type: str,
        time_period: Optional[str] = None,
        include_forecast: bool = False
    ) -> ToolResult:
        """Execute performance monitoring.
        
        Args:
            metrics_data: Metrics data
            metric_type: Type of metrics
            time_period: Time period
            include_forecast: Include forecast
            
        Returns:
            ToolResult with performance analysis
        """
        prompt = f"""Analyze performance metrics

Metric Type: {metric_type}
Time Period: {time_period or 'all available'}

Metrics Data:
```
{metrics_data}
```

Please provide:
1. Performance trends and patterns
2. Bottlenecks and hotspots
3. Anomalies and outliers
4. Resource utilization analysis
5. Performance baseline comparison
6. Optimization recommendations
7. Capacity planning insights
8. SLO/SLA compliance (if applicable)
"""
        
        if include_forecast:
            prompt += "\n9. Performance forecast and predictions"
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "metric_type": metric_type,
                "time_period": time_period,
                "include_forecast": include_forecast,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Set up automated performance monitoring",
                "Define performance baselines and thresholds",
                "Implement proactive alerting",
                "Regularly review and optimize based on metrics"
            ],
            confidence=0.85
        )
