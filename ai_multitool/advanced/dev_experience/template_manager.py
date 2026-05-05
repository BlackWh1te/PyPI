"""Template Manager - AI-powered code template management."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class TemplateManager(AdvancedTool):
    """AI-powered code template management.
    
    Features:
    - Template design
    - Template customization
    - Variable substitution
    - Template validation
    - Best practice templates
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "template_manager",
            "description": "Manage code templates with AI-powered analysis",
            "category": ToolCategory.CODE_ANALYSIS,
            "parameters": {
                "type": "object",
                "properties": {
                    "template_description": {
                        "type": "string",
                        "description": "Description of the template needed"
                    },
                    "template_type": {
                        "type": "string",
                        "enum": ["file", "class", "function", "config", "documentation"],
                        "description": "Type of template"
                    },
                    "language": {
                        "type": "string",
                        "enum": ["python", "javascript", "typescript", "java", "go", "rust", "cpp"],
                        "description": "Programming language"
                    },
                    "include_variables": {
                        "type": "boolean",
                        "description": "Include variable placeholders"
                    }
                },
                "required": ["template_description", "template_type", "language"]
            }
        }
    
    async def execute(
        self,
        template_description: str,
        template_type: str,
        language: str,
        include_variables: bool = True
    ) -> ToolResult:
        """Execute template management.
        
        Args:
            template_description: Template description
            template_type: Type of template
            language: Programming language
            include_variables: Include variable placeholders
            
        Returns:
            ToolResult with template
        """
        prompt = f"""Create a code template

Template Description: {template_description}
Template Type: {template_type}
Language: {language}
Include Variables: {include_variables}

Please provide:
1. Template code with structure
2. Variable placeholders (if requested)
3. Variable documentation
4. Usage instructions
5. Customization guidelines
6. Best practices for this template type
7. Example usage
8. Validation checks
"""
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "template_description": template_description,
                "template_type": template_type,
                "language": language,
                "include_variables": include_variables,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Store templates in a dedicated directory",
                "Version control your templates",
                "Document template variables clearly",
                "Regularly update templates with best practices"
            ],
            confidence=0.85
        )
