"""Re-ranking for better retrieval accuracy."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class AdvancedReranking(AdvancedTool):
    """Re-ranking for better retrieval accuracy.
    
    Uses AI to:
    - Re-rank search results
    - Improve relevance
    - Filter low-quality results
    - Add diversity to results
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "rerank_results",
            "description": "Re-rank search results for better accuracy",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "results": {"type": "array", "items": {"type": "object"}},
                    "top_k": {"type": "number", "default": 5},
                    "diversity": {"type": "boolean", "default": True}
                },
                "required": ["query", "results"]
            }
        }
    
    async def execute(self, query: str, results: List[Dict], top_k: int = 5,
                     diversity: bool = True, **kwargs) -> ToolResult:
        start_time = time.time()
        
        try:
            # Build prompt for re-ranking
            results_text = "\n".join([
                f"{i+1}. {r.get('content', str(r))[:200]}..."
                for i, r in enumerate(results)
            ])
            
            prompt = f"""Re-rank these search results for the query: "{query}"

Results:
{results_text}

Requirements:
- Re-rank by relevance to query
- {"Ensure diversity" if diversity else "Focus on top matches"}
- Return top {top_k} results

Provide JSON:
{{
    "reranked_results": [
        {{"original_rank": 1, "new_rank": 1, "relevance_score": 0.95, "reason": "why"}}
    ],
    "filtered_out": [original_ranks],
    "confidence": 0.0-1.0
}}"""
            
            response = await self.llm_client.chat([Message(role=MessageRole.USER, content=prompt)])
            
            return ToolResult(
                success=True,
                data={"reranking": response.content, "original_count": len(results)},
                confidence=0.85,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=response.tokens_used
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
