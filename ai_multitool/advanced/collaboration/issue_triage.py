"""Automated issue triage and prioritization."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class AdvancedIssueTriage(AdvancedTool):
    """Automated issue triage and prioritization.
    
    Provides:
    - Issue classification
    - Priority scoring
    - Assignment suggestions
    - Duplicate detection
    - Related issues
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "triage_issues",
            "description": "Automated issue triage and prioritization",
            "parameters": {
                "type": "object",
                "properties": {
                    "issues": {"type": "array", "items": {"type": "object"}},
                    "team_context": {"type": "object"}
                },
                "required": ["issues"]
            }
        }
    
    async def execute(self, issues: List[Dict], team_context: Optional[Dict] = None,
                     **kwargs) -> ToolResult:
        start_time = time.time()
        
        try:
            prompt = f"""Triage and prioritize these issues:

Issues: {json.dumps(issues[:10], indent=2)}
Team context: {team_context or 'none'}

Provide JSON:
{{
    "triaged_issues": [
        {{
            "issue_id": "id",
            "category": "bug|feature|improvement|documentation",
            "priority": "critical|high|medium|low",
            "assignee": "suggested assignee",
            "estimated_effort": "story points or hours",
            "related_issues": ["related issue ids"]
        }}
    ],
    "duplicates": [["issue1", "issue2"]],
    "recommendations": ["triage improvements"]
}}"""
            
            response = await self.llm_client.chat([Message(role=MessageRole.USER, content=prompt)])
            
            return ToolResult(
                success=True,
                data={"triage_report": response.content},
                confidence=0.85,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=response.tokens_used
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
