"""Code Review Bot - AI-powered automated code review."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class CodeReviewBot(AdvancedTool):
    """AI-powered automated code review.
    
    Features:
    - Automated code review
    - Best practices checking
    - Security review
    - Performance suggestions
    - Style consistency
    - Documentation review
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "code_review_bot",
            "description": "Perform automated code review with AI-powered analysis",
            "category": ToolCategory.COLLABORATION,
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to review"
                    },
                    "language": {
                        "type": "string",
                        "enum": ["python", "javascript", "typescript", "java", "go", "rust", "cpp"],
                        "description": "Programming language"
                    },
                    "review_focus": {
                        "type": "string",
                        "enum": ["security", "performance", "style", "documentation", "all"],
                        "description": "Focus of the review"
                    },
                    "severity_level": {
                        "type": "string",
                        "enum": ["critical", "high", "medium", "low", "all"],
                        "description": "Minimum severity to report"
                    }
                },
                "required": ["code", "language"]
            }
        }
    
    async def execute(
        self,
        code: str,
        language: str,
        review_focus: str = "all",
        severity_level: str = "medium"
    ) -> ToolResult:
        """Execute code review.
        
        Args:
            code: Code to review
            language: Programming language
            review_focus: Review focus
            severity_level: Minimum severity
            
        Returns:
            ToolResult with code review
        """
        prompt = f"""Perform code review on the following {language} code

Review Focus: {review_focus}
Severity Level: {severity_level} and above

Code:
```
{code}
```

Please provide:
1. Code quality issues found
2. Security vulnerabilities (if reviewing security)
3. Performance improvements (if reviewing performance)
4. Style inconsistencies (if reviewing style)
5. Documentation gaps (if reviewing documentation)
6. Best practices violations
7. Line-by-line feedback
8. Specific suggestions for improvement
9. Positive aspects of the code
"""
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "language": language,
                "review_focus": review_focus,
                "severity_level": severity_level,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Use automated code review in CI/CD",
                "Provide constructive feedback",
                "Focus on actionable suggestions",
                "Balance criticism with positive feedback"
            ],
            confidence=0.85
        )
