"""Secret and credential scanning."""

import time
import re
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole


class AdvancedSecretScanner(AdvancedTool):
    """Secret and credential scanning.
    
    Scans for:
    - API keys
    - Database credentials
    - SSH keys
    - Certificates
    - Tokens
    - Passwords
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Comprehensive secret patterns
        self.patterns = {
            "aws_key": r'AKIA[0-9A-Z]{16}',
            "aws_secret": r'[0-9a-zA-Z/+]{40}',
            "google_api_key": r'AIza[0-9A-Za-z\-_]{35}',
            "github_token": r'ghp_[a-zA-Z0-9]{36}',
            "slack_token": r'xox[bap]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32}',
            "stripe_key": r'sk_(live|test)_[0-9a-zA-Z]{24}',
            "private_key': r'-----BEGIN ((RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----)',
            "api_key": r'(?i)(api[_-]?key|apikey)[\s=:]+["\']?[a-zA-Z0-9_\-]{16,}["\']?',
            "password": r'(?i)(password|passwd|pwd)[\s=:]+["\']?[^\s"\']{6,}["\']?',
            "token": r'(?i)(token|auth[_-]?token)[\s=:]+["\']?[a-zA-Z0-9_\-]{20,}["\']?',
        }
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "scan_secrets",
            "description": "Scan for secrets and credentials",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "directory": {"type": "string"},
                    "content": {"type": "string"},
                    "severity": {"type": "string", "enum": ["all", "critical", "high", "medium"], "default": "all"}
                },
                "required": []
            }
        }
    
    async def execute(self, file_path: Optional[str] = None, directory: Optional[str] = None,
                     content: Optional[str] = None, severity: str = "all", **kwargs) -> ToolResult:
        start_time = time.time()
        secrets_found = []
        
        try:
            if file_path:
                from ...utils.file_utils import read_file
                scan_content = read_file(file_path)
                secrets = self._scan_content(scan_content, file_path)
            elif content:
                secrets = self._scan_content(content, "string")
            elif directory:
                from ...utils.file_utils import read_directory
                files = read_directory(directory, max_files=100)
                for file_info in files:
                    scan_content = file_info.get("content", "")
                    secrets.extend(self._scan_content(scan_content, file_info.get("path")))
            else:
                return ToolResult(success=False, errors=["No content to scan"])
            
            # Filter by severity
            if severity != "all":
                secrets = [s for s in secrets if s.get("severity") == severity]
            
            return ToolResult(
                success=True,
                data={
                    "secrets": secrets,
                    "total_secrets": len(secrets),
                    "severity_filter": severity
                },
                metrics={
                    "critical_secrets": len([s for s in secrets if s.get("severity") == "critical"]),
                    "high_secrets": len([s for s in secrets if s.get("severity") == "high"])
                },
                suggestions=[f"Remove/revoke: {s['type']} at {s['location']}" for s in secrets],
                confidence=0.95,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=0
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
    
    def _scan_content(self, content: str, location: str) -> List[Dict[str, Any]]:
        secrets = []
        lines = content.split('\n')
        
        for secret_type, pattern in self.patterns.items():
            for line_num, line in enumerate(lines, 1):
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    secrets.append({
                        "type": secret_type,
                        "location": f"{location}:{line_num}",
                        "line": line.strip(),
                        "match": match.group(),
                        "severity": self._get_severity(secret_type)
                    })
        
        return secrets
    
    def _get_severity(self, secret_type: str) -> str:
        critical_types = ["aws_key", "aws_secret", "private_key", "stripe_key"]
        high_types = ["google_api_key", "github_token", "slack_token"]
        
        if secret_type in critical_types:
            return "critical"
        elif secret_type in high_types:
            return "high"
        else:
            return "medium"
