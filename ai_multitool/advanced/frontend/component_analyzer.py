"""Frontend and UI component analysis tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class ComponentAnalyzer(AdvancedTool):
    """AI-powered frontend component analysis tool.
    
    Analyzes frontend components for:
    - Performance optimization
    - Accessibility improvements
    - Responsive design
    - State management
    - Component reusability
    - Bundle size optimization
    - SEO considerations
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for component analysis."""
        return {
            "name": "analyze_components",
            "description": "AI-powered frontend component analysis for performance, accessibility, and UX",
            "parameters": {
                "type": "object",
                "properties": {
                    "component_code": {"type": "string", "description": "Component code"},
                    "component_file": {"type": "string", "description": "Path to component file"},
                    "framework": {"type": "string", "enum": ["react", "vue", "angular", "svelte", "generic"], "default": "generic"},
                    "focus": {"type": "string", "enum": ["all", "performance", "accessibility", "responsive", "reusability", "bundle"], "default": "all"},
                    "include_a11y": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    
    async def execute(
        self,
        component_code: Optional[str] = None,
        component_file: Optional[str] = None,
        framework: str = "generic",
        focus: str = "all",
        include_a11y: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Get component code
            if component_file:
                from ...utils.file_utils import read_file
                code = read_file(component_file)
            else:
                code = component_code or ""
            
            # Build analysis prompt
            prompt = self._build_analysis_prompt(code, framework, focus, include_a11y)
            
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
                    "framework": framework,
                    "focus_area": focus
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "a11y_score": self._calculate_a11y_score(recommendations),
                    "performance_score": self._calculate_performance_score(recommendations)
                },
                suggestions=[f"{r['category']}: {r['description']}" for r in recommendations],
                confidence=0.83,
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
    
    def _build_analysis_prompt(self, code: str, framework: str, focus: str, include_a11y: bool) -> str:
        a11y_instruction = "Include accessibility (WCAG) recommendations." if include_a11y else ""
        
        return f"""Analyze this {framework} frontend component:

```jsx
{code}
```

Focus area: {focus}
{a11y_instruction}

Provide response in JSON format:
{{
    "recommendations": [
        {{
            "category": "performance|accessibility|responsive|reusability|bundle|state",
            "severity": "critical|high|medium|low",
            "description": "What can be improved",
            "current_issue": "Current problematic pattern",
            "recommendation": "Suggested improvement",
            "code_example": "Example of optimized code",
            "wcag_level": "A|AA|AAA (if accessibility)"
        }}
    ],
    "optimized_component": "Optimized component code",
    "summary": "Overall component analysis summary",
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
    
    def _calculate_a11y_score(self, recommendations: List[Dict[str, Any]]) -> str:
        """Calculate accessibility score based on recommendations."""
        a11y_issues = [r for r in recommendations if r.get("category") == "accessibility"]
        
        if not a11y_issues:
            return "excellent"
        elif len(a11y_issues) <= 2:
            return "good"
        elif len(a11y_issues) <= 5:
            return "fair"
        else:
            return "poor"
    
    def _calculate_performance_score(self, recommendations: List[Dict[str, Any]]) -> str:
        """Calculate performance score based on recommendations."""
        perf_issues = [r for r in recommendations if r.get("category") == "performance"]
        
        if not perf_issues:
            return "excellent"
        elif len(perf_issues) <= 2:
            return "good"
        elif len(perf_issues) <= 5:
            return "fair"
        else:
            return "poor"
