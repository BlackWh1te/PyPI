"""Email analysis and optimization tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class EmailAnalyzer(AdvancedTool):
    """AI-powered email analysis tool.
    
    Analyzes for:
    - Content optimization
    - Deliverability
    - Spam prevention
    - Personalization
    - A/B testing
    - Template design
    - Engagement tracking
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for email analysis."""
        return {
            "name": "analyze_email",
            "description": "AI-powered email analysis with deliverability and engagement optimization",
            "parameters": {
                "type": "object",
                "properties": {
                    "email_content": {"type": "string", "description": "Email content"},
                    "email_type": {"type": "string", "enum": ["marketing", "transactional", "notification", "newsletter"], "default": "marketing"},
                    "focus": {"type": "string", "enum": ["all", "deliverability", "content", "personalization", "design"], "default": "all"},
                    "include_subject": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    
    async def execute(
        self,
        email_content: Optional[str] = None,
        email_type: str = "marketing",
        focus: str = "all",
        include_subject: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Truncate input
            if email_content:
                email_content = self._truncate_input(email_content, "text")
            
            # Build email prompt
            prompt = self._build_email_prompt(email_content, email_type, focus, include_subject)
            
            # Optimize prompt
            prompt = self._optimize_prompt(prompt)
            
            # Check cache
            cache_key = self._get_cache_key(content=email_content, type=email_type, focus=focus)
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
                    "email_type": email_type
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "spam_score": self._assess_spam_score(recommendations)
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
    
    def _build_email_prompt(self, content: str, email_type: str, focus: str, include_subject: bool) -> str:
        content_section = f"\nContent:\n{content[:2000]}" if content else ""
        subject_instruction = "Include subject line suggestions." if include_subject else ""
        
        return f"""Analyze {email_type} email (focus: {focus}):{content_section}
{subject_instruction}
JSON: {{"recs":[{{"category","desc","fix"}}],"spam_score"}}"""
    
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
    
    def _assess_spam_score(self, recommendations: List[Dict[str, Any]]) -> str:
        spam_recs = [r for r in recommendations if r.get("category") == "deliverability"]
        if not spam_recs:
            return "unknown"
        return "low" if len(spam_recs) > 3 else "medium" if len(spam_recs) > 1 else "high"
