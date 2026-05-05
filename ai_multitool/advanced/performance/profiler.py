"""Performance profiling and optimization tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class PerformanceProfiler(AdvancedTool):
    """AI-powered performance profiling tool.
    
    Analyzes code for performance issues including:
    - Algorithmic complexity problems
    - Inefficient data structures
    - Unnecessary computations
    - I/O bottlenecks
    - Memory access patterns
    - Concurrency issues
    - Database query optimization
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for performance profiling."""
        return {
            "name": "profile_performance",
            "description": "AI-powered performance profiling with optimization suggestions",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to code file"},
                    "code": {"type": "string", "description": "Code content"},
                    "language": {"type": "string", "description": "Programming language"},
                    "focus": {"type": "string", "enum": ["all", "cpu", "memory", "io", "algorithm"], "default": "all"},
                    "include_optimizations": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    
    async def execute(
        self,
        file_path: Optional[str] = None,
        code: Optional[str] = None,
        language: Optional[str] = None,
        focus: str = "all",
        include_optimizations: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Get code
            if file_path:
                from ...utils.file_utils import read_file
                code_content = read_file(file_path)
            else:
                code_content = code or ""
            
            # Truncate input if too large
            code_content = self._truncate_input(code_content, content_type="code")
            
            # Build profiling prompt
            prompt = self._build_profiling_prompt(code_content, language, focus, include_optimizations)
            
            # Optimize prompt to reduce tokens
            prompt = self._optimize_prompt(prompt)
            
            # Check cache first
            cache_key = self._get_cache_key(code=code_content, language=language, focus=focus)
            cached_result = await self._get_cached(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Get AI analysis
            response = await self.llm_client.chat([
                Message(role=MessageRole.USER, content=prompt)
            ])
            
            # Parse response
            issues = self._parse_performance_issues(response.content)
            
            execution_time = (time.time() - start_time) * 1000
            
            result = ToolResult(
                success=True,
                status=ToolStatus.SUCCESS,
                data={
                    "performance_issues": issues,
                    "total_issues": len(issues),
                    "language": language,
                    "focus_area": focus
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "critical_issues": len([i for i in issues if i.get("severity") == "critical"]),
                    "potential_speedup": self._estimate_speedup(issues)
                },
                suggestions=[f"Optimize {i['type']}: {i['description']}" for i in issues],
                confidence=0.80,
                execution_time_ms=execution_time,
                tokens_used=response.tokens_used
            )
            
            # Cache the result
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
    
    def _build_profiling_prompt(self, code: str, language: str, focus: str, include_optimizations: bool) -> str:
        opt_instruction = "Include fixes." if include_optimizations else ""
        
        return f"""Analyze {language or 'code'} perf (focus: {focus}):
```{language or ''}
{code}
```
{opt_instruction}
JSON:
{{"issues":[{{"type","severity","location","desc","impact","fix","code"}}],"summary","confidence"}}"""
    
    def _parse_performance_issues(self, response: str) -> List[Dict[str, Any]]:
        import json
        import re
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("issues", [])
        except json.JSONDecodeError:
            pass
        
        return []
    
    def _estimate_speedup(self, issues: List[Dict[str, Any]]) -> float:
        """Estimate potential speedup from optimizations."""
        speedup = 1.0
        for issue in issues:
            severity = issue.get("severity", "low")
            if severity == "critical":
                speedup *= 1.5
            elif severity == "high":
                speedup *= 1.3
            elif severity == "medium":
                speedup *= 1.1
        return round(speedup, 2)
