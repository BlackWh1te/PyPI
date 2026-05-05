"""Dockerfile Analyzer - AI-powered Dockerfile analysis and optimization."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class DockerfileAnalyzer(AdvancedTool):
    """AI-powered Dockerfile analysis and optimization.
    
    Features:
    - Dockerfile best practices
    - Layer optimization
    - Security analysis
    - Multi-stage build recommendations
    - Image size reduction
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "dockerfile_analyzer",
            "description": "Analyze and optimize Dockerfiles with AI-powered analysis",
            "category": ToolCategory.CLOUD,
            "parameters": {
                "type": "object",
                "properties": {
                    "dockerfile": {
                        "type": "string",
                        "description": "Dockerfile content or path"
                    },
                    "base_image": {
                        "type": "string",
                        "description": "Base image being used"
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["best_practices", "security", "performance", "all"],
                        "description": "Type of analysis to perform"
                    },
                    "include_optimized": {
                        "type": "boolean",
                        "description": "Include optimized Dockerfile"
                    }
                },
                "required": ["dockerfile"]
            }
        }
    
    async def execute(
        self,
        dockerfile: str,
        base_image: Optional[str] = None,
        analysis_type: str = "all",
        include_optimized: bool = False
    ) -> ToolResult:
        """Execute Dockerfile analysis.
        
        Args:
            dockerfile: Dockerfile content
            base_image: Base image
            analysis_type: Type of analysis
            include_optimized: Include optimized version
            
        Returns:
            ToolResult with Dockerfile analysis
        """
        prompt = f"""Analyze the following Dockerfile

Dockerfile:
```
{dockerfile}
```
"""
        
        if base_image:
            prompt += f"\nBase Image: {base_image}"
        
        prompt += f"""
Analysis Type: {analysis_type}

Please provide:
1. Best practices violations
2. Security issues (if analyzing security)
3. Layer optimization opportunities
4. Image size reduction strategies
5. Multi-stage build recommendations
6. Build cache optimization
7. Dependency management suggestions
"""
        
        if include_optimized:
            prompt += "\n8. Optimized Dockerfile with improvements"
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "base_image": base_image,
                "analysis_type": analysis_type,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Use multi-stage builds to reduce image size",
                "Combine RUN commands to reduce layers",
                "Use .dockerignore to exclude unnecessary files",
                "Pin specific base image versions for reproducibility"
            ],
            confidence=0.85
        )
