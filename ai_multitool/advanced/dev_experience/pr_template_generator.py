"""PR Template Generator - AI-powered pull request template generation."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class PRTemplateGenerator(AdvancedTool):
    """AI-powered pull request template generation.
    
    Features:
    - PR template design
    - Custom sections
    - Checklist generation
    - Best practices inclusion
    - Platform-specific templates
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "pr_template_generator",
            "description": "Generate pull request templates with AI-powered analysis",
            "category": ToolCategory.COLLABORATION,
            "parameters": {
                "type": "object",
                "properties": {
                    "project_type": {
                        "type": "string",
                        "enum": ["web", "mobile", "api", "library", "infrastructure"],
                        "description": "Type of project"
                    },
                    "platform": {
                        "type": "string",
                        "enum": ["github", "gitlab", "bitbucket", "azure"],
                        "description": "Git platform"
                    },
                    "include_checklist": {
                        "type": "boolean",
                        "description": "Include PR checklist"
                    },
                    "include_sections": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Custom sections to include"
                    }
                },
                "required": ["project_type", "platform"]
            }
        }
    
    async def execute(
        self,
        project_type: str,
        platform: str,
        include_checklist: bool = True,
        include_sections: Optional[list] = None
    ) -> ToolResult:
        """Execute PR template generation.
        
        Args:
            project_type: Type of project
            platform: Git platform
            include_checklist: Include checklist
            include_sections: Custom sections
            
        Returns:
            ToolResult with PR template
        """
        if include_sections is None:
            include_sections = []
        
        prompt = f"""Generate a pull request template

Project Type: {project_type}
Platform: {platform}
Include Checklist: {include_checklist}
Custom Sections: {', '.join(include_sections) if include_sections else 'none'}

Please provide:
1. Complete PR template in markdown format
2. Standard sections (description, changes, testing)
3. Custom sections (if specified)
4. PR checklist (if requested)
5. Platform-specific formatting
6. Best practices for PR descriptions
7. Example filled template
8. Instructions for use
"""
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "project_type": project_type,
                "platform": platform,
                "include_checklist": include_checklist,
                "include_sections": include_sections,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Customize template to team needs",
                "Include links to contributing guidelines",
                "Add sections for performance impact",
                "Regularly review and update template"
            ],
            confidence=0.85
        )
