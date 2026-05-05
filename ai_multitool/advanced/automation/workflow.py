"""Automation and workflow tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class WorkflowDesigner(AdvancedTool):
    """AI-powered workflow automation tool.
    
    Analyzes for:
    - Workflow design
    - Automation opportunities
    - Task dependencies
    - Error handling
    - Retry strategies
    - Notification triggers
    - Integration points
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for workflow design."""
        return {
            "name": "design_workflow",
            "description": "AI-powered workflow automation design with dependency mapping",
            "parameters": {
                "type": "object",
                "properties": {
                    "process_description": {"type": "string", "description": "Process to automate"},
                    "steps": {"type": "array", "items": {"type": "string"}, "description": "Process steps"},
                    "tools": {"type": "array", "items": {"type": "string"}, "description": "Available tools"},
                    "focus": {"type": "string", "enum": ["all", "dependencies", "error_handling", "triggers", "integration"], "default": "all"},
                    "include_diagram": {"type": "boolean", "default": True}
                },
                "required": ["process_description"]
            }
        }
    
    async def execute(
        self,
        process_description: str,
        steps: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
        focus: str = "all",
        include_diagram: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Build workflow prompt
            prompt = self._build_workflow_prompt(process_description, steps, tools, focus, include_diagram)
            
            # Optimize prompt
            prompt = self._optimize_prompt(prompt)
            
            # Check cache
            cache_key = self._get_cache_key(desc=process_description, steps=steps, tools=tools, focus=focus)
            cached_result = await self._get_cached(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Get AI analysis
            response = await self.llm_client.chat([
                Message(role=MessageRole.USER, content=prompt)
            ])
            
            # Parse response
            design = self._parse_design(response.content)
            
            execution_time = (time.time() - start_time) * 1000
            
            result = ToolResult(
                success=True,
                status=ToolStatus.SUCCESS,
                data={
                    "workflow_design": design,
                    "total_steps": len(design.get("steps", [])),
                    "process": process_description
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "automation_potential": self._assess_automation_potential(design)
                },
                suggestions=[f"{s['task']}: {s['description']}" for s in design.get("steps", [])],
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
    
    def _build_workflow_prompt(self, desc: str, steps: List[str], tools: List[str], focus: str, include_diagram: bool) -> str:
        steps_str = ", ".join(steps) if steps else "not specified"
        tools_str = ", ".join(tools) if tools else "not specified"
        diagram_instruction = "Include Mermaid diagram." if include_diagram else ""
        
        return f"""Design workflow for {desc} (steps: {steps_str}, tools: {tools_str})
Focus: {focus}
{diagram_instruction}
JSON: {{"steps":[{{"task","depends_on","tool","error_handling"}}],"diagram"}}"""
    
    def _parse_design(self, response: str) -> Dict[str, Any]:
        import json
        import re
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return data
        except json.JSONDecodeError:
            pass
        
        return {"steps": [], "diagram": ""}
    
    def _assess_automation_potential(self, design: Dict[str, Any]) -> str:
        steps = len(design.get("steps", []))
        if steps > 10:
            return "high"
        elif steps > 5:
            return "medium"
        else:
            return "low"
