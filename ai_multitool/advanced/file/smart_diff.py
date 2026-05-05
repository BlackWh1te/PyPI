"""Smart diff generation."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class AdvancedSmartDiff(AdvancedTool):
    """Smart diff generation.
    
    Provides:
    - Semantic diff
    - Change summarization
    - Impact analysis
    - Review suggestions
    """
    
    
        """Get the tool definition for smart diff.

Returns:
    Tool definition dictionary with name, description, and parameters schema.
    The definition follows the standard tool registration format for
    integration with AI systems and CLI tools.
"""
        
            "name": "smart_diff",
            "description": "Smart diff generation",
            "parameters": {
                "type": "object",
                "properties": {
                    "old_content": {"type": "string"},
                    "new_content": {"type": "string"},
                    "file_path": {"type": "string"}
                },
                "required": ["old_content", "new_content"]
            }
        }
    
    async def execute(self, old_content: str, new_content: str, file_path: Optional[str] = None,
                     **kwargs) -> ToolResult:
        start_time = time.time()
        
        try:
            prompt = f"""Generate smart diff analysis:

Old content:
{old_content[:2000]}

New content:
{new_content[:2000]}

File: {file_path or 'unknown'}

Provide JSON:
{{
    "semantic_changes": ["what changed semantically"],
    "impact_analysis": "impact of changes",
    "risk_assessment": "risk level",
    "review_suggestions": ["what to review"],
    "confidence": 0.0-1.0
}}"""
            
            response = await self.llm_client.chat([Message(role=MessageRole.USER, content=prompt)])
            
            return ToolResult(
                success=True,
                data={"diff_analysis": response.content},
                confidence=0.85,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=response.tokens_used
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
