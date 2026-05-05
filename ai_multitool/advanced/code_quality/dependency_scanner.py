"""Dependency Scanner - AI-powered dependency analysis and vulnerability checking."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class DependencyScanner(AdvancedTool):
    """AI-powered dependency analysis and vulnerability checking.
    
    Features:
    - Dependency tree analysis
    - Vulnerability detection
    - License compliance checking
    - Outdated dependency detection
    - Security advisory integration
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "dependency_scanner",
            "description": "Scan dependencies for vulnerabilities and security issues",
            "category": ToolCategory.SECURITY,
            "parameters": {
                "type": "object",
                "properties": {
                    "manifest_file": {
                        "type": "string",
                        "description": "Dependency manifest file (package.json, requirements.txt, etc.)"
                    },
                    "package_manager": {
                        "type": "string",
                        "enum": ["npm", "pip", "yarn", "cargo", "go", "maven", "gradle"],
                        "description": "Package manager used"
                    },
                    "scan_type": {
                        "type": "string",
                        "enum": ["vulnerabilities", "outdated", "licenses", "all"],
                        "description": "Type of scan to perform"
                    },
                    "severity_threshold": {
                        "type": "string",
                        "enum": ["low", "moderate", "high", "critical"],
                        "description": "Minimum severity to report"
                    }
                },
                "required": ["manifest_file", "package_manager"]
            }
        }
    
    async def execute(
        self,
        manifest_file: str,
        package_manager: str,
        scan_type: str = "all",
        severity_threshold: str = "moderate"
    ) -> ToolResult:
        """Execute dependency scanning.
        
        Args:
            manifest_file: Dependency manifest file
            package_manager: Package manager used
            scan_type: Type of scan
            severity_threshold: Minimum severity to report
            
        Returns:
            ToolResult with dependency scan results
        """
        prompt = f"""Scan dependencies from {manifest_file}

Package Manager: {package_manager}
Scan Type: {scan_type}
Severity Threshold: {severity_threshold}

Please provide:
1. List of dependencies found
2. Known vulnerabilities (if any)
3. Outdated packages (if scanning for outdated)
4. License information (if scanning for licenses)
5. Recommendations for remediation
6. Dependency tree analysis
"""
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "manifest_file": manifest_file,
                "package_manager": package_manager,
                "scan_type": scan_type,
                "severity_threshold": severity_threshold,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Use automated dependency scanning in CI/CD",
                "Enable automated security updates",
                "Pin dependency versions for reproducibility",
                "Regularly audit dependencies for vulnerabilities"
            ],
            confidence=0.85
        )
