"""Log Aggregator - AI-powered log aggregation and analysis."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class LogAggregator(AdvancedTool):
    """AI-powered log aggregation and analysis.
    
    Features:
    - Log parsing and normalization
    - Pattern detection
    - Anomaly identification
    - Log summarization
    - Alert generation
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "log_aggregator",
            "description": "Aggregate and analyze logs with AI-powered analysis",
            "category": ToolCategory.LOGGING,
            "parameters": {
                "type": "object",
                "properties": {
                    "log_data": {
                        "type": "string",
                        "description": "Log data to analyze"
                    },
                    "log_format": {
                        "type": "string",
                        "enum": ["json", "text", "syslog", "apache", "nginx", "custom"],
                        "description": "Log format"
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["errors", "patterns", "anomalies", "summary", "all"],
                        "description": "Type of analysis"
                    },
                    "time_range": {
                        "type": "string",
                        "description": "Time range for analysis (e.g., '1h', '24h', '7d')"
                    }
                },
                "required": ["log_data", "log_format"]
            }
        }
    
    async def execute(
        self,
        log_data: str,
        log_format: str,
        analysis_type: str = "all",
        time_range: Optional[str] = None
    ) -> ToolResult:
        """Execute log aggregation and analysis.
        
        Args:
            log_data: Log data
            log_format: Log format
            analysis_type: Analysis type
            time_range: Time range
            
        Returns:
            ToolResult with log analysis
        """
        prompt = f"""Analyze the following log data

Log Format: {log_format}
Analysis Type: {analysis_type}
Time Range: {time_range or 'all available'}

Log Data:
```
{log_data}
```

Please provide:
1. Error patterns and frequency
2. Common log patterns
3. Anomalies and unusual events
4. Log summary and statistics
5. Timeline of significant events
6. Recommended alerts
7. Root cause indicators
8. Performance insights (if available)
"""
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "log_format": log_format,
                "analysis_type": analysis_type,
                "time_range": time_range,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Use structured logging (JSON) for better parsing",
                "Implement log aggregation with ELK or similar",
                "Set up alerts for critical error patterns",
                "Regularly review and refine log queries"
            ],
            confidence=0.85
        )
