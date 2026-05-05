"""Embedding models for text vectorization."""

from abc import ABC, abstractmethod
from typing import List, Optional
import os

from ai_multitool.core.exceptions import APIError, APIKeyError, ValidationError


class EmbeddingModel(ABC):
    """Abstract base class for embedding models."""
    
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        pass


class OpenAIEmbeddings(EmbeddingModel):
    """OpenAI embedding model using text-embedding-3-small."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
        """Initialize OpenAI embeddings.
        
        Args:
            api_key: OpenAI API key. If None, uses OPENAI_API_KEY env var.
            model: Model name to use. Default: text-embedding-3-small (1536 dimensions)
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise APIKeyError(
                "OpenAI API key not found",
                provider="openai",
                suggestion="Set OPENAI_API_KEY environment variable or pass api_key parameter"
            )
        
        self.model = model
        self._dimension = 1536  # text-embedding-3-small dimension
        
        # Lazy import to avoid requiring openai package unless used
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "openai package is required for OpenAI embeddings. "
                "Install with: pip install openai"
            )
    
    def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        if not text or not text.strip():
            raise ValidationError("Text cannot be empty", field="text")
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise APIError(
                f"Failed to generate embedding with OpenAI",
                provider="openai",
                model=self.model,
                details={"error_type": type(e).__name__, "error": str(e)}
            )
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (batched)."""
        if not texts:
            return []
        
        if any(not t or not t.strip() for t in texts):
            raise ValidationError("All texts must be non-empty", field="texts")
        
        embeddings = []
        
        # OpenAI supports batch embedding
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            embeddings = [item.embedding for item in response.data]
        except Exception as e:
            raise APIError(
                f"Failed to generate batch embeddings with OpenAI",
                provider="openai",
                model=self.model,
                details={"error_type": type(e).__name__, "error": str(e)}
            )
        
        return embeddings
    
    def get_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        return self._dimension


class FakeEmbeddings(EmbeddingModel):
    """Fake embedding model for testing (returns random vectors)."""
    
    def __init__(self, dimension: int = 1536):
        """Initialize fake embeddings for testing."""
        self._dimension = dimension
        import random
        self._random = random.Random(42)  # Fixed seed for reproducibility
    
    def embed(self, text: str) -> List[float]:
        """Generate a fake embedding (deterministic based on text hash)."""
        import hashlib
        # Use hash of text for deterministic but pseudo-random vectors
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        self._random.seed(hash_val)
        return [self._random.random() for _ in range(self._dimension)]
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate fake embeddings for multiple texts."""
        return [self.embed(text) for text in texts]
    
    def get_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        return self._dimension
