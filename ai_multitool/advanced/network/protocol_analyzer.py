"""Network protocol and API optimization tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class NetworkProtocolAnalyzer(AdvancedTool):
    """AI-powered network protocol and API optimization tool.
    
    Analyzes network communications for:
    - Protocol selection
    - Data serialization optimization
    - Compression strategies
    - Caching policies
    - Rate limiting design
    - Security considerations
    - Latency optimization
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for network protocol analysis."""
        return {
            "name": "analyze_network_protocol",
            "description": "AI-powered network protocol and API optimization for performance and security",
            "parameters": {
                "type": "object",
                "properties": {
                    "api_spec": {"type": "string", "description": "API specification or protocol documentation"},
                    "protocol": {"type": "string", "enum": ["http", "grpc", "websocket", "mqtt", "generic"], "default": "generic"},
                    "data_format": {"type": "string", "enum": ["json", "protobuf", "xml", "msgpack", "generic"], "default": "json"},
                    "focus": {"type": "string", "enum": ["all", "performance", "security", "bandwidth", "latency"], "default": "all"},
                    "include_compression": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    
    async def execute(
        self,
        api_spec: Optional[str] = None,
        protocol: str = "generic",
        data_format: str = "json",
        focus: str = "all",
        include_compression: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Build analysis prompt
            prompt = self._build_analysis_prompt(api_spec, protocol, data_format, focus, include_compression)
            
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
                    "protocol": protocol,
                    "data_format": data_format
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "bandwidth_savings": self._estimate_bandwidth_savings(recommendations),
                    "latency_improvement": self._estimate_latency_improvement(recommendations)
                },
                suggestions=[f"{r['category']}: {r['description']}" for r in recommendations],
                confidence=0.81,
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
    
    def _build_analysis_prompt(self, api_spec: str, protocol: str, data_format: str, focus: str, include_compression: bool) -> str:
        spec_str = f"\nAPI Spec:\n```\n{api_spec}\n```" if api_spec else ""
        compression_instruction = "Include compression strategy recommendations." if include_compression else ""
        
        return f"""Analyze this network protocol setup:

Protocol: {protocol}
Data Format: {data_format}
{spec_str}

Focus area: {focus}
{compression_instruction}

Provide response in JSON format:
{{
    "recommendations": [
        {{
            "category": "protocol|serialization|compression|caching|security|latency",
            "severity": "critical|high|medium|low",
            "description": "What can be improved",
            "current_issue": "Current approach",
            "recommendation": "Suggested improvement",
            "code_example": "Example of optimized implementation",
            "expected_benefit": "Expected benefit (e.g., '40% bandwidth reduction')"
        }}
    ],
    "summary": "Overall protocol analysis summary",
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
    
    def _estimate_bandwidth_savings(self, recommendations: List[Dict[str, Any]]) -> str:
        """Estimate potential bandwidth savings."""
        bandwidth_optimizations = [r for r in recommendations if r.get("category") in ["compression", "serialization"]]
        
        if not bandwidth_optimizations:
            return "0%"
        
        savings = min(len(bandwidth_optimizations) * 20, 60)  # Max 60% savings
        return f"{savings}%"
    
    def _estimate_latency_improvement(self, recommendations: List[Dict[str, Any]]) -> str:
        """Estimate potential latency improvement."""
        latency_optimizations = [r for r in recommendations if r.get("category") == "latency"]
        
        if not latency_optimizations:
            return "0%"
        
        improvement = min(len(latency_optimizations) * 15, 50)  # Max 50% improvement
        return f"{improvement}%"
