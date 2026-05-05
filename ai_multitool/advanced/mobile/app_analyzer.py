"""Mobile application analysis tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class MobileAppAnalyzer(AdvancedTool):
    """AI-powered mobile app analysis tool.
    
    Analyzes mobile applications for:
    - Performance optimization
    - Battery usage
    - Memory management
    - UI/UX improvements
    - App size optimization
    - Network efficiency
    - Platform-specific best practices
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for mobile app analysis."""
        return {
            "name": "analyze_mobile_app",
            "description": "AI-powered mobile app analysis for performance, battery, and UX optimization",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_code": {"type": "string", "description": "Mobile app code"},
                    "app_file": {"type": "string", "description": "Path to app file"},
                    "platform": {"type": "string", "enum": ["ios", "android", "flutter", "react_native", "generic"], "default": "generic"},
                    "focus": {"type": "string", "enum": ["all", "performance", "battery", "memory", "ux", "size"], "default": "all"},
                    "include_platform_specific": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    
    async def execute(
        self,
        app_code: Optional[str] = None,
        app_file: Optional[str] = None,
        platform: str = "generic",
        focus: str = "all",
        include_platform_specific: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Get app code
            if app_file:
                from ...utils.file_utils import read_file
                code = read_file(app_file)
            else:
                code = app_code or ""
            
            # Build analysis prompt
            prompt = self._build_analysis_prompt(code, platform, focus, include_platform_specific)
            
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
                    "battery_savings": self._estimate_battery_savings(recommendations)
                },
                suggestions=[f"{r['category']}: {r['description']}" for r in recommendations],
                confidence=0.80,
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
    
    def _build_analysis_prompt(self, code: str, platform: str, focus: str, include_platform_specific: bool) -> str:
        platform_instruction = "Include platform-specific best practices." if include_platform_specific else ""
        
        return f"""Analyze this {platform} mobile app code:

```code
{code}
```

Focus area: {focus}
{platform_instruction}

Provide response in JSON format:
{{
    "recommendations": [
        {{
            "category": "performance|battery|memory|ux|size|network",
            "severity": "critical|high|medium|low",
            "description": "What can be improved",
            "current_issue": "Current problematic pattern",
            "recommendation": "Suggested improvement",
            "code_example": "Example of optimized code",
            "expected_benefit": "Expected benefit (e.g., '20% less battery usage')"
        }}
    ],
    "summary": "Overall app analysis summary",
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
    
    def _estimate_battery_savings(self, recommendations: List[Dict[str, Any]]) -> str:
        """Estimate potential battery savings."""
        battery_recommendations = [r for r in recommendations if r.get("category") == "battery"]
        
        if not battery_recommendations:
            return "0%"
        
        savings = min(len(battery_recommendations) * 10, 40)  # Max 40% savings
        return f"{savings}%"
