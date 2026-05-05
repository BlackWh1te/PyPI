"""Advanced code refactoring with AI."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole
from ...parsers.code_parser import CodeParser, CodeStructure


class AdvancedCodeRefactoring(AdvancedTool):
    """AI-powered code refactoring tool.
    
    Analyzes code and suggests/implements refactoring improvements including:
    - Variable/function renaming for clarity
    - Extracting methods/functions
    - Reducing code duplication
    - Improving code organization
    - Applying design patterns
    - Optimizing performance
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code_parser = CodeParser()
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for code refactoring.
        
        Returns:
            Tool definition dictionary with name, description, and parameters schema.
            The definition follows the standard tool registration format for
            integration with AI systems and CLI tools.
        """
        return {
            "name": "refactor_code",
            "description": "AI-powered code refactoring with suggestions for improvements",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the code file to refactor"
                    },
                    "code": {
                        "type": "string",
                        "description": "Code content to refactor (alternative to file_path)"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language (auto-detected if not provided)"
                    },
                    "aggressive": {
                        "type": "boolean",
                        "description": "Enable aggressive refactoring (more changes)",
                        "default": False
                    },
                    "focus_areas": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Areas to focus on (readability, performance, maintainability, all)",
                        "default": ["all"]
                    },
                    "apply_changes": {
                        "type": "boolean",
                        "description": "Whether to apply changes or just suggest",
                        "default": False
                    }
                },
                "required": []
            }
        }
    
    async def execute(
        self,
        file_path: Optional[str] = None,
        code: Optional[str] = None,
        language: Optional[str] = None,
        aggressive: bool = False,
        focus_areas: List[str] = None,
        apply_changes: bool = False,
        **kwargs
    ) -> ToolResult:
        """Execute code refactoring.
        
        Args:
            file_path: Path to code file
            code: Code content directly
            language: Programming language
            aggressive: Enable aggressive refactoring
            focus_areas: Areas to focus on
            apply_changes: Apply changes or just suggest
            
        Returns:
            ToolResult with refactoring suggestions/changes
        """
        start_time = time.time()
        focus_areas = focus_areas or ["all"]
        
        try:
            # Get code content
            if file_path:
                from ...utils.file_utils import read_file
                code_content = read_file(file_path)
                if not language:
                    structure = self.code_parser.parse_file(file_path)
                    language = structure.language
            elif code:
                code_content = code
            else:
                return ToolResult(
                    success=False,
                    status=ToolStatus.FAILED,
                    errors=["Either file_path or code must be provided"]
                )
            
            # Build refactoring prompt
            prompt = self._build_refactoring_prompt(
                code_content,
                language,
                aggressive,
                focus_areas
            )
            
            # Get AI suggestions
            response = await self.llm_client.chat([
                Message(role=MessageRole.USER, content=prompt)
            ])
            
            # Parse AI response
            refactoring_plan = self._parse_refactoring_response(response.content)
            
            # Apply changes if requested
            applied_changes = []
            if apply_changes and file_path:
                applied_changes = await self._apply_refactoring(
                    file_path,
                    refactoring_plan
                )
            
            execution_time = (time.time() - start_time) * 1000
            
            return ToolResult(
                success=True,
                status=ToolStatus.SUCCESS,
                data={
                    "original_code": code_content,
                    "refactored_code": refactoring_plan.get("refactored_code", ""),
                    "changes": refactoring_plan.get("changes", []),
                    "applied_changes": applied_changes,
                    "language": language,
                    "aggressive": aggressive,
                    "focus_areas": focus_areas
                },
                metrics={
                    "execution_time_ms": execution_time,
                    "changes_count": len(refactoring_plan.get("changes", [])),
                    "complexity_reduction": refactoring_plan.get("complexity_reduction", 0)
                },
                suggestions=refactoring_plan.get("suggestions", []),
                confidence=refactoring_plan.get("confidence", 0.8),
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
    
    def _build_refactoring_prompt(
        self,
        code: str,
        language: str,
        aggressive: bool,
        focus_areas: List[str]
    ) -> str:
        """Build refactoring prompt for AI.
        
        Args:
            code: Code to refactor
            language: Programming language
            aggressive: Aggressive refactoring
            focus_areas: Focus areas
            
        Returns:
            Refactoring prompt
        """
        focus_instruction = ""
        if "all" not in focus_areas:
            focus_instruction = f"Focus specifically on: {', '.join(focus_areas)}."
        
        aggressiveness = "extensive" if aggressive else "conservative"
        
        prompt = f"""You are an expert code refactoring assistant for {language or 'programming'}.

Analyze the following code and provide refactoring suggestions.

Code:
```{language or ''}
{code}
```

Refactoring requirements:
- Use {aggressiveness} refactoring approach
- {focus_instruction}
- Ensure changes maintain functionality
- Improve code quality, readability, and maintainability
- Consider performance implications

Provide your response in the following JSON format:
{{
    "summary": "Brief summary of refactoring needed",
    "changes": [
        {{
            "type": "rename|extract|inline|restructure|optimize",
            "description": "What to change and why",
            "location": "line numbers or function names",
            "original": "original code snippet",
            "refactored": "refactored code snippet",
            "impact": "high|medium|low"
        }}
    ],
    "refactored_code": "Complete refactored code if applying changes",
    "suggestions": ["Additional suggestions not implemented"],
    "complexity_reduction": "Estimated complexity reduction (0-100)",
    "confidence": 0.0-1.0
}}"""
        
        return prompt
    
    def _parse_refactoring_response(self, response: str) -> Dict[str, Any]:
        """Parse AI refactoring response.
        
        Args:
            response: AI response text
            
        Returns:
            Parsed refactoring plan
        """
        import json
        import re
        
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        # Fallback: parse as plain text
        return {
            "summary": response[:200],
            "changes": [],
            "refactored_code": "",
            "suggestions": [response],
            "complexity_reduction": 0,
            "confidence": 0.5
        }
    
    async def _apply_refactoring(
        self,
        file_path: str,
        refactoring_plan: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply refactoring changes to file.
        
        Args:
            file_path: Path to file
            refactoring_plan: Refactoring plan
            
        Returns:
            List of applied changes
        """
        applied = []
        
        # Read original file
        from ...utils.file_utils import read_file, write_file
        original_code = read_file(file_path)
        
        # Apply refactored code if provided
        refactored_code = refactoring_plan.get("refactored_code")
        if refactored_code and refactored_code != original_code:
            write_file(file_path, refactored_code)
            applied.append({
                "type": "full_refactor",
                "description": "Applied complete refactoring"
            })
        
        return applied
