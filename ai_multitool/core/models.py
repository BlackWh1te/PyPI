"""Core data models for AI interactions"""

from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any
from enum import Enum
import time


class MessageRole(str, Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """Chat message"""
    role: MessageRole
    content: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


class LLMResponse(BaseModel):
    """LLM response"""
    content: str
    model: str
    tokens_used: int
    finish_reason: str
    latency_ms: Optional[float] = None
    cached: bool = False
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ModelInfo(BaseModel):
    """Model information and capabilities"""
    name: str
    max_tokens: int
    supports_streaming: bool
    supports_function_calling: bool
    cost_per_1k_input: float
    cost_per_1k_output: float
    context_window: Optional[int] = None


class ChatHistory(BaseModel):
    """Chat history with smart trimming"""
    messages: List[Message] = Field(default_factory=list)
    max_history: int = 10
    max_tokens: int = 8000
    system_prompt: Optional[str] = None

    def add_message(self, message: Message):
        """Add message to history"""
        self.messages.append(message)
        self._trim_history()

    def _trim_history(self):
        """Trim history by message count and token count"""
        # Trim by message count
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]

        # Trim by token count (rough estimate)
        total_tokens = sum(
            len(m.content.split()) * 1.3
            for m in self.messages
        )
        while total_tokens > self.max_tokens and len(self.messages) > 2:
            removed = self.messages.pop(0)
            total_tokens -= len(removed.content.split()) * 1.3

    def get_context_messages(self) -> List[Dict[str, str]]:
        """Get context messages for API call"""
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.extend([
            {"role": m.role.value, "content": m.content}
            for m in self.messages
        ])
        return messages
