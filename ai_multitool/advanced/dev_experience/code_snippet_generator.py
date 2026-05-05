"""Code Snippet Generator - AI-powered code snippet generation."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class CodeSnippetGenerator(AdvancedTool):
    """AI-powered code snippet generation.
    
    Features:
    - Code snippet generation
    - Pattern-based code
    - Best practice examples
    - Language-specific snippets
    - Documentation integration
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "code_snippet_generator",
            "description": "Generate code snippets with AI-powered analysis",
            "category": ToolCategory.CODE_ANALYSIS,
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Description of the code snippet needed"
                    },
                    "language": {
                        "type": "string",
                        "enum": ["python", "javascript", "typescript", "java", "go", "rust", "cpp"],
                        "description": "Programming language"
                    },
                    "include_comments": {
                        "type": "boolean",
                        "description": "Include explanatory comments"
                    },
                    "include_tests": {
                        "type": "boolean",
                        "description": "Include test examples"
                    }
                },
                "required": ["description", "language"]
            }
        }
    
    async def execute(
        self,
        description: str,
        language: str,
        include_comments: bool = True,
        include_tests: bool = False
    ) -> ToolResult:
        """Execute code snippet generation.
        
        Args:
            description: Description of needed code
            language: Programming language
            include_comments: Include comments
            include_tests: Include tests
            
        Returns:
            ToolResult with generated code snippet
        """
        prompt = f"""Generate a code snippet for the following task

Language: {language}
Task Description: {description}

Please provide:
1. Complete, working code snippet
2. Explanation of the code (if comments requested)
3. Best practices followed
4. Dependencies or imports needed
5. Usage examples
"""
        
        if include_comments:
            prompt += "\n6. Inline comments explaining key parts"
        
        if include_tests:
            prompt += "\n7. Unit test examples"
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "language": language,
                "description": description,
                "include_comments": include_comments,
                "include_tests": include_tests,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Review generated code for security issues",
                "Adapt to your specific use case",
                "Add error handling as needed",
                "Test thoroughly before production use"
            ],
            confidence=0.85
        )
