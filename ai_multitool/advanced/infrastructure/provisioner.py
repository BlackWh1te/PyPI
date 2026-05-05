"""Infrastructure provisioning tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class InfrastructureProvisioner(AdvancedTool):
    """AI-powered infrastructure provisioning tool.
    
    Analyzes for:
    - Resource sizing
    - Cost optimization
    - High availability
    - Scalability
    - Security groups
    - Network design
    - Multi-region strategy
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for infrastructure provisioning."""
        return {
            "name": "provision_infrastructure",
            "description": "AI-powered infrastructure provisioning with cost and HA optimization",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_type": {"type": "string", "description": "Type of service (web, database, cache, etc.)"},
                    "expected_load": {"type": "string", "description": "Expected load (e.g., '1000 RPS', '1M users')"},
                    "provider": {"type": "string", "enum": ["aws", "gcp", "azure", "generic"], "default": "generic"},
                    "focus": {"type": "string", "enum": ["all", "cost", "ha", "scalability", "security"], "default": "all"},
                    "include_terraform": {"type": "boolean", "default": True}
                },
                "required": ["service_type"]
            }
        }
    
    async def execute(
        self,
        service_type: str,
        expected_load: Optional[str] = None,
        provider: str = "generic",
        focus: str = "all",
        include_terraform: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Build provisioning prompt
            prompt = self._build_provisioning_prompt(service_type, expected_load, provider, focus, include_terraform)
            
            # Optimize prompt
            prompt = self._optimize_prompt(prompt)
            
            # Check cache
            cache_key = self._get_cache_key(service=service_type, load=expected_load, provider=provider, focus=focus)
            cached_result = await self._get_cached(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Get AI analysis
            response = await self.llm_client.chat([
                Message(role=MessageRole.USER, content=prompt)
            ])
            
            # Parse response
            config = self._parse_config(response.content)
            
            execution_time = (time.time() - start_time) * 1000
            
            result = ToolResult(
                success=True,
                status=ToolStatus.SUCCESS,
                data={
                    "infrastructure_config": config,
                    "service_type": service_type,
                    "provider": provider
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "estimated_cost": config.get("estimated_cost", "unknown")
                },
                suggestions=[f"{c['component']}: {c['description']}" for c in config.get("components", [])],
                confidence=0.81,
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
    
    def _build_provisioning_prompt(self, service: str, load: str, provider: str, focus: str, include_terraform: bool) -> str:
        tf_instruction = "Include Terraform." if include_terraform else ""
        
        return f"""Provision {service} (load: {load or 'unknown'}, provider: {provider})
Focus: {focus}
{tf_instruction}
JSON: {{"components":[{{"component","size","ha","cost"}}],"summary"}}"""
    
    def _parse_config(self, response: str) -> Dict[str, Any]:
        import json
        import re
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return data
        except json.JSONDecodeError:
            pass
        
        return {"components": [], "estimated_cost": "unknown"}
