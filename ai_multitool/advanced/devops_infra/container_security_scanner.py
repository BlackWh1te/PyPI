"""Container Security Scanner - AI-powered container security analysis."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class ContainerSecurityScanner(AdvancedTool):
    """AI-powered container security analysis.
    
    Features:
    - Vulnerability scanning
    - Configuration security
    - Runtime security
    - Compliance checking
    - Security hardening
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "container_security_scanner",
            "description": "Scan containers for security vulnerabilities with AI-powered analysis",
            "category": ToolCategory.SECURITY,
            "parameters": {
                "type": "object",
                "properties": {
                    "image_name": {
                        "type": "string",
                        "description": "Container image name or ID"
                    },
                    "dockerfile": {
                        "type": "string",
                        "description": "Dockerfile used to build the image"
                    },
                    "scan_depth": {
                        "type": "string",
                        "enum": ["base", "dependencies", "full"],
                        "description": "Depth of security scan"
                    },
                    "compliance_standard": {
                        "type": "string",
                        "enum": ["cis", "nist", "pci", "none"],
                        "description": "Compliance standard to check"
                    }
                },
                "required": ["image_name"]
            }
        }
    
    async def execute(
        self,
        image_name: str,
        dockerfile: Optional[str] = None,
        scan_depth: str = "full",
        compliance_standard: str = "none"
    ) -> ToolResult:
        """Execute container security scanning.
        
        Args:
            image_name: Container image name
            dockerfile: Dockerfile content
            scan_depth: Scan depth
            compliance_standard: Compliance standard
            
        Returns:
            ToolResult with security scan results
        """
        prompt = f"""Perform security analysis on container image: {image_name}

Scan Depth: {scan_depth}
Compliance Standard: {compliance_standard}
"""
        
        if dockerfile:
            prompt += f"\nDockerfile:\n```\n{dockerfile}\n```"
        
        prompt += """

Please provide:
1. Known vulnerabilities in base image and dependencies
2. Security misconfigurations
3. Privilege and permission issues
4. Secrets exposure risks
5. Compliance violations (if standard specified)
6. Security hardening recommendations
7. Best practices for secure containers
"""
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "image_name": image_name,
                "scan_depth": scan_depth,
                "compliance_standard": compliance_standard,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Use minimal base images (alpine, distroless)",
                "Scan images regularly in CI/CD pipeline",
                "Run containers as non-root users",
                "Keep images updated with security patches"
            ],
            confidence=0.85
        )
