"""Sprint and release planning assistance."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class AdvancedPlanning(AdvancedTool):
    """Sprint and release planning assistance.
    
    Provides:
    - Sprint planning
    - Release planning
    - Task breakdown
    - Timeline estimation
    - Resource allocation
    """
    
    
        """Get the tool definition for planning.

Returns:
    Tool definition dictionary with name, description, and parameters schema.
    The definition follows the standard tool registration format for
    integration with AI systems and CLI tools.
"""
        
            "name": "planning_assistance",
            "description": "Sprint and release planning assistance",
            "parameters": {
                "type": "object",
                "properties": {
                    "planning_type": {"type": "string", "enum": ["sprint", "release", "roadmap"], "default": "sprint"},
                    "backlog": {"type": "array", "items": {"type": "object"}},
                    "team_capacity": {"type": "number"},
                    "timeline": {"type": "string"}
                },
                "required": ["planning_type"]
            }
        }
    
    async def execute(self, planning_type: str = "sprint", backlog: Optional[List[Dict]] = None,
                     team_capacity: Optional[int] = None, timeline: Optional[str] = None, **kwargs) -> ToolResult:
        start_time = time.time()
        
        try:
            prompt = f"""Create {planning_type} plan
            
            Backlog: {json.dumps(backlog[:10], indent=2) if backlog else 'none'}
            Team capacity: {team_capacity or 'not specified'}
            Timeline: {timeline or 'not specified'}
            
            Provide JSON:
            {{
                "plan": {{
                    "sprint_name": "name",
                    "duration": "weeks",
                    "goals": ["goals"],
                    "selected_items": [{"item": "task", "effort": "points"}]
                }},
                "risks": ["potential risks"],
                "recommendations": ["planning advice"]
            }}"""
            
            response = await self.llm_client.chat([Message(role=MessageRole.USER, content=prompt)])
            
            return ToolResult(
                success=True,
                data={"plan": response.content},
                confidence=0.85,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=response.tokens_used
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
