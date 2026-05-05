"""Cryptography and security key management tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class CryptoKeyManager(AdvancedTool):
    """AI-powered cryptographic key management advisor.
    
    Provides guidance on:
    - Key generation best practices
    - Key rotation strategies
    - Encryption algorithm selection
    - Key storage security
    - Certificate management
    - Key lifecycle management
    - Compliance requirements
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for crypto key management."""
        return {
            "name": "manage_crypto_keys",
            "description": "AI-powered cryptographic key management advisor for security best practices",
            "parameters": {
                "type": "object",
                "properties": {
                    "use_case": {"type": "string", "description": "Intended use case (e.g., 'data encryption at rest', 'API authentication')"},
                    "data_type": {"type": "string", "enum": ["symmetric", "asymmetric", "hashing", "signing", "generic"], "default": "generic"},
                    "compliance": {"type": "array", "items": {"type": "string"}, "description": "Compliance requirements (e.g., ['GDPR', 'PCI-DSS'])"},
                    "focus": {"type": "string", "enum": ["all", "generation", "rotation", "storage", "algorithms"], "default": "all"},
                    "include_examples": {"type": "boolean", "default": True}
                },
                "required": ["use_case"]
            }
        }
    
    async def execute(
        self,
        use_case: str,
        data_type: str = "generic",
        compliance: Optional[List[str]] = None,
        focus: str = "all",
        include_examples: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Build advisory prompt
            prompt = self._build_advisory_prompt(use_case, data_type, compliance, focus, include_examples)
            
            # Get AI analysis
            response = await self.llm_client.chat([
                Message(role=MessageRole.USER, content=prompt)
            ])
            
            # Parse response
            recommendations = self._parse_recommendations(response.content)
            
            execution_time = (time.time() - start_time) * 1000
            
            return ToolResult(
                success=True,
                status=ToolStatus.SUCCESS,
                data={
                    "recommendations": recommendations,
                    "total_recommendations": len(recommendations),
                    "use_case": use_case,
                    "data_type": data_type,
                    "compliance": compliance or []
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "security_level": self._assess_security_level(recommendations),
                    "compliance_coverage": self._assess_compliance(recommendations, compliance)
                },
                suggestions=[f"{r['category']}: {r['description']}" for r in recommendations],
                confidence=0.87,
                execution_time_ms=execution_time,
                tokens_used=response.tokens_used
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ToolResult(
                success=False,
                status=ToolStatus.FAILED,
                errors=[str(e)],
                execution_time_ms=execution_time
            )
    
    def _build_advisory_prompt(self, use_case: str, data_type: str, compliance: List[str], focus: str, include_examples: bool) -> str:
        compliance_str = ", ".join(compliance) if compliance else "none specified"
        examples_instruction = "Include code examples for implementation." if include_examples else ""
        
        return f"""Provide cryptographic key management guidance for:

Use Case: {use_case}
Data Type: {data_type}
Compliance Requirements: {compliance_str}
Focus Area: {focus}
{examples_instruction}

Provide response in JSON format:
{{
    "recommendations": [
        {{
            "category": "generation|rotation|storage|algorithms|lifecycle",
            "severity": "critical|high|medium|low",
            "description": "Recommendation",
            "rationale": "Why this is recommended",
            "algorithm": "Suggested algorithm (e.g., 'AES-256-GCM')",
            "key_size": "Recommended key size",
            "rotation_period": "Suggested rotation frequency",
            "code_example": "Implementation example (if include_examples)",
            "compliance": ["Relevant compliance standards"]
        }}
    ],
    "summary": "Overall key management strategy",
    "confidence": 0.0-1.0
}}"""
    
    def _parse_recommendations(self, response: str) -> List[Dict[str, Any]]:
        import json
        import re
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("recommendations", [])
        except json.JSONDecodeError:
            pass
        
        return []
    
    def _assess_security_level(self, recommendations: List[Dict[str, Any]]) -> str:
        """Assess overall security level based on recommendations."""
        critical_count = len([r for r in recommendations if r.get("severity") == "critical"])
        
        if critical_count == 0:
            return "high"
        elif critical_count <= 2:
            return "medium"
        else:
            return "low"
    
    def _assess_compliance(self, recommendations: List[Dict[str, Any]], compliance: List[str]) -> str:
        """Assess compliance coverage."""
        if not compliance:
            return "not applicable"
        
        covered = sum(1 for r in recommendations if r.get("compliance"))
        if covered >= len(compliance):
            return "fully covered"
        elif covered > 0:
            return "partially covered"
        else:
            return "not covered"
