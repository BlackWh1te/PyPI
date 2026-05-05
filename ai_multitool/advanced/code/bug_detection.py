"""Advanced bug detection with AI."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole
from ...parsers.code_parser import CodeParser


class AdvancedBugDetection(AdvancedTool):
    """AI-powered bug detection tool.
    
    Analyzes code for potential bugs including:
    - Null pointer exceptions
    - Race conditions
    - Memory leaks
    - Off-by-one errors
    - Type mismatches
    - Resource leaks
    - Logic errors
    - Security vulnerabilities
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code_parser = CodeParser()
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for bug detection.
        
        Returns:
            Tool definition dictionary with name, description, and parameters schema.
            The definition follows the standard tool registration format for
            integration with AI systems and CLI tools.
        """
        return {
            "name": "detect_bugs",
            "description": "AI-powered bug detection with fix suggestions",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to code file"},
                    "code": {"type": "string", "description": "Code content"},
                    "language": {"type": "string", "description": "Programming language"},
                    "severity": {"type": "string", "enum": ["all", "critical", "high", "medium", "low"], "default": "all"},
                    "include_fixes": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    
    async def execute(
        self,
        file_path: Optional[str] = None,
        code: Optional[str] = None,
        language: Optional[str] = None,
        severity: str = "all",
        include_fixes: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Get code
            if file_path:
                from ...utils.file_utils import read_file
                code_content = read_file(file_path)
                if not language:
                    structure = self.code_parser.parse_file(file_path)
                    language = structure.language
            else:
                code_content = code or ""
            
            # Build bug detection prompt
            prompt = self._build_detection_prompt(code_content, language, severity, include_fixes)
            
            # Get AI analysis
            response = await self.llm_client.chat([
                Message(role=MessageRole.USER, content=prompt)
            ])
            
            # Parse response
            bugs = self._parse_bugs(response.content)
            
            execution_time = (time.time() - start_time) * 1000
            
            return ToolResult(
                success=True,
                status=ToolStatus.SUCCESS,
                data={
                    "bugs_detected": bugs,
                    "total_bugs": len(bugs),
                    "language": language,
                    "severity_filter": severity
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "critical_bugs": len([b for b in bugs if b.get("severity") == "critical"]),
                    "high_bugs": len([b for b in bugs if b.get("severity") == "high"])
                },
                suggestions=[f"Fix {b['type']}: {b['description']}" for b in bugs],
                confidence=0.85,
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
    
    def _build_detection_prompt(self, code: str, language: str, severity: str, include_fixes: bool) -> str:
        fix_instruction = "Provide fix suggestions for each bug." if include_fixes else ""
        
        return f"""Analyze this {language or 'code'} for bugs and potential issues:

```{language or ''}
{code}
```

Focus on severity: {severity}
{fix_instruction}

Provide response in JSON format:
{{
    "bugs": [
        {{
            "type": "bug type (null_pointer, race_condition, memory_leak, etc.)",
            "severity": "critical|high|medium|low",
            "location": "line numbers or function names",
            "description": "What the bug is",
            "impact": "What could happen",
            "fix": "How to fix it (if include_fixes)",
            "code_example": "Example of fix"
        }}
    ],
    "summary": "Overall assessment",
    "confidence": 0.0-1.0
}}"""
    
    def _parse_bugs(self, response: str) -> List[Dict[str, Any]]:
        import json
        import re
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("bugs", [])
        except json.JSONDecodeError:
            pass
        
        return []
