"""Compliance auditing tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class ComplianceAuditor(AdvancedTool):
    """AI-powered compliance auditing tool.
    
    Analyzes for:
    - GDPR compliance
    - HIPAA compliance
    - SOC 2 compliance
    - PCI-DSS compliance
    - Data retention
    - Privacy policies
    - Audit trails
    - Risk assessment
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for compliance auditing."""
        return {
            "name": "audit_compliance",
            "description": "AI-powered compliance auditing for GDPR, HIPAA, SOC 2, PCI-DSS",
            "parameters": {
                "type": "object",
                "properties": {
                    "system_description": {"type": "string", "description": "System description"},
                    "standards": {"type": "array", "items": {"type": "string"}, "description": "Compliance standards (GDPR, HIPAA, SOC2, PCI-DSS)"},
                    "data_type": {"type": "string", "description": "Type of data processed"},
                    "focus": {"type": "string", "enum": ["all", "data_privacy", "security", "audit_trail", "risk"], "default": "all"},
                    "include_checklist": {"type": "boolean", "default": True}
                },
                "required": ["system_description"]
            }
        }
    
    async def execute(
        self,
        system_description: str,
        standards: Optional[List[str]] = None,
        data_type: Optional[str] = None,
        focus: str = "all",
        include_checklist: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Build compliance prompt
            prompt = self._build_compliance_prompt(system_description, standards, data_type, focus, include_checklist)
            
            # Optimize prompt
            prompt = self._optimize_prompt(prompt)
            
            # Check cache
            cache_key = self._get_cache_key(desc=system_description, standards=standards, data_type=data_type, focus=focus)
            cached_result = await self._get_cached(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Get AI analysis
            response = await self.llm_client.chat([
                Message(role=MessageRole.USER, content=prompt)
            ])
            
            # Parse response
            findings = self._parse_findings(response.content)
            
            execution_time = (time.time() - start_time) * 1000
            
            result = ToolResult(
                success=True,
                status=ToolStatus.SUCCESS,
                data={
                    "findings": findings,
                    "total_findings": len(findings),
                    "standards": standards or [],
                    "data_type": data_type
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "compliance_score": self._calculate_compliance_score(findings)
                },
                suggestions=[f"{f['category']}: {f['description']}" for f in findings],
                confidence=0.84,
                execution_time_ms=execution_time,
                tokens_used=response.tokens_used
            )
            
            # Cache result
            await self._set_cached(cache_key, result)
            
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ToolResult(
                success=False,
                status=ToolStatus.FAILED,
                errors=[str(e)],
                execution_time_ms=execution_time
            )
    
    def _build_compliance_prompt(self, desc: str, standards: List[str], data_type: str, focus: str, include_checklist: bool) -> str:
        standards_str = ", ".join(standards) if standards else "not specified"
        checklist_instruction = "Include checklist." if include_checklist else ""
        
        return f"""Audit compliance for {desc} (standards: {standards_str}, data: {data_type or 'not set'})
Focus: {focus}
{checklist_instruction}
JSON: {{"findings":[{{"standard","category","severity","desc","remediation"}}],"score"}}"""
    
    def _parse_findings(self, response: str) -> List[Dict[str, Any]]:
        import json
        import re
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("findings", [])
        except json.JSONDecodeError:
            pass
        
        return []
    
    def _calculate_compliance_score(self, findings: List[Dict[str, Any]]) -> str:
        critical = len([f for f in findings if f.get("severity") == "critical"])
        if critical == 0:
            return "compliant"
        elif critical <= 2:
            return "mostly_compliant"
        elif critical <= 5:
            return "partially_compliant"
        else:
            return "non_compliant"
