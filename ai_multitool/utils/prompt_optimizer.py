"""Prompt optimization utilities to reduce token usage."""

import re
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class OptimizationResult:
    """Result of prompt optimization."""
    optimized_prompt: str
    original_tokens: int
    optimized_tokens: int
    reduction_percent: float
    techniques_used: list[str]


class PromptOptimizer:
    """Optimizes prompts to reduce token usage while maintaining effectiveness."""
    
    # Patterns that can be safely removed or compressed
    REDUNDANT_PHRASES = [
        r"Please ",
        r"Kindly ",
        r"I would like you to ",
        r"Can you please ",
        r"Could you please ",
        r"I need you to ",
        r"Your task is to ",
        r"The goal is to ",
        r"You should ",
        r"Make sure to ",
        r"Ensure that ",
        r"Don't forget to ",
        r"Remember to ",
    ]
    
    # Patterns that can be shortened
    SHORTENINGS = {
        "information": "info",
        "description": "desc",
        "optimization": "opt",
        "recommendation": "rec",
        "suggestion": "sugg",
        "improvement": "imp",
        "performance": "perf",
        "implementation": "impl",
        "configuration": "config",
        "documentation": "docs",
        "functionality": "func",
        "capability": "cap",
        "requirement": "req",
        "specification": "spec",
        "architecture": "arch",
        "structure": "struct",
        "analysis": "anal",
        "evaluation": "eval",
        "generation": "gen",
        "processing": "proc",
        "calculation": "calc",
        "validation": "val",
        "verification": "verif",
    }
    
    @staticmethod
    def optimize_prompt(prompt: str, max_tokens: Optional[int] = None) -> OptimizationResult:
        """Optimize a prompt to reduce token usage.
        
        Args:
            prompt: Original prompt
            max_tokens: Maximum tokens allowed (truncates if exceeded)
            
        Returns:
            OptimizationResult with optimized prompt and metrics
        """
        original_tokens = PromptOptimizer.estimate_tokens(prompt)
        optimized = prompt
        techniques = []
        
        # 1. Remove redundant phrases
        optimized, removed = PromptOptimizer._remove_redundant_phrases(optimized)
        if removed:
            techniques.append("redundant_phrase_removal")
        
        # 2. Apply common shortenings
        optimized, shortened = PromptOptimizer._apply_shortenings(optimized)
        if shortened:
            techniques.append("word_shortening")
        
        # 3. Remove excessive whitespace
        optimized, whitespace = PromptOptimizer._compress_whitespace(optimized)
        if whitespace:
            techniques.append("whitespace_compression")
        
        # 4. Remove verbose JSON structure
        optimized, json_compact = PromptOptimizer._compact_json_structure(optimized)
        if json_compact:
            techniques.append("json_compaction")
        
        # 5. Truncate if still too long
        if max_tokens:
            optimized_tokens = PromptOptimizer.estimate_tokens(optimized)
            if optimized_tokens > max_tokens:
                optimized, truncated = PromptOptimizer._smart_truncate(optimized, max_tokens)
                if truncated:
                    techniques.append("smart_truncation")
        
        optimized_tokens = PromptOptimizer.estimate_tokens(optimized)
        reduction = ((original_tokens - optimized_tokens) / original_tokens * 100) if original_tokens > 0 else 0
        
        return OptimizationResult(
            optimized_prompt=optimized,
            original_tokens=original_tokens,
            optimized_tokens=optimized_tokens,
            reduction_percent=round(reduction, 1),
            techniques_used=techniques
        )
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count (rough approximation)."""
        if not text:
            return 0
        # Rough estimation: ~4 characters per token for English
        return max(1, len(text) // 4)
    
    @staticmethod
    def _remove_redundant_phrases(text: str) -> Tuple[str, bool]:
        """Remove redundant conversational phrases."""
        modified = False
        for phrase in PromptOptimizer.REDUNDANT_PHRASES:
            if re.search(phrase, text, re.IGNORECASE):
                text = re.sub(phrase, "", text, flags=re.IGNORECASE)
                modified = True
        return text, modified
    
    @staticmethod
    def _apply_shortenings(text: str) -> Tuple[str, bool]:
        """Apply common word shortenings."""
        modified = False
        for long_word, short_word in PromptOptimizer.SHORTENINGS.items():
            if re.search(r"\b" + long_word + r"\b", text, re.IGNORECASE):
                text = re.sub(r"\b" + long_word + r"\b", short_word, text, flags=re.IGNORECASE)
                modified = True
        return text, modified
    
    @staticmethod
    def _compress_whitespace(text: str) -> Tuple[str, bool]:
        """Compress multiple spaces and newlines."""
        original = text
        # Replace multiple spaces with single space
        text = re.sub(r" +", " ", text)
        # Replace multiple newlines with double newline
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Remove leading/trailing whitespace from lines
        text = "\n".join(line.strip() for line in text.split("\n"))
        return text, text != original
    
    @staticmethod
    def _compact_json_structure(text: str) -> Tuple[str, bool]:
        """Compact JSON structure in prompts."""
        modified = False
        # Compact JSON blocks by removing extra spacing
        json_blocks = re.findall(r'\{[\s\S]*?\}', text)
        for block in json_blocks:
            try:
                import json
                # Parse and re-minify
                parsed = json.loads(block)
                compact = json.dumps(parsed, separators=(",", ":"))
                text = text.replace(block, compact)
                modified = True
            except:
                pass
        return text, modified
    
    @staticmethod
    def _smart_truncate(text: str, max_tokens: int) -> Tuple[str, bool]:
        """Intelligently truncate text while preserving structure."""
        current_tokens = PromptOptimizer.estimate_tokens(text)
        if current_tokens <= max_tokens:
            return text, False
        
        # Calculate how much to remove
        target_ratio = max_tokens / current_tokens
        target_length = int(len(text) * target_ratio)
        
        # Try to truncate at a natural break point
        # Prefer truncating in code blocks or JSON first
        code_block_pattern = r'```[\s\S]*?```'
        code_blocks = re.findall(code_block_pattern, text)
        
        if code_blocks:
            # Truncate the largest code block
            largest_block = max(code_blocks, key=len)
            if len(largest_block) > target_length // 2:
                # Truncate code block to half target length
                truncated_block = largest_block[:target_length // 2] + "\n```"
                text = text.replace(largest_block, truncated_block)
                return text, True
        
        # If no code blocks, truncate from the end
        truncated = text[:target_length]
        # Try to end at a sentence boundary
        last_period = truncated.rfind(".")
        if last_period > target_length * 0.8:
            truncated = truncated[:last_period + 1]
        
        return truncated, True


class InputTruncator:
    """Truncates input content to reduce token usage."""
    
    @staticmethod
    def truncate_code(code: str, max_lines: int = 500, max_chars: int = 10000) -> str:
        """Truncate code to specified limits.
        
        Args:
            code: Code content
            max_lines: Maximum lines to keep
            max_chars: Maximum characters to keep
            
        Returns:
            Truncated code
        """
        lines = code.split("\n")
        
        # Truncate by lines
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            lines.append(f"\n# ... ({len(lines) - max_lines} more lines truncated)")
        
        truncated = "\n".join(lines)
        
        # Truncate by characters
        if len(truncated) > max_chars:
            truncated = truncated[:max_chars]
            truncated += "\n# ... (content truncated)"
        
        return truncated
    
    @staticmethod
    def truncate_text(text: str, max_chars: int = 5000) -> str:
        """Truncate text content.
        
        Args:
            text: Text content
            max_chars: Maximum characters
            
        Returns:
            Truncated text
        """
        if len(text) <= max_chars:
            return text
        
        # Try to truncate at sentence boundary
        truncated = text[:max_chars]
        last_period = truncated.rfind(".")
        if last_period > max_chars * 0.8:
            truncated = truncated[:last_period + 1]
        
        return truncated + "..."
    
    @staticmethod
    def smart_truncate(content: str, content_type: str = "text") -> str:
        """Smart truncation based on content type.
        
        Args:
            content: Content to truncate
            content_type: Type of content (code, text, json, etc.)
            
        Returns:
            Truncated content
        """
        if content_type == "code":
            return InputTruncator.truncate_code(content)
        elif content_type == "json":
            return InputTruncator.truncate_text(content, max_chars=3000)
        else:
            return InputTruncator.truncate_text(content)
