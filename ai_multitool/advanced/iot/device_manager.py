"""IoT device management tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class IoTDeviceManager(AdvancedTool):
    """AI-powered IoT device management tool.
    
    Analyzes for:
    - Device provisioning
    - Firmware updates
    - Security policies
    - Data collection
    - Edge computing
    - Power management
    - Telemetry
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for IoT device management."""
        return {
            "name": "manage_iot",
            "description": "AI-powered IoT device management with security and power optimization",
            "parameters": {
                "type": "object",
                "properties": {
                    "device_type": {"type": "string", "description": "Type of IoT device"},
                    "deployment_scale": {"type": "string", "description": "Deployment scale (e.g., '1000 devices')"},
                    "connectivity": {"type": "string", "enum": ["wifi", "cellular", "lora", "mqtt", "generic"], "default": "generic"},
                    "focus": {"type": "string", "enum": ["all", "security", "power", "connectivity", "telemetry"], "default": "all"},
                    "include_architecture": {"type": "boolean", "default": True}
                },
                "required": ["device_type"]
            }
        }
    
    async def execute(
        self,
        device_type: str,
        deployment_scale: Optional[str] = None,
        connectivity: str = "generic",
        focus: str = "all",
        include_architecture: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Build IoT prompt
            prompt = self._build_iot_prompt(device_type, deployment_scale, connectivity, focus, include_architecture)
            
            # Optimize prompt
            prompt = self._optimize_prompt(prompt)
            
            # Check cache
            cache_key = self._get_cache_key(device=device_type, scale=deployment_scale, conn=connectivity, focus=focus)
            cached_result = await self._get_cached(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Get AI analysis
            response = await self.llm_client.chat([
                Message(role=MessageRole.USER, content=prompt)
            ])
            
            # Parse response
            recommendations = self._parse_recommendations(response.content)
            
            execution_time = (time.time() - start_time) * 1000
            
            result = ToolResult(
                success=True,
                status=ToolStatus.SUCCESS,
                data={
                    "recommendations": recommendations,
                    "total_recommendations": len(recommendations),
                    "device_type": device_type
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "security_score": self._assess_security(recommendations)
                },
                suggestions=[f"{r['category']}: {r['description']}" for r in recommendations],
                confidence=0.79,
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
    
    def _build_iot_prompt(self, device: str, scale: str, connectivity: str, focus: str, include_architecture: bool) -> str:
        arch_instruction = "Include architecture diagram." if include_architecture else ""
        
        return f"""Manage {device} IoT (scale: {scale or 'unknown'}, connectivity: {connectivity})
Focus: {focus}
{arch_instruction}
JSON: {{"recs":[{{"category","desc","config"}}],"summary"}}"""
    
    def _parse_recommendations(self, response: str) -> List[Dict[str, Any]]:
        import json
        import re
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("recs", [])
        except json.JSONDecodeError:
            pass
        
        return []
    
    def _assess_security(self, recommendations: List[Dict[str, Any]]) -> str:
        security_recs = [r for r in recommendations if r.get("category") == "security"]
        if not security_recs:
            return "unknown"
        return "high" if len(security_recs) > 3 else "medium" if len(security_recs) > 1 else "low"
