"""Docker and container optimization tools."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class DockerOptimizer(AdvancedTool):
    """AI-powered Docker optimization tool.
    
    Analyzes Docker configurations for:
    - Image size optimization
    - Multi-stage builds
    - Layer caching strategies
    - Security best practices
    - Resource limits
    - Health checks
    - Network configuration
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for Docker optimization."""
        return {
            "name": "optimize_docker",
            "description": "AI-powered Dockerfile and docker-compose optimization",
            "parameters": {
                "type": "object",
                "properties": {
                    "dockerfile_path": {"type": "string", "description": "Path to Dockerfile"},
                    "dockerfile_content": {"type": "string", "description": "Dockerfile content"},
                    "compose_file": {"type": "string", "description": "Path to docker-compose.yml"},
                    "focus": {"type": "string", "enum": ["all", "size", "security", "performance", "best_practices"], "default": "all"},
                    "include_multistage": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    
    async def execute(
        self,
        dockerfile_path: Optional[str] = None,
        dockerfile_content: Optional[str] = None,
        compose_file: Optional[str] = None,
        focus: str = "all",
        include_multistage: bool = True,
        **kwargs
    ) -> ToolResult:
        start_time = time.time()
        
        try:
            # Get Dockerfile content
            if dockerfile_path:
                from ...utils.file_utils import read_file
                dockerfile = read_file(dockerfile_path)
            else:
                dockerfile = dockerfile_content or ""
            
            # Get docker-compose if provided
            compose_content = ""
            if compose_file:
                from ...utils.file_utils import read_file
                compose_content = read_file(compose_file)
            
            # Build optimization prompt
            prompt = self._build_optimization_prompt(dockerfile, compose_content, focus, include_multistage)
            
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
                    "focus_area": focus,
                    "estimated_size_reduction": self._estimate_size_reduction(optimizations)
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "critical_issues": len([o for o in optimizations if o.get("severity") == "critical"]),
                    "security_improvements": len([o for o in optimizations if o.get("category") == "security"])
                },
                suggestions=[f"{o['category']}: {o['description']}" for o in optimizations],
                confidence=0.83,
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
    
    def _build_optimization_prompt(self, dockerfile: str, compose: str, focus: str, include_multistage: bool) -> str:
        multistage_instruction = "Suggest multi-stage build improvements." if include_multistage else ""
        compose_section = f"\nDocker Compose:\n```yaml\n{compose}\n```" if compose else ""
        
        return f"""Optimize this Docker configuration:

Dockerfile:
```dockerfile
{dockerfile}
```
{compose_section}

Focus area: {focus}
{multistage_instruction}

Provide response in JSON format:
{{
    "optimizations": [
        {{
            "category": "size|security|performance|best_practices",
            "severity": "critical|high|medium|low",
            "description": "What can be improved",
            "current_issue": "Current problematic pattern",
            "recommendation": "How to fix it",
            "code_example": "Example of optimized code",
            "estimated_impact": "Expected benefit (e.g., '30% smaller image')"
        }}
    ],
    "optimized_dockerfile": "Fully optimized Dockerfile",
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
    
    def _estimate_size_reduction(self, optimizations: List[Dict[str, Any]]) -> str:
        """Estimate potential image size reduction."""
        size_optimizations = [o for o in optimizations if o.get("category") == "size"]
        
        if not size_optimizations:
            return "0%"
        
        # Rough estimation based on optimization count
        reduction = min(len(size_optimizations) * 15, 60)  # Max 60% reduction
        return f"{reduction}%"
