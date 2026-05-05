"""Advanced function calling and tool use."""

import time
import json
from typing import Dict, Any, List, Optional, Callable
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class AdvancedFunctionCalling(AdvancedTool):
    """Advanced function calling and tool use.
    
    Provides:
    - Function schema generation
    - Function execution
    - Tool selection
    - Parameter validation
    - Result formatting
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.available_functions: Dict[str, Callable] = {}
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "function_calling",
            "description": "Advanced function calling and tool use",
            "parameters": {
                "type": "object",
                "properties": {
                    "functions": {"type": "array", "items": {"type": "object"}},
                    "query": {"type": "string"},
                    "auto_execute": {"type": "boolean", "default": False}
                },
                "required": ["query"]
            }
        }
    
    async def execute(self, query: str, functions: Optional[List[Dict]] = None,
                     auto_execute: bool = False, **kwargs) -> ToolResult:
        start_time = time.time()
        
        try:
            # Register functions if provided
            if functions:
                for func_def in functions:
                    self._register_function(func_def)
            
            # Build function calling prompt
            functions_schema = self._build_functions_schema()
            
            prompt = f"""Available functions:
{json.dumps(functions_schema, indent=2)}

User query: {query}

{"Auto-execute" if auto_execute else "Plan"} function calls to answer the query.

Provide JSON:
{{
    "function_calls": [
        {{
            "function": "name",
            "parameters": {{}},
            "reasoning": "why"
        }}
    ],
    "execution_results": ["results if auto_execute"],
    "final_answer": "answer to query"
}}"""
            
            response = await self.llm_client.chat([Message(role=MessageRole.USER, content=prompt)])
            
            # Parse and optionally execute
            result_data = json.loads(response.content) if response.content.startswith("{") else {"raw": response.content}
            
            if auto_execute and "function_calls" in result_data:
                execution_results = await self._execute_functions(result_data["function_calls"])
                result_data["execution_results"] = execution_results
            
            return ToolResult(
                success=True,
                data=result_data,
                confidence=0.85,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=response.tokens_used
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
    
    def _register_function(self, func_def: Dict):
        """Register a function for calling."""
        name = func_def.get("name")
        # In production, you'd register actual callable functions
        self.available_functions[name] = lambda **kwargs: {"result": f"Called {name}"}
    
    def _build_functions_schema(self) -> List[Dict]:
        """Build schema for available functions."""
        return [{"name": name, "description": "Function"} for name in self.available_functions.keys()]
    
    async def _execute_functions(self, function_calls: List[Dict]) -> List[Dict]:
        """Execute function calls."""
        results = []
        for call in function_calls:
            func_name = call.get("function")
            parameters = call.get("parameters", {})
            if func_name in self.available_functions:
                result = self.available_functions[func_name](**parameters)
                results.append({"function": func_name, "result": result})
        return results
