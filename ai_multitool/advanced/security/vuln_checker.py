"""Dependency vulnerability checking."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class AdvancedVulnChecker(AdvancedTool):
    """Dependency vulnerability checking.
    
    Checks:
    - Known CVEs in dependencies
    - Outdated packages
    - Security advisories
    - License vulnerabilities
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "check_vulnerabilities",
            "description": "Check for dependency vulnerabilities",
            "parameters": {
                "type": "object",
                "properties": {
                    "requirements_file": {"type": "string"},
                    "package_name": {"type": "string"},
                    "package_version": {"type": "string"}
                },
                "required": []
            }
        }
    
    async def execute(self, requirements_file: Optional[str] = None,
                     package_name: Optional[str] = None, package_version: Optional[str] = None, **kwargs) -> ToolResult:
        start_time = time.time()
        
        try:
            if requirements_file:
                from ...utils.file_utils import read_file
                requirements = read_file(requirements_file)
                prompt = f"""Check these dependencies for vulnerabilities:\n{requirements}"""
            elif package_name:
                prompt = f"Check {package_name} {package_version or ''} for vulnerabilities"
            else:
                return ToolResult(success=False, errors=["No package specified"])
            
            prompt += """

Provide JSON response:
{
    "vulnerabilities": [
        {
            "package": "name",
            "version": "version",
            "cve_id": "CVE-XXXX-XXXX",
            "severity": "critical|high|medium|low",
            "description": "what",
            "fix_version": "version",
            "advisory_url": "url"
        }
    ],
    "safe_packages": ["list"],
    "recommendation": "overall advice"
}"""
            
            response = await self.llm_client.chat([Message(role=MessageRole.USER, content=prompt)])
            
            return ToolResult(
                success=True,
                data={"vulnerability_report": response.content},
                confidence=0.8,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=response.tokens_used
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
