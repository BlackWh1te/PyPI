"""Content sanitization for security and privacy."""

import re
from typing import List, Optional, Tuple
from dataclasses import dataclass

from ai_multitool.core.exceptions import SanitizationError, ValidationError


@dataclass
class SanitizationResult:
    """Result of content sanitization."""
    original_content: str
    sanitized_content: str
    issues_found: List[str]
    warnings: List[str]
    is_safe: bool


class ContentSanitizer:
    """Sanitize content to prevent security issues and protect sensitive data."""
    
    # Patterns that might indicate prompt injection
    INJECTION_PATTERNS = [
        r'ignore\s+(previous|all)\s+instructions',
        r'system\s*:\s*ignore',
        r'override\s+system\s+prompt',
        r'act\s+as\s+(a\s+)?(jailbroken|unrestricted)',
        r'disregard\s+(previous|all)\s+(instructions|rules)',
        r'forget\s+(everything|previous\s+instructions)',
        r'new\s+(role|persona|character)',
        r'you\s+are\s+now\s+(jailbroken|unrestricted)',
        r'dan\s+mode',
        r'simulator\s+mode',
        r'developer\s+mode',
    ]
    
    # Sensitive data patterns (basic)
    SENSITIVE_PATTERNS = [
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'EMAIL'),
        (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 'PHONE'),
        (r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', 'CREDIT_CARD'),
        (r'\b[A-Z]{2}[0-9A-Z]{9}\b', 'SSN'),
        (r'\b(?:sk|pk|sk_live|pk_live|sk_test|pk_test)_[a-zA-Z0-9]{32,}\b', 'STRIPE_KEY'),
        (r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b', 'AWS_KEY'),
        (r'\bAIza[0-9A-Za-z\\-_]{35}\b', 'GOOGLE_API_KEY'),
        (r'\bsk-[a-zA-Z0-9]{48}\b', 'OPENAI_KEY'),
        (r'\bsk-ant-[a-zA-Z0-9_-]{95}\b', 'ANTHROPIC_KEY'),
    ]
    
    # File paths that might contain sensitive data
    SENSITIVE_FILE_PATTERNS = [
        r'\.env$',
        r'\.pem$',
        r'\.key$',
        r'\.p12$',
        r'\.pfx$',
        r'password',
        r'secret',
        r'credential',
        r'auth',
        r'token',
        r'private',
    ]
    
    def __init__(self):
        """Initialize the content sanitizer."""
        self.injection_regex = re.compile(
            '|'.join(self.INJECTION_PATTERNS),
            re.IGNORECASE | re.MULTILINE
        )
        self.sensitive_regexes = [
            (re.compile(pattern, re.IGNORECASE), label)
            for pattern, label in self.SENSITIVE_PATTERNS
        ]
        self.sensitive_file_regex = re.compile(
            '|'.join(self.SENSITIVE_FILE_PATTERNS),
            re.IGNORECASE
        )
    
    def sanitize(self, content: str, file_path: str = None) -> SanitizationResult:
        """Sanitize content for security and privacy."""
        if content is None:
            raise ValidationError("Content cannot be None", field="content")
        
        if not isinstance(content, str):
            raise ValidationError("Content must be a string", field="content")
        
        issues = []
        warnings = []
        sanitized = content
        
        try:
            # Check for prompt injection attempts
            injection_matches = self.injection_regex.findall(content)
            if injection_matches:
                issues.append(f"Potential prompt injection detected: {injection_matches[:3]}")
                # Remove or flag the injection attempts
                for match in injection_matches:
                    sanitized = sanitized.replace(match, "[POTENTIAL_INJECTION_REMOVED]")
            
            # Check for sensitive data
            for regex, label in self.sensitive_regexes:
                try:
                    matches = regex.findall(content)
                    if matches:
                        issues.append(f"Sensitive data detected ({label}): {len(matches)} occurrences")
                        # Redact sensitive data
                        for match in matches:
                            if label == 'EMAIL':
                                sanitized = sanitized.replace(match, self._redact_email(match))
                            elif label in ['PHONE', 'CREDIT_CARD', 'SSN']:
                                sanitized = sanitized.replace(match, self._redact_number(match))
                            else:
                                # For API keys, show first 4 and last 4 characters
                                if len(match) > 8:
                                    redacted = match[:4] + '*' * (len(match) - 8) + match[-4:]
                                else:
                                    redacted = '*' * len(match)
                                sanitized = sanitized.replace(match, redacted)
                except re.error:
                    # Skip this pattern if regex fails
                    continue
            
            # Check file path for sensitive files
            if file_path:
                try:
                    if self.sensitive_file_regex.search(file_path):
                        warnings.append(f"File path may contain sensitive data: {file_path}")
                except re.error:
                    pass
            
            # Check for extremely long content that might cause issues
            if len(sanitized) > 100000:
                warnings.append(f"Content is very long ({len(sanitized)} chars), consider truncating")
            
            # Check for binary-like content
            if self._is_binary_like(content):
                warnings.append("Content appears to be binary or contains non-text data")
            
            is_safe = len(issues) == 0
            
            return SanitizationResult(
                original_content=content,
                sanitized_content=sanitized,
                issues_found=issues,
                warnings=warnings,
                is_safe=is_safe
            )
        except (SanitizationError, ValidationError):
            raise
        except Exception as e:
            raise SanitizationError(
                f"Failed to sanitize content",
                file_path=file_path,
                details={"error_type": type(e).__name__, "error": str(e)}
            )
    
    def _redact_email(self, email: str) -> str:
        """Redact email address while preserving format."""
        if '@' in email:
            local, domain = email.split('@', 1)
            if len(local) > 2:
                local = local[0] + '*' * (len(local) - 2) + local[-1]
            return f"{local}@{domain}"
        return '*' * len(email)
    
    def _redact_number(self, number: str) -> str:
        """Redact phone/SSN/credit card numbers."""
        # Remove non-alphanumeric characters
        clean = re.sub(r'[^0-9]', '', number)
        if len(clean) > 4:
            return clean[:2] + '*' * (len(clean) - 4) + clean[-2:]
        return '*' * len(clean)
    
    def _is_binary_like(self, content: str) -> bool:
        """Check if content appears to be binary."""
        # Check for null bytes
        if '\x00' in content:
            return True
        
        # Check for high ratio of non-printable characters
        printable = sum(1 for c in content if c.isprintable() or c in '\n\r\t')
        if len(content) > 100 and printable / len(content) < 0.7:
            return True
        
        return False
    
    def check_file_safety(self, file_path: str) -> Tuple[bool, List[str]]:
        """Check if a file is safe to analyze."""
        if not file_path or not file_path.strip():
            raise ValidationError("File path cannot be empty", field="file_path")
        
        warnings = []
        
        try:
            # Check file extension
            if self.sensitive_file_regex.search(file_path):
                warnings.append(f"File may contain sensitive data: {file_path}")
                return False, warnings
            
            # Check for binary file extensions
            binary_extensions = ['.exe', '.dll', '.so', '.dylib', '.bin', '.zip', '.tar', '.gz', '.7z', '.rar']
            if any(file_path.lower().endswith(ext) for ext in binary_extensions):
                warnings.append(f"File appears to be binary: {file_path}")
                return False, warnings
        except re.error:
            # If regex fails, continue with other checks
            pass
        
        return True, warnings
    
    def sanitize_code_snippet(self, code: str, language: str = None) -> str:
        """Sanitize code snippets specifically."""
        if code is None:
            raise ValidationError("Code cannot be None", field="code")
        
        if not isinstance(code, str):
            raise ValidationError("Code must be a string", field="code")
        
        try:
            # Remove comments that might contain sensitive data
            if language in ['python', 'javascript', 'typescript']:
                # Remove single-line comments
                code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
                # Remove multi-line comments
                code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
            
            # Check for hardcoded secrets in code
            secret_patterns = [
                (r'password\s*=\s*[\'"][^\'"]+[\'"]', 'Hardcoded password'),
                (r'api[_-]?key\s*=\s*[\'"][^\'"]+[\'"]', 'Hardcoded API key'),
                (r'secret\s*=\s*[\'"][^\'"]+[\'"]', 'Hardcoded secret'),
                (r'token\s*=\s*[\'"][^\'"]+[\'"]', 'Hardcoded token'),
            ]
            
            for pattern, label in secret_patterns:
                try:
                    matches = re.findall(pattern, code, re.IGNORECASE)
                    if matches:
                        for match in matches:
                            # Extract the value
                            value_match = re.search(r'[\'"]([^\'"]+)[\'"]', match)
                            if value_match:
                                value = value_match.group(1)
                                if len(value) > 8:
                                    redacted = value[:4] + '*' * (len(value) - 8) + value[-4:]
                                else:
                                    redacted = '*' * len(value)
                                code = code.replace(value, redacted)
                except re.error:
                    # Skip this pattern if regex fails
                    continue
            
            return code
        except (SanitizationError, ValidationError):
            raise
        except Exception as e:
            raise SanitizationError(
                f"Failed to sanitize code snippet",
                details={"error_type": type(e).__name__, "error": str(e)}
            )


# Singleton instance
_sanitizer_instance: Optional[ContentSanitizer] = None


def get_sanitizer() -> ContentSanitizer:
    """Get the singleton sanitizer instance."""
    global _sanitizer_instance
    if _sanitizer_instance is None:
        _sanitizer_instance = ContentSanitizer()
    return _sanitizer_instance
