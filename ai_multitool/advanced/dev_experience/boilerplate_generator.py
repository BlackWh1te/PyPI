"""Boilerplate Generator - AI-powered boilerplate code generation."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class BoilerplateGenerator(AdvancedTool):
    """AI-powered boilerplate code generation.
    
    Features:
    - Project scaffolding
    - Boilerplate code generation
    - Best practice templates
    - Configuration files
    - Documentation stubs
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "boilerplate_generator",
            "description": "Generate boilerplate code with AI-powered analysis",
            "category": ToolCategory.CODE_ANALYSIS,
            "parameters": {
                "type": "object",
                "properties": {
                    "project_type": {
                        "type": "string",
                        "enum": ["web_api", "web_app", "cli", "library", "microservice"],
                        "description": "Type of project"
                    },
                    "language": {
                        "type": "string",
                        "enum": ["python", "javascript", "typescript", "java", "go", "rust", "cpp"],
                        "description": "Programming language"
                    },
                    "framework": {
                        "type": "string",
                        "description": "Framework to use (optional)"
                    },
                    "include_tests": {
                        "type": "boolean",
                        "description": "Include test setup"
                    },
                    "include_ci": {
                        "type": "boolean",
                        "description": "Include CI/CD configuration"
                    }
                },
                "required": ["project_type", "language"]
            }
        }
    
    async def execute(
        self,
        project_type: str,
        language: str,
        framework: Optional[str] = None,
        include_tests: bool = True,
        include_ci: bool = True
    ) -> ToolResult:
        """Execute boilerplate generation.
        
        Args:
            project_type: Type of project
            language: Programming language
            framework: Framework to use
            include_tests: Include test setup
            include_ci: Include CI/CD config
            
        Returns:
            ToolResult with boilerplate code
        """
        prompt = f"""Generate boilerplate code for a new project

Project Type: {project_type}
Language: {language}
Framework: {framework or 'standard'}
Include Tests: {include_tests}
Include CI/CD: {include_ci}

Please provide:
1. Project structure
2. Main application code
3. Configuration files
4. Package management files
5. Test setup (if requested)
6. CI/CD configuration (if requested)
7. Documentation stubs
8. Setup instructions
"""
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "project_type": project_type,
                "language": language,
                "framework": framework,
                "include_tests": include_tests,
                "include_ci": include_ci,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Customize boilerplate to your needs",
                "Review and update documentation",
                "Add project-specific configurations",
                "Set up version control and initial commit"
            ],
            confidence=0.85
        )
