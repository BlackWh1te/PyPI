"""Backup and recovery strategy tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class BackupStrategy(AdvancedTool):
    """AI-powered backup strategy tool.
    
    Analyzes for:
    - Backup frequency
    - Retention policies
    - Storage optimization
    - Recovery testing
    - Disaster recovery
    - Encryption strategies
    - Cost optimization
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for backup strategy."""
        return {
            "name": "design_backup",
            "description": "AI-powered backup strategy design with disaster recovery planning",
            "parameters": {
                "type": "object",
                "properties": {
                    "data_type": {"type": "string", "description": "Type of data (database, files, etc.)"},
                    "data_size": {"type": "string", "description": "Data size (e.g., '100GB', '1TB')"},
                    "rpo": {"type": "string", "description": "Recovery Point Objective (e.g., '1 hour', '5 min')"},
                    "rto": {"type": "string", "description": "Recovery Time Objective (e.g., '4 hours', '1 hour')"},
                    "focus": {"type": "string", "enum": ["all", "frequency", "storage", "recovery", "cost"], "default": "all"},
                    "include_encryption": {"type": "boolean", "default": True}
                },
                "required": ["data_type"]
            }
        }
    
    async def execute(
        self,
        data_type: str,
        data_size: Optional[str] = None,
        rpo: Optional[str] = None,
        rto: Optional[str] = None,
        focus: str = "all",
        include_encryption: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Build strategy prompt
            prompt = self._build_strategy_prompt(data_type, data_size, rpo, rto, focus, include_encryption)
            
            # Optimize prompt
            prompt = self._optimize_prompt(prompt)
            
            # Check cache
            cache_key = self._get_cache_key(data_type=data_type, size=data_size, rpo=rpo, rto=rto, focus=focus)
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
                    "data_type": data_type,
                    "rpo": rpo,
                    "rto": rto
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "cost_estimate": self._estimate_cost(recommendations, data_size)
                },
                suggestions=[f"{r['category']}: {r['description']}" for r in recommendations],
                confidence=0.83,
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
    
    def _build_strategy_prompt(self, data_type: str, size: str, rpo: str, rto: str, focus: str, include_encryption: bool) -> str:
        enc_instruction = "Include encryption." if include_encryption else ""
        
        return f"""Design backup for {data_type} (size: {size or 'unknown'}, RPO: {rpo or 'not set'}, RTO: {rto or 'not set'})
Focus: {focus}
{enc_instruction}
JSON: {{"recs":[{{"category","desc","strategy","cost"}}],"summary"}}"""
    
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
    
    def _estimate_cost(self, recommendations: List[Dict[str, Any]], size: str) -> str:
        if not size:
            return "unknown"
        return "low" if "GB" in size else "medium" if "TB" in size else "high"
