"""Error Tracker - AI-powered error tracking and analysis."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class ErrorTracker(AdvancedTool):
    """AI-powered error tracking and analysis.
    
    Features:
    - Error aggregation
    - Error pattern detection
    - Root cause analysis
    - Error frequency analysis
    - Resolution recommendations
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "error_tracker",
            "description": "Track and analyze errors with AI-powered analysis",
            "category": ToolCategory.MONITORING,
            "parameters": {
                "type": "object",
                "properties": {
                    "error_data": {
                        "type": "string",
                        "description": "Error logs or stack traces"
                    },
                    "error_type": {
                        "type": "string",
                        "enum": ["application", "database", "network", "system", "all"],
                        "description": "Type of errors"
                    },
                    "severity_filter": {
                        "type": "string",
                        "enum": ["critical", "high", "medium", "low", "all"],
                        "description": "Minimum severity to include"
                    },
                    "include_grouping": {
                        "type": "boolean",
                        "description": "Group similar errors"
                    }
                },
                "required": ["error_data", "error_type"]
            }
        }
    
    async def execute(
        self,
        error_data: str,
        error_type: str,
        severity_filter: str = "all",
        include_grouping: bool = True
    ) -> ToolResult:
        """Execute error tracking and analysis.
        
        Args:
            error_data: Error data
            error_type: Type of errors
            severity_filter: Severity filter
            include_grouping: Group similar errors
            
        Returns:
            ToolResult with error analysis
        """
        prompt = f"""Analyze error data for tracking and resolution

Error Type: {error_type}
Severity Filter: {severity_filter}
Group Similar Errors: {include_grouping}

Error Data:
```
{error_data}
```

Please provide:
1. Error summary and statistics
2. Error frequency analysis
3. Error patterns and groupings (if requested)
4. Root cause analysis
5. Critical errors requiring immediate attention
6. Resolution recommendations
7. Prevention strategies
8. Suggested alerts and monitoring
"""
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "error_type": error_type,
                "severity_filter": severity_filter,
                "include_grouping": include_grouping,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Implement structured error logging",
                "Use error tracking tools (Sentry, Rollbar)",
                "Set up alerts for critical errors",
                "Regularly review and address recurring errors"
            ],
            confidence=0.85
        )
