"""Dependency Updater - AI-powered dependency update management."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class DependencyUpdater(AdvancedTool):
    """AI-powered dependency update management.
    
    Features:
    - Safe update planning
    - Breaking change detection
    - Version compatibility analysis
    - Update recommendations
    - Rollback strategies
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "dependency_updater",
            "description": "Plan and manage dependency updates with AI-powered analysis",
            "category": ToolCategory.CODE_ANALYSIS,
            "parameters": {
                "type": "object",
                "properties": {
                    "manifest_file": {
                        "type": "string",
                        "description": "Dependency manifest file"
                    },
                    "package_manager": {
                        "type": "string",
                        "enum": ["npm", "pip", "yarn", "cargo", "go", "maven", "gradle"],
                        "description": "Package manager used"
                    },
                    "update_type": {
                        "type": "string",
                        "enum": ["major", "minor", "patch", "all"],
                        "description": "Type of updates to consider"
                    },
                    "include_breaking_changes": {
                        "type": "boolean",
                        "description": "Include major version updates with breaking changes"
                    }
                },
                "required": ["manifest_file", "package_manager"]
            }
        }
    
    async def execute(
        self,
        manifest_file: str,
        package_manager: str,
        update_type: str = "minor",
        include_breaking_changes: bool = False
    ) -> ToolResult:
        """Execute dependency update planning.
        
        Args:
            manifest_file: Dependency manifest file
            package_manager: Package manager used
            update_type: Type of updates
            include_breaking_changes: Include breaking changes
            
        Returns:
            ToolResult with update recommendations
        """
        prompt = f"""Plan dependency updates for {manifest_file}

Package Manager: {package_manager}
Update Type: {update_type}
Include Breaking Changes: {include_breaking_changes}

Please provide:
1. Available updates for each dependency
2. Breaking changes (if any)
3. Compatibility analysis
4. Recommended update order
5. Potential risks and mitigations
6. Rollback strategies
7. Update commands for the package manager
"""
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "manifest_file": manifest_file,
                "package_manager": package_manager,
                "update_type": update_type,
                "include_breaking_changes": include_breaking_changes,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Test updates in a staging environment first",
                "Use semantic versioning to understand impact",
                "Keep a changelog of dependency updates",
                "Automate dependency updates with Dependabot or Renovate"
            ],
            confidence=0.85
        )
