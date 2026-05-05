"""README and documentation generation."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class AdvancedReadmeGen(AdvancedTool):
    """README and documentation generation.
    
    Generates:
    - Project README
    - CONTRIBUTING guide
    - CHANGELOG
    - Architecture docs
    """
    
    
        """Get the tool definition for readme gen.

Returns:
    Tool definition dictionary with name, description, and parameters schema.
    The definition follows the standard tool registration format for
    integration with AI systems and CLI tools.
"""
        
            "name": "generate_readme",
            "description": "README and documentation generation",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_info": {"type": "object"},
                    "doc_type": {"type": "string", "enum": ["readme", "contributing", "changelog", "architecture"], "default": "readme"}
                },
                "required": ["doc_type"]
            }
        }
    
    async def execute(self, doc_type: str = "readme", project_info: Optional[Dict] = None,
                     **kwargs) -> ToolResult:
        start_time = time.time()
        
        try:
            prompt = f"Generate {doc_type} documentation"
            
            if project_info:
                prompt += f"\n\nProject Info:\n{project_info}"
            
            prompt += """

Provide JSON:
{
    "document_content": "full documentation",
    "sections": [{"title": "section", "content": "content"}],
    "suggestions": ["improvements"]
}"""
            
            response = await self.llm_client.chat([Message(role=MessageRole.USER, content=prompt)])
            
            return ToolResult(
                success=True,
                data={"generated_document": response.content},
                confidence=0.85,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=response.tokens_used
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
