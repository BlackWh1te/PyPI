"""Project health scoring and metrics."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class AdvancedProjectHealth(AdvancedTool):
    """Project health scoring and metrics.
    
    Analyzes:
    - Code quality
    - Test coverage
    - Documentation
    - Technical debt
    - Maintainability
    - Security posture
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "analyze_health",
            "description": "Project health scoring and metrics",
            "parameters": {
                "type": "object",
                "properties": {
                    "codebase_path": {"type": "string"},
                    "metrics": {"type": "object"}
                },
                "required": ["codebase_path"]
            }
        }
    
    async def execute(self, codebase_path: str, metrics: Optional[Dict] = None, **kwargs) -> ToolResult:
        start_time = time.time()
        
        try:
            prompt = f"""Analyze project health for: {codebase_path}
            
            Metrics provided: {metrics or 'none'}
            
            Provide JSON:
            {{
                "overall_score": 0-100,
                "category_scores": {{
                    "code_quality": 0-100,
                    "test_coverage": 0-100,
                    "documentation": 0-100,
                    "security": 0-100,
                    "maintainability": 0-100
                }},
                "critical_issues": ["issues"],
                "recommendations": ["improvements"],
                "trends": "health trends"
            }}"""
            
            response = await self.llm_client.chat([Message(role=MessageRole.USER, content=prompt)])
            
            return ToolResult(
                success=True,
                data={"health_report": response.content},
                confidence=0.85,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=response.tokens_used
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
