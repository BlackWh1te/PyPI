"""Code Formatter - AI-powered code formatting and style enforcement."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class CodeFormatter(AdvancedTool):
    """AI-powered code formatting and style enforcement.
    
    Features:
    - Code formatting
    - Style normalization
    - Consistency enforcement
    - Automatic formatting
    - Format configuration
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "code_formatter",
            "description": "Format code and enforce consistent style with AI-powered analysis",
            "category": ToolCategory.CODE_ANALYSIS,
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to format"
                    },
                    "language": {
                        "type": "string",
                        "enum": ["python", "javascript", "typescript", "java", "go", "rust", "cpp"],
                        "description": "Programming language"
                    },
                    "indent_style": {
                        "type": "string",
                        "enum": ["spaces", "tabs"],
                        "description": "Indentation style"
                    },
                    "indent_size": {
                        "type": "integer",
                        "description": "Indentation size"
                    },
                    "line_width": {
                        "type": "integer",
                        "description": "Maximum line width"
                    }
                },
                "required": ["code", "language"]
            }
        }
    
    async def execute(
        self,
        code: str,
        language: str,
        indent_style: str = "spaces",
        indent_size: int = 4,
        line_width: int = 88
    ) -> ToolResult:
        """Execute code formatting.
        
        Args:
            code: Code to format
            language: Programming language
            indent_style: Indentation style (spaces or tabs)
            indent_size: Indentation size
            line_width: Maximum line width
            
        Returns:
            ToolResult with formatted code and recommendations
        """
        prompt = f"""Format the following {language} code:

Formatting Options:
- Indent Style: {indent_style}
- Indent Size: {indent_size}
- Line Width: {line_width}

Code:
```
{code}
```

Please provide:
1. Formatted code
2. Changes made
3. Formatting rules applied
4. Suggestions for maintaining consistency
"""
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "language": language,
                "indent_style": indent_style,
                "indent_size": indent_size,
                "line_width": line_width,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Use automated formatters like black, prettier, or gofmt",
                "Configure editor format-on-save",
                "Include formatting in pre-commit hooks"
            ],
            confidence=0.85
        )
