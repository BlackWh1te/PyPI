"""Legal document analysis tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class ContractAnalyzer(AdvancedTool):
    """AI-powered legal document analysis tool.
    
    Analyzes for:
    - Contract clauses
    - Risk identification
    - Compliance checks
    - Terms negotiation
    - Liability assessment
    - Jurisdiction issues
    - Standard clauses
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for contract analysis."""
        return {
            "name": "analyze_contract",
            "description": "AI-powered legal contract analysis with risk identification",
            "parameters": {
                "type": "object",
                "properties": {
                    "contract_text": {"type": "string", "description": "Contract text"},
                    "contract_type": {"type": "string", "description": "Type of contract (NDA, employment, SaaS, etc.)"},
                    "jurisdiction": {"type": "string", "description": "Legal jurisdiction"},
                    "focus": {"type": "string", "enum": ["all", "risks", "compliance", "terms", "liability"], "default": "all"},
                    "include_suggestions": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    
    async def execute(
        self,
        contract_text: Optional[str] = None,
        contract_type: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        focus: str = "all",
        include_suggestions: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Truncate input
            if contract_text:
                contract_text = self._truncate_input(contract_text, "text")
            
            # Build contract prompt
            prompt = self._build_contract_prompt(contract_text, contract_type, jurisdiction, focus, include_suggestions)
            
            # Optimize prompt
            prompt = self._optimize_prompt(prompt)
            
            # Check cache
            cache_key = self._get_cache_key(text=contract_text, type=contract_type, jurisdiction=jurisdiction, focus=focus)
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
                    "contract_type": contract_type
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "risk_level": self._assess_risk_level(findings)
                },
                suggestions=[f"{f['category']}: {f['description']}" for f in findings],
                confidence=0.78,
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
    
    def _build_contract_prompt(self, text: str, contract_type: str, jurisdiction: str, focus: str, include_suggestions: bool) -> str:
        text_section = f"\nContract:\n{text[:3000]}" if text else ""
        sugg_instruction = "Include modification suggestions." if include_suggestions else ""
        
        return f"""Analyze {contract_type or 'contract'} (jurisdiction: {jurisdiction or 'not set'}){text_section}
Focus: {focus}
{sugg_instruction}
JSON: {{"findings":[{{"category","severity","desc","clause"}}],"risk"}}"""
    
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
    
    def _assess_risk_level(self, findings: List[Dict[str, Any]]) -> str:
        critical = len([f for f in findings if f.get("severity") == "critical"])
        if critical == 0:
            return "low"
        elif critical <= 2:
            return "medium"
        else:
            return "high"
