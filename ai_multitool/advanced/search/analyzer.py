"""Search and indexing tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class SearchAnalyzer(AdvancedTool):
    """AI-powered search and indexing tool.
    
    Analyzes for:
    - Search schema design
    - Indexing strategy
    - Query optimization
    - Relevance tuning
    - Faceted search
    - Synonyms handling
    - Spell correction
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for search analysis."""
        return {
            "name": "analyze_search",
            "description": "AI-powered search and indexing analysis with query optimization",
            "parameters": {
                "type": "object",
                "properties": {
                    "data_description": {"type": "string", "description": "Description of data to search"},
                    "search_engine": {"type": "string", "enum": ["elasticsearch", "solr", "algolia", "generic"], "default": "generic"},
                    "query_types": {"type": "array", "items": {"type": "string"}, "description": "Types of queries needed"},
                    "focus": {"type": "string", "enum": ["all", "schema", "indexing", "query", "relevance"], "default": "all"},
                    "include_mapping": {"type": "boolean", "default": True}
                },
                "required": ["data_description"]
            }
        }
    
    async def execute(
        self,
        data_description: str,
        search_engine: str = "generic",
        query_types: Optional[List[str]] = None,
        focus: str = "all",
        include_mapping: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Build search prompt
            prompt = self._build_search_prompt(data_description, search_engine, query_types, focus, include_mapping)
            
            # Optimize prompt
            prompt = self._optimize_prompt(prompt)
            
            # Check cache
            cache_key = self._get_cache_key(desc=data_description, engine=search_engine, queries=query_types, focus=focus)
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
                    "search_engine": search_engine
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "relevance_score": self._assess_relevance(recommendations)
                },
                suggestions=[f"{r['category']}: {r['description']}" for r in recommendations],
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
    
    def _build_search_prompt(self, desc: str, engine: str, queries: List[str], focus: str, include_mapping: bool) -> str:
        queries_str = ", ".join(queries) if queries else "not specified"
        mapping_instruction = "Include index mapping." if include_mapping else ""
        
        return f"""Analyze search for {desc} (engine: {engine}, queries: {queries_str})
Focus: {focus}
{mapping_instruction}
JSON: {{"recs":[{{"category","desc","config","mapping"}}],"summary"}}"""
    
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
    
    def _assess_relevance(self, recommendations: List[Dict[str, Any]]) -> str:
        relevance_recs = [r for r in recommendations if r.get("category") == "relevance"]
        if not relevance_recs:
            return "unknown"
        return "high" if len(relevance_recs) > 3 else "medium" if len(relevance_recs) > 1 else "low"
