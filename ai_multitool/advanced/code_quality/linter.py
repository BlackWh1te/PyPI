"""Code Linter - AI-powered code linting and style checking."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class CodeLinter(AdvancedTool):
    """AI-powered code linting and style checking.
    
    Features:
    - Code style analysis
    - Best practices checking
    - Code smell detection
    - Style guide compliance
    - Auto-fix suggestions
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "code_linter",
            "description": "Lint code and detect style issues with AI-powered analysis",
            "category": ToolCategory.CODE_ANALYSIS,
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to lint"
                    },
                    "language": {
                        "type": "string",
                        "enum": ["python", "javascript", "typescript", "java", "go", "rust", "cpp"],
                        "description": "Programming language"
                    },
                    "style_guide": {
                        "type": "string",
                        "enum": ["pep8", "google", "airbnb", "standard", "custom"],
                        "description": "Style guide to follow"
                    },
                    "include_fixes": {
                        "type": "boolean",
                        "description": "Include auto-fix suggestions"
                    }
                },
                "required": ["code", "language"]
            }
        }
    
    async def execute(
        self,
        code: str,
        language: str,
        style_guide: str = "pep8",
        include_fixes: bool = False
    ) -> ToolResult:
        """Execute code linting.
        
        Args:
            code: Code to lint
            language: Programming language
            style_guide: Style guide to follow
            include_fixes: Include auto-fix suggestions
            
        Returns:
            ToolResult with linting results and recommendations
        """
        prompt = f"""Lint the following {language} code:

Style Guide: {style_guide}

Code:
```
{code}
```

Please provide:
1. Style violations found
2. Code quality issues
3. Best practices violations
4. Severity levels for each issue
5. Line numbers where issues occur
"""
        
        if include_fixes:
            prompt += "\n6. Suggested fixes for each issue"
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "language": language,
                "style_guide": style_guide,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Configure automated linting in CI/CD",
                "Use pre-commit hooks for local linting",
                "Adopt consistent style across the codebase"
            ],
            confidence=0.85
        )
