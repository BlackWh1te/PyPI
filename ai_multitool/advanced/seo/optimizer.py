"""SEO optimization tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class SEOOptimizer(AdvancedTool):
    """AI-powered SEO optimization tool.
    
    Analyzes content for:
    - Keyword optimization
    - Meta tags
    - Content structure
    - Readability
    - Internal linking
    - Technical SEO
    - Performance impact
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for SEO optimization."""
        return {
            "name": "optimize_seo",
            "description": "AI-powered SEO optimization with keyword and technical analysis",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Web page content"},
                    "url": {"type": "string", "description": "Page URL"},
                    "keywords": {"type": "array", "items": {"type": "string"}, "description": "Target keywords"},
                    "focus": {"type": "string", "enum": ["all", "keywords", "technical", "content", "performance"], "default": "all"},
                    "include_suggestions": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    
    async def execute(
        self,
        content: Optional[str] = None,
        url: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        focus: str = "all",
        include_suggestions: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Truncate input
            if content:
                content = self._truncate_input(content, "text")
            
            # Build SEO prompt
            prompt = self._build_seo_prompt(content, url, keywords, focus, include_suggestions)
            
            # Optimize prompt
            prompt = self._optimize_prompt(prompt)
            
            # Check cache
            cache_key = self._get_cache_key(content=content, url=url, keywords=keywords, focus=focus)
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
                    "url": url,
                    "focus_area": focus
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "seo_score": self._calculate_seo_score(recommendations)
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
    
    def _build_seo_prompt(self, content: str, url: str, keywords: List[str], focus: str, include_suggestions: bool) -> str:
        kw_str = ", ".join(keywords) if keywords else "not specified"
        content_section = f"\nContent:\n{content[:3000]}" if content else ""
        sugg_instruction = "Include fix suggestions." if include_suggestions else ""
        
        return f"""Optimize SEO for {url or 'page'} (keywords: {kw_str}):{content_section}
Focus: {focus}
{sugg_instruction}
JSON: {{"recs":[{{"category","desc","priority","fix"}}],"score"}}"""
    
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
    
    def _calculate_seo_score(self, recommendations: List[Dict[str, Any]]) -> str:
        critical = len([r for r in recommendations if r.get("priority") == "critical"])
        if critical == 0:
            return "excellent"
        elif critical <= 2:
            return "good"
        elif critical <= 5:
            return "fair"
        else:
            return "poor"
