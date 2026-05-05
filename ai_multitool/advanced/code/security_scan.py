"""Advanced security scanning in code."""

import time
import re
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole
from ...parsers.code_parser import CodeParser


class AdvancedSecurityScan(AdvancedTool):
    """Security vulnerability scanning in code.
    
    Scans for:
    - SQL injection vulnerabilities
    - XSS vulnerabilities
    - Hardcoded secrets/credentials
    - Insecure cryptographic practices
    - Command injection
    - Path traversal
    - CSRF vulnerabilities
    - Insecure deserialization
    - Buffer overflows
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code_parser = CodeParser()
        
        # Common secret patterns
        self.secret_patterns = [
            r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'secret[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'password\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'aws[_-]?access[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'private[_-]?key\s*=\s*["\'][^"\']+["\']',
        ]
    
    
        """Get the tool definition for security scan.

Returns:
    Tool definition dictionary with name, description, and parameters schema.
    The definition follows the standard tool registration format for
    integration with AI systems and CLI tools.
"""
        
            "name": "security_scan",
            "description": "Security vulnerability scanning in code",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "code": {"type": "string"},
                    "language": {"type": "string"},
                    "scan_secrets": {"type": "boolean", "default": True},
                    "scan_vulnerabilities": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    
    async def execute(self, file_path: Optional[str] = None, code: Optional[str] = None,
                     language: Optional[str] = None, scan_secrets: bool = True,
                     scan_vulnerabilities: bool = True, **kwargs) -> ToolResult:
        start_time = time.time()
        vulnerabilities = []
        secrets_found = []
        
        try:
            if file_path:
                from ...utils.file_utils import read_file
                code_content = read_file(file_path)
                structure = self.code_parser.parse_file(file_path)
                language = language or structure.language
            else:
                code_content = code or ""
            
            # Scan for secrets (pattern-based)
            if scan_secrets:
                secrets_found = self._scan_secrets(code_content)
            
            # Scan for vulnerabilities (AI-based)
            if scan_vulnerabilities:
                prompt = f"""Security analysis of this {language or 'code'}:

```{language or ''}
{code_content}
```

Identify security vulnerabilities. Provide JSON:
{{
    "vulnerabilities": [
        {{
            "type": "SQLi|XSS|Command Injection|Path Traversal|CSRF|Insecure Crypto|Other",
            "severity": "critical|high|medium|low",
            "location": "where",
            "description": "what",
            "fix": "how to fix"
        }}
    ],
    "overall_risk": "critical|high|medium|low"
}}"""

                response = await self.llm_client.chat([Message(role=MessageRole.USER, content=prompt)])
                vulnerabilities = self._parse_vulnerabilities(response.content)
            
            return ToolResult(
                success=True,
                data={
                    "vulnerabilities": vulnerabilities,
                    "secrets": secrets_found,
                    "total_vulnerabilities": len(vulnerabilities),
                    "total_secrets": len(secrets_found)
                },
                metrics={
                    "critical_vulns": len([v for v in vulnerabilities if v.get("severity") == "critical"]),
                    "high_vulns": len([v for v in vulnerabilities if v.get("severity") == "high"])
                },
                suggestions=[v["fix"] for v in vulnerabilities] + [f"Remove secret: {s}" for s in secrets_found],
                confidence=0.9,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=response.tokens_used
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
    
    def _scan_secrets(self, code: str) -> List[str]:
        """Scan for hardcoded secrets using patterns."""
        secrets = []
        for pattern in self.secret_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                secrets.append(f"Potential secret at line {code[:match.start()].count('\\n') + 1}")
        return secrets
    
    def _parse_vulnerabilities(self, response: str) -> List[Dict]:
        import json
        try:
            match = re.search(r'\{[\s\S]*\}', response)
            if match:
                return json.loads(match.group()).get("vulnerabilities", [])
        except (json.JSONDecodeError, ValueError, KeyError):
            # If parsing fails, return empty list
            pass
        return []
