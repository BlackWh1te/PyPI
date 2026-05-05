"""Accessibility auditing tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class AccessibilityAuditor(AdvancedTool):
    """AI-powered accessibility auditing tool.
    
    Analyzes for:
    - WCAG compliance
    - Screen reader compatibility
    - Keyboard navigation
    - Color contrast
    - Alt text
    - ARIA attributes
    - Focus management
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for accessibility auditing."""
        return {
            "name": "audit_accessibility",
            "description": "AI-powered accessibility auditing with WCAG compliance checking",
            "parameters": {
                "type": "object",
                "properties": {
                    "html_content": {"type": "string", "description": "HTML content"},
                    "component_code": {"type": "string", "description": "Component code"},
                    "wcag_level": {"type": "string", "enum": ["A", "AA", "AAA"], "default": "AA"},
                    "focus": {"type": "string", "enum": ["all", "contrast", "keyboard", "screen_reader", "aria"], "default": "all"},
                    "include_fixes": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    
    async def execute(
        self,
        html_content: Optional[str] = None,
        component_code: Optional[str] = None,
        wcag_level: str = "AA",
        focus: str = "all",
        include_fixes: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Truncate input
            if html_content:
                html_content = self._truncate_input(html_content, "text")
            if component_code:
                component_code = self._truncate_input(component_code, "code")
            
            # Build audit prompt
            prompt = self._build_audit_prompt(html_content, component_code, wcag_level, focus, include_fixes)
            
            # Optimize prompt
            prompt = self._optimize_prompt(prompt)
            
            # Check cache
            cache_key = self._get_cache_key(html=html_content, code=component_code, wcag=wcag_level, focus=focus)
            cached_result = await self._get_cached(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Get AI analysis
            response = await self.llm_client.chat([
                Message(role=MessageRole.USER, content=prompt)
            ])
            
            # Parse response
            issues = self._parse_issues(response.content)
            
            execution_time = (time.time() - start_time) * 1000
            
            result = ToolResult(
                success=True,
                status=ToolStatus.SUCCESS,
                data={
                    "issues": issues,
                    "total_issues": len(issues),
                    "wcag_level": wcag_level,
                    "focus_area": focus
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "critical_issues": len([i for i in issues if i.get("severity") == "critical"]),
                    "a11y_score": self._calculate_a11y_score(issues)
                },
                suggestions=[f"{i['category']}: {i['description']}" for i in issues],
                confidence=0.85,
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
    
    def _build_audit_prompt(self, html: str, code: str, wcag: str, focus: str, include_fixes: bool) -> str:
        html_section = f"\nHTML:\n{html[:3000]}" if html else ""
        code_section = f"\nCode:\n{code[:3000]}" if code else ""
        fix_instruction = "Include fixes." if include_fixes else ""
        
        return f"""Audit WCAG {wcag} compliance (focus: {focus}):{html_section}{code_section}
{fix_instruction}
JSON: {{"issues":[{{"category","severity","desc","location","fix"}}],"score"}}"""
    
    def _parse_issues(self, response: str) -> List[Dict[str, Any]]:
        import json
        import re
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("issues", [])
        except json.JSONDecodeError:
            pass
        
        return []
    
    def _calculate_a11y_score(self, issues: List[Dict[str, Any]]) -> str:
        critical = len([i for i in issues if i.get("severity") == "critical"])
        if critical == 0:
            return "compliant"
        elif critical <= 2:
            return "mostly_compliant"
        elif critical <= 5:
            return "partially_compliant"
        else:
            return "non_compliant"
