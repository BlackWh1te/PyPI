"""Machine learning model optimization tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class ModelOptimizer(AdvancedTool):
    """AI-powered ML model optimization tool.
    
    Analyzes ML models for:
    - Hyperparameter tuning suggestions
    - Architecture improvements
    - Training efficiency
    - Inference optimization
    - Model compression
    - Feature engineering
    - Data preprocessing
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for model optimization."""
        return {
            "name": "optimize_model",
            "description": "AI-powered ML model optimization with hyperparameter and architecture suggestions",
            "parameters": {
                "type": "object",
                "properties": {
                    "model_code": {"type": "string", "description": "Model code (PyTorch, TensorFlow, etc.)"},
                    "model_file": {"type": "string", "description": "Path to model file"},
                    "framework": {"type": "string", "enum": ["pytorch", "tensorflow", "sklearn", "xgboost", "generic"], "default": "generic"},
                    "task_type": {"type": "string", "enum": ["classification", "regression", "nlp", "cv", "reinforcement", "generic"], "default": "generic"},
                    "focus": {"type": "string", "enum": ["all", "hyperparameters", "architecture", "training", "inference"], "default": "all"},
                    "include_quantization": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    
    async def execute(
        self,
        model_code: Optional[str] = None,
        model_file: Optional[str] = None,
        framework: str = "generic",
        task_type: str = "generic",
        focus: str = "all",
        include_quantization: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Get model code
            if model_file:
                from ...utils.file_utils import read_file
                code = read_file(model_file)
            else:
                code = model_code or ""
            
            # Build optimization prompt
            prompt = self._build_optimization_prompt(code, framework, task_type, focus, include_quantization)
            
            # Get AI analysis
            response = await self.llm_client.chat([
                Message(role=MessageRole.USER, content=prompt)
            ])
            
            # Parse response
            optimizations = self._parse_optimizations(response.content)
            
            execution_time = (time.time() - start_time) * 1000
            
            return ToolResult(
                success=True,
                status=ToolStatus.SUCCESS,
                data={
                    "optimizations": optimizations,
                    "total_optimizations": len(optimizations),
                    "framework": framework,
                    "task_type": task_type
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "performance_improvements": len([o for o in optimizations if o.get("category") == "performance"]),
                    "memory_savings": self._estimate_memory_savings(optimizations)
                },
                suggestions=[f"{o['category']}: {o['description']}" for o in optimizations],
                confidence=0.81,
                execution_time_ms=execution_time,
                tokens_used=response.tokens_used
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ToolResult(
                success=False,
                status=ToolStatus.FAILED,
                errors=[str(e)],
                execution_time_ms=execution_time
            )
    
    def _build_optimization_prompt(self, code: str, framework: str, task_type: str, focus: str, include_quantization: bool) -> str:
        quantization_instruction = "Include quantization and model compression suggestions." if include_quantization else ""
        
        return f"""Optimize this {framework} ML model for {task_type} tasks:

```python
{code}
```

Focus area: {focus}
{quantization_instruction}

Provide response in JSON format:
{{
    "optimizations": [
        {{
            "category": "hyperparameters|architecture|training|inference|data",
            "severity": "critical|high|medium|low",
            "description": "What can be improved",
            "current_issue": "Current approach",
            "recommendation": "Suggested improvement",
            "code_example": "Example code",
            "expected_improvement": "Expected benefit (e.g., '20% faster training')"
        }}
    ],
    "optimized_code": "Optimized model code",
    "summary": "Overall optimization summary",
    "confidence": 0.0-1.0
}}"""
    
    def _parse_optimizations(self, response: str) -> List[Dict[str, Any]]:
        import json
        import re
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("optimizations", [])
        except json.JSONDecodeError:
            pass
        
        return []
    
    def _estimate_memory_savings(self, optimizations: List[Dict[str, Any]]) -> str:
        """Estimate potential memory savings."""
        memory_optimizations = [o for o in optimizations if "memory" in o.get("description", "").lower()]
        
        if not memory_optimizations:
            return "0%"
        
        savings = min(len(memory_optimizations) * 20, 70)  # Max 70% savings
        return f"{savings}%"
