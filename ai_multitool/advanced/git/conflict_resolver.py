"""Automated merge conflict resolution."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class AdvancedConflictResolver(AdvancedTool):
    """Automated merge conflict resolution.
    
    Resolves conflicts by:
    - Analyzing conflict markers
    - Understanding both sides
    - Applying AI to suggest resolution
    - Supporting automatic resolution strategies
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "resolve_conflicts",
            "description": "AI-assisted merge conflict resolution",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "conflict_content": {"type": "string"},
                    "strategy": {"type": "string", "enum": ["suggest", "auto_theirs", "auto_ours", "manual"], "default": "suggest"}
                },
                "required": []
            }
        }
    
    async def execute(self, file_path: Optional[str] = None, conflict_content: Optional[str] = None,
                     strategy: str = "suggest", **kwargs) -> ToolResult:
        start_time = time.time()
        
        try:
            if file_path:
                from ...utils.file_utils import read_file
                content = read_file(file_path)
            else:
                content = conflict_content or ""
            
            if "<<<<<<< HEAD" not in content:
                return ToolResult(success=False, errors=["No conflicts found"])
            
            prompt = f"""Resolve this merge conflict:

{content}

Strategy: {strategy}

Provide resolution in JSON:
{{
    "conflicts_resolved": true/false,
    "resolved_content": "file content with conflicts resolved",
    "explanation": "how conflicts were resolved",
    "warnings": ["any warnings"]
}}"""
            
            response = await self.llm_client.chat([Message(role=MessageRole.USER, content=prompt)])
            
            return ToolResult(
                success=True,
                data={"resolution": response.content},
                confidence=0.8,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=response.tokens_used
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
