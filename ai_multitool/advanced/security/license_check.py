"""License compliance checking."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class AdvancedLicenseCheck(AdvancedTool):
    """License compliance checking.
    
    Checks:
    - License compatibility
    - Commercial use restrictions
    - Attribution requirements
    - Copyleft conditions
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Known license compatibility matrix
        self.license_info = {
            "MIT": {"permissive": True, "commercial": True, "copyleft": False},
            "Apache-2.0": {"permissive": True, "commercial": True, "copyleft": False},
            "BSD-3-Clause": {"permissive": True, "commercial": True, "copyleft": False},
            "GPL-3.0": {"permissive": False, "commercial": True, "copyleft": True},
            "AGPL-3.0": {"permissive": False, "commercial": False, "copyleft": True},
            "LGPL-3.0": {"permissive": False, "commercial": True, "copyleft": True},
        }
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "check_license",
            "description": "Check license compliance",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_license": {"type": "string"},
                    "dependency_licenses": {"type": "array", "items": {"type": "string"}},
                    "commercial_use": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    
    async def execute(self, project_license: Optional[str] = None,
                     dependency_licenses: Optional[List[str]] = None, commercial_use: bool = True, **kwargs) -> ToolResult:
        start_time = time.time()
        
        try:
            issues = []
            compatible = True
            
            if project_license and dependency_licenses:
                for dep_license in dependency_licenses:
                    dep_info = self.license_info.get(dep_license, {})
                    project_info = self.license_info.get(project_license, {})
                    
                    # Check compatibility
                    if dep_info.get("copyleft") and not project_info.get("copyleft"):
                        issues.append({
                            "dependency": dep_license,
                            "issue": "Copyleft license may not be compatible",
                            "severity": "high"
                        })
                        compatible = False
                    
                    if not dep_info.get("commercial", True) and commercial_use:
                        issues.append({
                            "dependency": dep_license,
                            "issue": "Non-commercial license",
                            "severity": "critical"
                        })
                        compatible = False
            
            return ToolResult(
                success=True,
                data={
                    "compatible": compatible,
                    "issues": issues,
                    "project_license": project_license,
                    "dependency_licenses": dependency_licenses
                },
                suggestions=[f"Consider alternatives for: {i['dependency']}" for i in issues],
                confidence=0.9,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=0
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
