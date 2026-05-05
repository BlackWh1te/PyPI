"""AI-assisted code review."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class AdvancedCodeReview(AdvancedTool):
    """AI-assisted code review.
    
    Provides:
    - Automated code review
    - Best practices checking
    - Style guide compliance
    - Security review
    - Performance review
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "code_review",
            "description": "AI-assisted code review",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "diff": {"type": "string"},
                    "review_focus": {"type": "array", "items": {"type": "string"}, "default": ["all"]}
                },
                "required": []
            }
        }
    
    async def execute(self, code: Optional[str] = None, diff: Optional[str] = None,
                     review_focus: List[str] = None, **kwargs) -> ToolResult:
        start_time = time.time()
        
        try:
            review_focus = review_focus or ["all"]
            
            if diff:
                content = f"Diff to review:\n{diff}"
            elif code:
                content = f"Code to review:\n{code}"
            else:
                return ToolResult(success=False, errors=["No code or diff provided"])
            
            prompt = f"""Perform code review focusing on: {', '.join(review_focus)}

{content}

Provide JSON:
{{
    "review_comments": [
        {{"line": "number", "severity": "critical|high|medium|low", "issue": "what", "suggestion": "fix"}}
    ],
    "overall_assessment": "summary",
    "approval_status": "approved|needs_changes|rejected",
    "confidence": 0.0-1.0
}}"""
            
            response = await self.llm_client.chat([Message(role=MessageRole.USER, content=prompt)])
            
            return ToolResult(
                success=True,
                data={"code_review": response.content},
                confidence=0.85,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=response.tokens_used
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
