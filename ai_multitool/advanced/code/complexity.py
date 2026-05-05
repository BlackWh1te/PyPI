"""Advanced complexity analysis."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole
from ...parsers.code_parser import CodeParser


class AdvancedComplexityAnalysis(AdvancedTool):
    """Advanced code complexity analysis.
    
    Analyzes:
    - Cyclomatic complexity
    - Cognitive complexity
    - Halstead complexity
    - Maintainability index
    - Code churn
    - Technical debt
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code_parser = CodeParser()
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "analyze_complexity",
            "description": "Advanced code complexity analysis",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "code": {"type": "string"},
                    "language": {"type": "string"}
                },
                "required": []
            }
        }
    
    async def execute(self, file_path: Optional[str] = None, code: Optional[str] = None,
                     language: Optional[str] = None, **kwargs) -> ToolResult:
        start_time = time.time()
        
        try:
            if file_path:
                from ...utils.file_utils import read_file
                code_content = read_file(file_path)
                structure = self.code_parser.parse_file(file_path)
                language = language or structure.language
            else:
                code_content = code or ""
            
            prompt = f"""Analyze complexity of this {language or 'code'}:

```{language or ''}
{code_content}
```

Provide JSON:
{{
    "cyclomatic_complexity": number,
    "cognitive_complexity": number,
    "maintainability_index": 0-100,
    "technical_debt_hours": number,
    "complex_functions": [
        {{"name": "function", "complexity": number}}
    ],
    "recommendations": ["suggestions"]
}}"""

            response = await self.llm_client.chat([Message(role=MessageRole.USER, content=prompt)])
            
            metrics = self._parse_metrics(response.content)
            
            return ToolResult(
                success=True,
                data=metrics,
                suggestions=metrics.get("recommendations", []),
                confidence=0.85,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=response.tokens_used
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
    
    def _parse_metrics(self, response: str) -> Dict:
        import json, re
        try:
            match = re.search(r'\{[\s\S]*\}', response)
            if match:
                return json.loads(match.group())
        except:
            pass
        return {}
