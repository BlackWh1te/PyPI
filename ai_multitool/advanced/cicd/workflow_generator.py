"""CI Workflow Generator - AI-powered CI/CD workflow generation."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class CIWorkflowGenerator(AdvancedTool):
    """AI-powered CI/CD workflow generation.
    
    Features:
    - CI/CD pipeline design
    - Workflow automation
    - Multi-platform support
    - Build optimization
    - Deployment strategies
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "ci_workflow_generator",
            "description": "Generate CI/CD workflows with AI-powered analysis",
            "category": ToolCategory.DEVOPS,
            "parameters": {
                "type": "object",
                "properties": {
                    "project_type": {
                        "type": "string",
                        "enum": ["web", "mobile", "desktop", "api", "library"],
                        "description": "Type of project"
                    },
                    "platform": {
                        "type": "string",
                        "enum": ["github", "gitlab", "jenkins", "circleci", "azure", "bitbucket"],
                        "description": "CI/CD platform"
                    },
                    "language": {
                        "type": "string",
                        "enum": ["python", "javascript", "typescript", "java", "go", "rust", "cpp"],
                        "description": "Primary programming language"
                    },
                    "include_tests": {
                        "type": "boolean",
                        "description": "Include test stages in workflow"
                    },
                    "include_deploy": {
                        "type": "boolean",
                        "description": "Include deployment stages in workflow"
                    }
                },
                "required": ["project_type", "platform", "language"]
            }
        }
    
    async def execute(
        self,
        project_type: str,
        platform: str,
        language: str,
        include_tests: bool = True,
        include_deploy: bool = True
    ) -> ToolResult:
        """Execute CI workflow generation.
        
        Args:
            project_type: Type of project
            platform: CI/CD platform
            language: Programming language
            include_tests: Include test stages
            include_deploy: Include deployment stages
            
        Returns:
            ToolResult with CI workflow configuration
        """
        prompt = f"""Generate a CI/CD workflow for a {project_type} project

Platform: {platform}
Language: {language}
Include Tests: {include_tests}
Include Deploy: {include_deploy}

Please provide:
1. Complete workflow configuration file
2. Stage definitions (build, test, deploy)
3. Environment variable recommendations
4. Caching strategies
5. Artifact handling
6. Deployment strategy recommendations
7. Best practices for the chosen platform
"""
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "project_type": project_type,
                "platform": platform,
                "language": language,
                "include_tests": include_tests,
                "include_deploy": include_deploy,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Use matrix builds for multi-platform testing",
                "Implement branch protection rules",
                "Cache dependencies to speed up builds",
                "Use secrets management for sensitive data"
            ],
            confidence=0.85
        )
