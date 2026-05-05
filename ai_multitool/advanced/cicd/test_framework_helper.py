"""Test Framework Helper - AI-powered test framework setup and guidance."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class TestFrameworkHelper(AdvancedTool):
    """AI-powered test framework setup and guidance.
    
    Features:
    - Test framework selection
    - Test structure design
    - Best practices guidance
    - Mock and stub generation
    - Test configuration
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "test_framework_helper",
            "description": "Get help with test framework setup and best practices",
            "category": ToolCategory.TESTING,
            "parameters": {
                "type": "object",
                "properties": {
                    "language": {
                        "type": "string",
                        "enum": ["python", "javascript", "typescript", "java", "go", "rust", "cpp"],
                        "description": "Programming language"
                    },
                    "test_type": {
                        "type": "string",
                        "enum": ["unit", "integration", "e2e", "performance", "all"],
                        "description": "Type of testing needed"
                    },
                    "framework_preference": {
                        "type": "string",
                        "description": "Preferred test framework (optional)"
                    },
                    "include_examples": {
                        "type": "boolean",
                        "description": "Include example test code"
                    }
                },
                "required": ["language", "test_type"]
            }
        }
    
    async def execute(
        self,
        language: str,
        test_type: str,
        framework_preference: Optional[str] = None,
        include_examples: bool = False
    ) -> ToolResult:
        """Execute test framework guidance.
        
        Args:
            language: Programming language
            test_type: Type of testing
            framework_preference: Preferred framework
            include_examples: Include example code
            
        Returns:
            ToolResult with test framework recommendations
        """
        prompt = f"""Provide test framework guidance for {language}

Test Type: {test_type}
Framework Preference: {framework_preference or 'auto-select'}

Please provide:
1. Recommended test frameworks
2. Project structure for tests
3. Best practices for {test_type} testing
4. Configuration examples
5. Mock and stub strategies
6. Test organization patterns
7. CI/CD integration tips
"""
        
        if include_examples:
            prompt += "\n8. Example test code with common patterns"
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "language": language,
                "test_type": test_type,
                "framework_preference": framework_preference,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Follow the Arrange-Act-Assert pattern",
                "Keep tests independent and isolated",
                "Use descriptive test names",
                "Mock external dependencies for reliable tests"
            ],
            confidence=0.85
        )
