"""Messaging and queue analysis tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class QueueAnalyzer(AdvancedTool):
    """AI-powered message queue analysis tool.
    
    Analyzes for:
    - Queue configuration
    - Message ordering
    - Dead letter queues
    - Retry policies
    - Throughput optimization
    - Consumer scaling
    - Backpressure handling
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for queue analysis."""
        return {
            "name": "analyze_queue",
            "description": "AI-powered message queue analysis with throughput optimization",
            "parameters": {
                "type": "object",
                "properties": {
                    "queue_type": {"type": "string", "enum": ["rabbitmq", "kafka", "sqs", "redis", "generic"], "default": "generic"},
                    "message_type": {"type": "string", "description": "Type of messages"},
                    "throughput": {"type": "string", "description": "Expected throughput (e.g., '1000 msg/s')"},
                    "focus": {"type": "string", "enum": ["all", "configuration", "retry", "scaling", "ordering"], "default": "all"},
                    "include_examples": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    
    async def execute(
        self,
        queue_type: str = "generic",
        message_type: Optional[str] = None,
        throughput: Optional[str] = None,
        focus: str = "all",
        include_examples: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Build queue analysis prompt
            prompt = self._build_queue_prompt(queue_type, message_type, throughput, focus, include_examples)
            
            # Optimize prompt
            prompt = self._optimize_prompt(prompt)
            
            # Check cache
            cache_key = self._get_cache_key(queue_type=queue_type, msg_type=message_type, throughput=throughput, focus=focus)
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
                    "queue_type": queue_type
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "throughput_score": self._assess_throughput(recommendations)
                },
                suggestions=[f"{r['category']}: {r['description']}" for r in recommendations],
                confidence=0.80,
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
    
    def _build_queue_prompt(self, queue_type: str, msg_type: str, throughput: str, focus: str, include_examples: bool) -> str:
        ex_instruction = "Include code examples." if include_examples else ""
        
        return f"""Analyze {queue_type} queue (msg: {msg_type or 'unknown'}, throughput: {throughput or 'unknown'})
Focus: {focus}
{ex_instruction}
JSON: {{"recs":[{{"category","desc","config","code"}}],"summary"}}"""
    
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
    
    def _assess_throughput(self, recommendations: List[Dict[str, Any]]) -> str:
        if not recommendations:
            return "unknown"
        return "high" if len(recommendations) > 5 else "medium" if len(recommendations) > 2 else "low"
