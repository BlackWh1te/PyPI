"""Web scraping and data extraction tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class WebScraper(AdvancedTool):
    """AI-powered web scraping tool.
    
    Analyzes web pages for:
    - Data extraction strategies
    - Selector generation (CSS, XPath)
    - Anti-scraping evasion
    - Rate limiting design
    - Data cleaning
    - Storage strategies
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for web scraping."""
        return {
            "name": "scrape_web",
            "description": "AI-powered web scraping with selector generation and anti-bot strategies",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Target URL"},
                    "html_content": {"type": "string", "description": "HTML content"},
                    "data_target": {"type": "string", "description": "What data to extract (e.g., 'product prices', 'article titles')"},
                    "focus": {"type": "string", "enum": ["all", "selectors", "anti_bot", "cleaning", "storage"], "default": "all"},
                    "include_code": {"type": "boolean", "default": True}
                },
                "required": ["data_target"]
            }
        }
    
    async def execute(
        self,
        url: Optional[str] = None,
        html_content: Optional[str] = None,
        data_target: str = "",
        focus: str = "all",
        include_code: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Truncate input if too large
            if html_content:
                html_content = self._truncate_input(html_content, "text")
            
            # Build scraping prompt
            prompt = self._build_scraping_prompt(url, html_content, data_target, focus, include_code)
            
            # Optimize prompt
            prompt = self._optimize_prompt(prompt)
            
            # Check cache
            cache_key = self._get_cache_key(url=url, data_target=data_target, focus=focus)
            cached_result = await self._get_cached(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Get AI analysis
            response = await self.llm_client.chat([
                Message(role=MessageRole.USER, content=prompt)
            ])
            
            # Parse response
            strategies = self._parse_strategies(response.content)
            
            execution_time = (time.time() - start_time) * 1000
            
            result = ToolResult(
                success=True,
                status=ToolStatus.SUCCESS,
                data={
                    "strategies": strategies,
                    "total_strategies": len(strategies),
                    "data_target": data_target,
                    "url": url
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "selectors_count": len([s for s in strategies if s.get("category") == "selectors"])
                },
                suggestions=[f"{s['category']}: {s['description']}" for s in strategies],
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
    
    def _build_scraping_prompt(self, url: str, html: str, target: str, focus: str, include_code: bool) -> str:
        code_instruction = "Include Python code." if include_code else ""
        html_section = f"\nHTML:\n```\n{html[:5000]}\n```" if html else ""
        
        return f"""Scrape {target} from {url or 'web page'}:{html_section}
Focus: {focus}
{code_instruction}
JSON: {{"strategies":[{{"category","desc","selectors","code"}}],"summary"}}"""
    
    def _parse_strategies(self, response: str) -> List[Dict[str, Any]]:
        import json
        import re
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("strategies", [])
        except json.JSONDecodeError:
            pass
        
        return []
