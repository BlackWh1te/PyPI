"""Storage optimization tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class StorageOptimizer(AdvancedTool):
    """AI-powered storage optimization tool.
    
    Analyzes for:
    - Storage tier selection
    - Compression strategies
    - Lifecycle policies
    - Access patterns
    - Cost optimization
    - Performance tuning
    - Data archiving
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for storage optimization."""
        return {
            "name": "optimize_storage",
            "description": "AI-powered storage optimization with tier selection and lifecycle policies",
            "parameters": {
                "type": "object",
                "properties": {
                    "data_type": {"type": "string", "description": "Type of data (images, logs, backups, etc.)"},
                    "access_pattern": {"type": "string", "enum": ["hot", "warm", "cold", "mixed"], "default": "mixed"},
                    "provider": {"type": "string", "enum": ["s3", "gcs", "azure", "generic"], "default": "generic"},
                    "focus": {"type": "string", "enum": ["all", "cost", "performance", "lifecycle", "compression"], "default": "all"},
                    "include_policy": {"type": "boolean", "default": True}
                },
                "required": ["data_type"]
            }
        }
    
    async def execute(
        self,
        data_type: str,
        access_pattern: str = "mixed",
        provider: str = "generic",
        focus: str = "all",
        include_policy: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Build storage prompt
            prompt = self._build_storage_prompt(data_type, access_pattern, provider, focus, include_policy)
            
            # Optimize prompt
            prompt = self._optimize_prompt(prompt)
            
            # Check cache
            cache_key = self._get_cache_key(data_type=data_type, pattern=access_pattern, provider=provider, focus=focus)
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
                    "data_type": data_type
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "cost_savings": self._estimate_savings(recommendations)
                },
                suggestions=[f"{r['category']}: {r['description']}" for r in recommendations],
                confidence=0.82,
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
    
    def _build_storage_prompt(self, data_type: str, pattern: str, provider: str, focus: str, include_policy: bool) -> str:
        policy_instruction = "Include lifecycle policy." if include_policy else ""
        
        return f"""Optimize {data_type} storage (pattern: {pattern}, provider: {provider})
Focus: {focus}
{policy_instruction}
JSON: {{"recs":[{{"category","desc","tier","policy"}}],"summary"}}"""
    
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
    
    def _estimate_savings(self, recommendations: List[Dict[str, Any]]) -> str:
        cost_recs = [r for r in recommendations if r.get("category") == "cost"]
        if not cost_recs:
            return "unknown"
        return "high" if len(cost_recs) > 3 else "medium" if len(cost_recs) > 1 else "low"
