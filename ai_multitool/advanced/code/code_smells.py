"""Advanced code smell detection."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole
from ...parsers.code_parser import CodeParser


class AdvancedCodeSmellDetection(AdvancedTool):
    """Detection of code smells and anti-patterns.
    
    Detects:
    - Long methods/functions
    - Large classes
    - Duplicate code
    - God objects
    - Feature envy
    - Inappropriate intimacy
    - Long parameter lists
    - Divergent change
    - Shotgun surgery
    - Parallel inheritance hierarchies
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code_parser = CodeParser()
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for code smell detection.
        
        Returns:
            Tool definition dictionary with name, description, and parameters schema.
            The definition follows the standard tool registration format for
            integration with AI systems and CLI tools.
        """
        return {
            "name": "detect_code_smells",
            "description": "Detect code smells and anti-patterns",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "code": {"type": "string"},
                    "language": {"type": "string"},
                    "threshold": {"type": "number", "default": 0.7}
                },
                "required": []
            }
        }
    
    async def execute(self, file_path: Optional[str] = None, code: Optional[str] = None, 
                     language: Optional[str] = None, threshold: float = 0.7, **kwargs) -> ToolResult:
        start_time = time.time()
        
        try:
            if file_path:
                from ...utils.file_utils import read_file
                code_content = read_file(file_path)
                structure = self.code_parser.parse_file(file_path)
                language = language or structure.language
            else:
                code_content = code or ""
                structure = None
            
            prompt = f"""Analyze this {language or 'code'} for code smells and anti-patterns:

```{language or ''}
{code_content}
```

Provide JSON response:
{{
    "smells": [
        {{
            "type": "smell type",
            "severity": "critical|high|medium|low",
            "location": "where",
            "description": "what",
            "suggestion": "how to fix"
        }}
    ],
    "overall_score": 0.0-1.0
}}"""

            response = await self.llm_client.chat([Message(role=MessageRole.USER, content=prompt)])
            
            smells = self._parse_smells(response.content)
            
            return ToolResult(
                success=True,
                data={"smells": smells, "threshold": threshold},
                metrics={"smell_count": len(smells)},
                suggestions=[s["suggestion"] for s in smells],
                confidence=0.8,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=response.tokens_used
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
    
    def _parse_smells(self, response: str) -> List[Dict]:
        import json, re
        try:
            match = re.search(r'\{[\s\S]*\}', response)
            if match:
                return json.loads(match.group()).get("smells", [])
        except (json.JSONDecodeError, ValueError, KeyError):
            # If parsing fails, return empty list
            pass
        return []
