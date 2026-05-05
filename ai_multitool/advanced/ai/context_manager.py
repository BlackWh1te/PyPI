"""Advanced context window management."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole, ChatHistory


class AdvancedContextManager(AdvancedTool):
    """Advanced context window management.
    
    Provides:
    - Context compression
    - Smart truncation
    - Priority-based inclusion
    - Token estimation
    - Context optimization
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for context management.
        
        Returns:
            Tool definition dictionary with name, description, and parameters schema.
            The definition follows the standard tool registration format for
            integration with AI systems and CLI tools.
        """
        return {
            "name": "context_management",
            "description": "Advanced context window management",
            "parameters": {
                "type": "object",
                "properties": {
                    "messages": {"type": "array", "items": {"type": "object"}},
                    "max_tokens": {"type": "number", "default": 8000},
                    "strategy": {"type": "string", "enum": ["recent", "important", "hybrid"], "default": "hybrid"}
                },
                "required": ["messages"]
            }
        }
    
    async def execute(self, messages: List[Dict], max_tokens: int = 8000,
                     strategy: str = "hybrid", **kwargs) -> ToolResult:
        start_time = time.time()
        
        try:
            # Estimate tokens
            total_tokens = self._estimate_tokens(messages)
            
            if total_tokens <= max_tokens:
                return ToolResult(
                    success=True,
                    data={
                        "optimized_messages": messages,
                        "original_tokens": total_tokens,
                        "optimized_tokens": total_tokens,
                        "truncated": False
                    },
                    confidence=1.0,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    tokens_used=0
                )
            
            # Optimize context based on strategy
            if strategy == "recent":
                optimized = self._keep_recent(messages, max_tokens)
            elif strategy == "important":
                optimized = self._keep_important(messages, max_tokens)
            else:  # hybrid
                optimized = self._hybrid_selection(messages, max_tokens)
            
            optimized_tokens = self._estimate_tokens(optimized)
            
            return ToolResult(
                success=True,
                data={
                    "optimized_messages": optimized,
                    "original_tokens": total_tokens,
                    "optimized_tokens": optimized_tokens,
                    "truncated": True,
                    "strategy": strategy
                },
                suggestions=["Consider increasing max_tokens for full context"],
                confidence=0.9,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=0
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
    
    def _estimate_tokens(self, messages: List[Dict]) -> int:
        """Estimate token count."""
        total_chars = sum(len(str(m.get("content", ""))) for m in messages)
        return int(total_chars / 4)  # Rough estimate: 4 chars per token
    
    def _keep_recent(self, messages: List[Dict], max_tokens: int) -> List[Dict]:
        """Keep most recent messages."""
        result = []
        current_tokens = 0
        for msg in reversed(messages):
            msg_tokens = len(str(msg.get("content", ""))) / 4
            if current_tokens + msg_tokens <= max_tokens:
                result.insert(0, msg)
                current_tokens += msg_tokens
            else:
                break
        return result
    
    def _keep_important(self, messages: List[Dict], max_tokens: int) -> List[Dict]:
        """Keep important messages (system, user questions)."""
        # Simple implementation: prioritize system and user messages
        prioritized = [m for m in messages if m.get("role") in ["system", "user"]]
        others = [m for m in messages if m.get("role") not in ["system", "user"]]
        
        result = []
        current_tokens = 0
        for msg in prioritized + others:
            msg_tokens = len(str(msg.get("content", ""))) / 4
            if current_tokens + msg_tokens <= max_tokens:
                result.append(msg)
                current_tokens += msg_tokens
        
        return result
    
    def _hybrid_selection(self, messages: List[Dict], max_tokens: int) -> List[Dict]:
        """Hybrid selection: recent + important."""
        # Combine both strategies
        recent = self._keep_recent(messages, max_tokens * 0.7)
        important = self._keep_important(messages, max_tokens * 0.3)
        
        # Deduplicate while preserving order
        seen = set()
        result = []
        for msg in recent + important:
            msg_id = id(msg)
            if msg_id not in seen:
                result.append(msg)
                seen.add(msg_id)
        
        return result
