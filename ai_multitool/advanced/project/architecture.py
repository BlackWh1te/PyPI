"""Architecture analysis and visualization."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class AdvancedArchitecture(AdvancedTool):
    """Architecture analysis and visualization.
    
    Analyzes:
    - System architecture
    - Component relationships
    - Design patterns
    - Architectural smells
    - Coupling and cohesion
    """
    
    
        """Get the tool definition for architecture.

Returns:
    Tool definition dictionary with name, description, and parameters schema.
    The definition follows the standard tool registration format for
    integration with AI systems and CLI tools.
"""
        
            "name": "analyze_architecture",
            "description": "Architecture analysis and visualization",
            "parameters": {
                "type": "object",
                "properties": {
                    "codebase_path": {"type": "string"},
                    "analysis_depth": {"type": "string", "enum": ["overview", "detailed", "deep"], "default": "overview"}
                },
                "required": ["codebase_path"]
            }
        }
    
    async def execute(self, codebase_path: str, analysis_depth: str = "overview", **kwargs) -> ToolResult:
        start_time = time.time()
        
        try:
            from ...parsers.code_parser import CodeParser
            from ...utils.file_utils import read_directory
            
            parser = CodeParser()
            files = read_directory(codebase_path, max_files=50)
            
            # Analyze code structure
            components = []
            for file_info in files:
                try:
                    structure = parser.parse_file(file_info["path"])
                    components.append({
                        "file": file_info["path"],
                        "functions": len(structure.functions),
                        "classes": len(structure.classes),
                        "imports": structure.imports
                    })
                except (ValueError, KeyError, AttributeError):
                    # Skip files that can't be parsed
                    pass
            
            prompt = f"""Analyze architecture of this codebase ({analysis_depth} depth):

Components: {len(components)} files
Sample: {components[:5]}

Provide JSON:
{{
    "architecture_type": "monolith|microservices|layered|event_driven",
    "layers": ["layer names"],
    "components": [{"name": "component", "responsibility": "what"}],
    "patterns": ["design patterns detected"],
    "coupling_analysis": {{"component": "coupling_score"}},
    "recommendations": ["architectural improvements"]
}}"""
            
            response = await self.llm_client.chat([Message(role=MessageRole.USER, content=prompt)])
            
            return ToolResult(
                success=True,
                data={"architecture_analysis": response.content},
                confidence=0.8,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=response.tokens_used
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
