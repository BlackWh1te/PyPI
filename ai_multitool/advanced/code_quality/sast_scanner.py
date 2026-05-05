"""SAST Scanner - AI-powered Static Application Security Testing."""

from typing import Optional, Dict, Any
from ..base import AdvancedTool, ToolResult, ToolCategory, AdvancedToolConfig


class SASTScanner(AdvancedTool):
    """AI-powered Static Application Security Testing.
    
    Features:
    - Static code security analysis
    - Vulnerability pattern detection
    - Security best practices checking
    - OWASP Top 10 coverage
    - Custom rule support
    """
    
    def __init__(self, llm_client, config: Optional[AdvancedToolConfig] = None):
        super().__init__(llm_client, config)
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "sast_scanner",
            "description": "Perform static application security testing with AI-powered analysis",
            "category": ToolCategory.SECURITY,
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to scan for security issues"
                    },
                    "language": {
                        "type": "string",
                        "enum": ["python", "javascript", "typescript", "java", "go", "rust", "cpp"],
                        "description": "Programming language"
                    },
                    "scan_depth": {
                        "type": "string",
                        "enum": ["quick", "standard", "deep"],
                        "description": "Depth of security scan"
                    },
                    "check_types": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["injection", "xss", "auth", "crypto", "config", "all"]
                        },
                        "description": "Types of security checks to perform"
                    }
                },
                "required": ["code", "language"]
            }
        }
    
    async def execute(
        self,
        code: str,
        language: str,
        scan_depth: str = "standard",
        check_types: Optional[list] = None
    ) -> ToolResult:
        """Execute SAST scanning.
        
        Args:
            code: Code to scan
            language: Programming language
            scan_depth: Depth of scan
            check_types: Types of security checks
            
        Returns:
            ToolResult with security scan results
        """
        if check_types is None:
            check_types = ["all"]
        
        prompt = f"""Perform static security analysis on the following {language} code:

Scan Depth: {scan_depth}
Check Types: {', '.join(check_types)}

Code:
```
{code}
```

Please provide:
1. Security vulnerabilities found
2. Severity levels (critical, high, medium, low)
3. OWASP Top 10 categories affected
4. Line numbers where issues occur
5. Detailed explanations of each vulnerability
6. Remediation recommendations
7. Code examples showing fixes
"""
        
        response = await self._call_llm(prompt)
        
        return ToolResult(
            success=True,
            data={
                "language": language,
                "scan_depth": scan_depth,
                "check_types": check_types,
                "analysis": response.content
            },
            metrics={
                "tokens_used": response.tokens_used,
                "cached": response.cached
            },
            suggestions=[
                "Integrate SAST into CI/CD pipeline",
                "Use multiple SAST tools for comprehensive coverage",
                "Fix critical and high severity issues immediately",
                "Educate developers on secure coding practices"
            ],
            confidence=0.85
        )
