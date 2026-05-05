"""Image Optimizer - AI-powered container image optimization."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class ImageOptimizer(AdvancedTool):
    """AI-powered container image optimization.
    
    Features:
    - Image size reduction
    - Layer optimization
    - Build cache optimization
    - Multi-stage build strategies
    - Dependency pruning
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "image_optimizer",
            "description": "Optimize container images for size and performance with AI-powered analysis",
            "category": ToolCategory.CLOUD,
            "parameters": {
                "type": "object",
                "properties": {
                    "dockerfile": {
                        "type": "string",
                        "description": "Dockerfile to optimize"
                    },
                    "current_size": {
                        "type": "string",
                        "description": "Current image size (e.g., '500MB', '2GB')"
                    },
                    "target_size": {
                        "type": "string",
                        "description": "Target image size (optional)"
                    },
                    "optimization_level": {
                        "type": "string",
                        "enum": ["conservative", "moderate", "aggressive"],
                        "description": "Level of optimization"
                    }
                },
                "required": ["dockerfile"]
            }
        }
    
    async def execute(
        self,
        dockerfile: str,
        current_size: Optional[str] = None,
        target_size: Optional[str] = None,
        optimization_level: str = "moderate"
    ) -> ToolResult:
        """Execute image optimization.
        
        Args:
            dockerfile: Dockerfile to optimize
            current_size: Current image size
            target_size: Target size
            optimization_level: Optimization level
            
        Returns:
            ToolResult with optimization recommendations
        """
        prompt = f"""Optimize the following Dockerfile for smaller image size

Dockerfile:
```
{dockerfile}
```
"""
        
        if current_size:
            prompt += f"\nCurrent Image Size: {current_size}"
        
        if target_size:
            prompt += f"\nTarget Image Size: {target_size}"
        
        prompt += f"""
Optimization Level: {optimization_level}

Please provide:
1. Optimized Dockerfile
2. Size reduction strategies applied
3. Expected size reduction
4. Layer consolidation opportunities
5. Multi-stage build recommendations
6. Dependency pruning suggestions
7. Build cache optimization tips
8. Trade-offs and considerations
"""
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "current_size": current_size,
                "target_size": target_size,
                "optimization_level": optimization_level,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Use multi-stage builds to separate build and runtime dependencies",
                "Combine RUN commands to reduce layers",
                "Use .dockerignore to exclude unnecessary files",
                "Choose minimal base images (alpine, distroless)"
            ],
            confidence=0.85
        )
