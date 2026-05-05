"""Automatic documentation generation."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class AdvancedAutoDoc(AdvancedTool):
    """Automatic documentation generation.
    
    Generates:
    - Function docstrings
    - Class documentation
    - Module documentation
    - Inline comments
    """
    
    
        """Get the tool definition for auto doc.

Returns:
    Tool definition dictionary with name, description, and parameters schema.
    The definition follows the standard tool registration format for
    integration with AI systems and CLI tools.
"""
        
            "name": "generate_docs",
            "description": "Automatic documentation generation",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "doc_style": {"type": "string", "enum": ["google", "numpy", "sphinx", "plain"], "default": "google"},
                    "include_examples": {"type": "boolean", "default": True}
                },
                "required": ["code"]
            }
        }
    
    async def execute(self, code: str, doc_style: str = "google",
                     include_examples: bool = True, **kwargs) -> ToolResult:
        start_time = time.time()
        
        try:
            prompt = f"""Generate documentation for this code in {doc_style} style:

Code:
{code}

Requirements:
- {"Include usage examples" if include_examples else "No examples"}
- Clear parameter descriptions
- Return value documentation
- Raises documentation
- Type hints

Provide JSON:
{{
    "documented_code": "code with docs added",
    "docstrings": {"function": "docstring"},
    "examples": ["usage examples"],
    "missing_docs": ["parts needing docs"]
}}"""
            
            response = await self.llm_client.chat([Message(role=MessageRole.USER, content=prompt)])
            
            return ToolResult(
                success=True,
                data={"documentation": response.content},
                confidence=0.85,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=response.tokens_used
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
