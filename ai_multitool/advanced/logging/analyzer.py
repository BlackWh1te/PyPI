"""Log analysis and debugging tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class LogAnalyzer(AdvancedTool):
    """AI-powered log analysis tool.
    
    Analyzes log files for:
    - Error patterns and anomalies
    - Performance bottlenecks
    - Security incidents
    - Root cause analysis
    - Trend analysis
    - Alert recommendations
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for log analysis."""
        return {
            "name": "analyze_logs",
            "description": "AI-powered log analysis with anomaly detection and root cause analysis",
            "parameters": {
                "type": "object",
                "properties": {
                    "log_file": {"type": "string", "description": "Path to log file"},
                    "log_content": {"type": "string", "description": "Log content"},
                    "log_format": {"type": "string", "enum": ["json", "text", "syslog", "apache", "nginx", "custom"], "default": "text"},
                    "time_range": {"type": "string", "description": "Time range to analyze (e.g., 'last 1 hour')"},
                    "focus": {"type": "string", "enum": ["all", "errors", "performance", "security", "anomalies"], "default": "all"},
                    "include_patterns": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    
    async def execute(
        self,
        log_file: Optional[str] = None,
        log_content: Optional[str] = None,
        log_format: str = "text",
        time_range: Optional[str] = None,
        focus: str = "all",
        include_patterns: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Get log content
            if log_file:
                from ...utils.file_utils import read_file
                logs = read_file(log_file)
            else:
                logs = log_content or ""
            
            # Build analysis prompt
            prompt = self._build_analysis_prompt(logs, log_format, time_range, focus, include_patterns)
            
            # Get AI analysis
            response = await self.llm_client.chat([
                Message(role=MessageRole.USER, content=prompt)
            ])
            
            # Parse response
            findings = self._parse_findings(response.content)
            
            execution_time = (time.time() - start_time) * 1000
            
            return ToolResult(
                success=True,
                status=ToolStatus.SUCCESS,
                data={
                    "findings": findings,
                    "total_findings": len(findings),
                    "log_format": log_format,
                    "focus_area": focus
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "critical_issues": len([f for f in findings if f.get("severity") == "critical"]),
                    "anomalies_detected": len([f for f in findings if f.get("type") == "anomaly"])
                },
                suggestions=[f"{f['type']}: {f['description']}" for f in findings],
                confidence=0.78,
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
    
    def _build_analysis_prompt(self, logs: str, log_format: str, time_range: str, focus: str, include_patterns: bool) -> str:
        time_instruction = f"Time range: {time_range}" if time_range else ""
        pattern_instruction = "Identify recurring patterns." if include_patterns else ""
        
        return f"""Analyze these {log_format} logs:

```
{logs}
```

{time_instruction}
Focus area: {focus}
{pattern_instruction}

Provide response in JSON format:
{{
    "findings": [
        {{
            "type": "error|warning|anomaly|performance|security",
            "severity": "critical|high|medium|low",
            "timestamp": "When it occurred",
            "description": "What happened",
            "pattern": "Recurring pattern (if any)",
            "root_cause": "Likely root cause",
            "recommendation": "How to fix or prevent"
        }}
    ],
    "summary": "Overall log analysis summary",
    "patterns": ["Recurring patterns identified"],
    "confidence": 0.0-1.0
}}"""
    
    def _parse_findings(self, response: str) -> List[Dict[str, Any]]:
        import json
        import re
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("findings", [])
        except json.JSONDecodeError:
            pass
        
        return []
