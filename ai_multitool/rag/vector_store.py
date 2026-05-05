"""Vector store for storing and searching document embeddings."""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
import json
from pathlib import Path
import numpy as np

from ai_multitool.rag.chunkers import DocumentChunk
from ai_multitool.core.exceptions import ValidationError
from ai_multitool.constants import DEFAULT_EMBEDDING_DIMENSION, DEFAULT_MAX_CHUNKS


@dataclass
class SearchResult:
    """A search result with similarity score."""
    chunk: DocumentChunk
    score: float
    metadata: dict

    def __str__(self) -> str:
        """String representation."""
        preview = self.chunk.text[:50] + "..." if len(self.chunk.text) > 50 else self.chunk.text
        return f"SearchResult(score={self.score:.4f}, preview={preview})"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (f"SearchResult(chunk_id={self.chunk.chunk_id}, score={self.score:.4f}, "
                f"metadata_keys={list(self.metadata.keys())})")


class VectorStore(ABC):
    """Abstract base class for vector stores."""
    
    @abstractmethod
    def add(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> None:
        """Add document chunks with their embeddings to the store."""
        pass
    
    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResult]:
        """Search for similar chunks."""
        pass
    
    @abstractmethod
    def delete(self, chunk_id: str) -> bool:
        """Delete a chunk by ID."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all chunks from the store."""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Get the number of chunks in the store."""
        pass


class InMemoryVectorStore(VectorStore):
    """In-memory vector store using numpy for similarity search."""
    
    def __init__(self, dimension: int = None, max_chunks: int = None):
        """Initialize the in-memory vector store.
        
        Args:
            dimension: Dimension of the embedding vectors (default: from constants)
            max_chunks: Maximum number of chunks to store (default: from constants)
        """
        if dimension is None:
            dimension = DEFAULT_EMBEDDING_DIMENSION
        
        if max_chunks is None:
            max_chunks = DEFAULT_MAX_CHUNKS
        
        if dimension <= 0:
            raise ValueError("dimension must be positive")
        
        if max_chunks <= 0:
            raise ValueError("max_chunks must be positive")
        
        self.dimension = dimension
        self.max_chunks = max_chunks
        self.chunks: Dict[str, DocumentChunk] = {}
        # Changed: Use dynamic allocation instead of pre-allocation to reduce memory usage
        self.embeddings: np.ndarray = np.zeros((0, dimension), dtype=np.float32)
        self.chunk_ids: List[str] = []
        self.current_size = 0
        self._is_open = True
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources."""
        self.clear()
        self._is_open = False
        return False
    
    def add(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> None:
        """Add document chunks with their embeddings to store.
        
        Changed: Dynamic allocation to reduce memory usage from 58MB to near-zero when empty.
        """
        # Input validation
        if chunks is None:
            raise ValidationError("Chunks cannot be None", field="chunks")
        
        if embeddings is None:
            raise ValidationError("Embeddings cannot be None", field="embeddings")
        
        if not isinstance(chunks, list):
            raise ValidationError("Chunks must be a list", field="chunks")
        
        if not isinstance(embeddings, list):
            raise ValidationError("Embeddings must be a list", field="embeddings")
        
        if len(chunks) != len(embeddings):
            raise ValidationError(
                "Number of chunks must match number of embeddings",
                field="chunks"
            )
        
        if not chunks:
            return
        
        # Check if adding would exceed max capacity
        if self.current_size + len(chunks) > self.max_chunks:
            raise MemoryError(
                f"Cannot add {len(chunks)} chunks: would exceed max capacity of {self.max_chunks} chunks"
            )
        
        # Validate embedding dimensions
        for emb in embeddings:
            if len(emb) != self.dimension:
                raise ValidationError(
                    f"Embedding dimension mismatch: expected {self.dimension}, got {len(emb)}",
                    field="embeddings"
                )
        
        # Add chunks
        for chunk in chunks:
            self.chunks[chunk.chunk_id] = chunk
        
        # Changed: Dynamic allocation - resize array instead of pre-allocation
        new_embeddings = np.array(embeddings, dtype=np.float32)
        
        # Resize embeddings array dynamically
        if self.current_size == 0:
            # First addition
            self.embeddings = new_embeddings
        else:
            # Append to existing array
            self.embeddings = np.vstack([self.embeddings, new_embeddings])
        
        # Track chunk IDs
        self.chunk_ids.extend([chunk.chunk_id for chunk in chunks])
        self.current_size += len(chunks)
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResult]:
        """Search for similar chunks using cosine similarity."""
        # Input validation
        if query_embedding is None:
            raise ValidationError("Query embedding cannot be None", field="query_embedding")
        
        if not isinstance(query_embedding, list):
            raise ValidationError("Query embedding must be a list", field="query_embedding")
        
        if len(query_embedding) != self.dimension:
            raise ValidationError(
                f"Query embedding dimension mismatch: expected {self.dimension}, got {len(query_embedding)}",
                field="query_embedding"
            )
        
        if top_k <= 0:
            raise ValidationError("top_k must be positive", field="top_k")
        
        if self.current_size == 0:
            return []
        
        # Calculate cosine similarity (only use current_size portion)
        query_vector = np.array(query_embedding, dtype=np.float32)
        query_norm = np.linalg.norm(query_vector)
        
        if query_norm == 0:
            return []
        
        # Normalize embeddings (only use current_size portion)
        active_embeddings = self.embeddings[:self.current_size]
        embeddings_norm = np.linalg.norm(active_embeddings, axis=1)
        embeddings_norm[embeddings_norm == 0] = 1  # Avoid division by zero
        
        similarities = np.dot(active_embeddings, query_vector) / (embeddings_norm * query_norm)
        
        # Get top-k indices
        top_k = min(top_k, self.current_size)
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Build results
        results = []
        for idx in top_indices:
            chunk_id = self.chunk_ids[idx]
            chunk = self.chunks[chunk_id]
            score = float(similarities[idx])
            
            result = SearchResult(
                chunk=chunk,
                score=score,
                metadata={
                    "chunk_id": chunk_id,
                    "similarity": score,
                }
            )
            results.append(result)
        
        return results
    
    def delete(self, chunk_id: str) -> bool:
        """Delete a chunk by ID.
        
        Changed: Updated to work with dynamic allocation.
        """
        if chunk_id not in self.chunks:
            return False
        
        # Find index of chunk
        try:
            idx = self.chunk_ids.index(chunk_id)
        except ValueError:
            return False
        
        # Remove chunk
        del self.chunks[chunk_id]
        
        # Changed: Dynamic deletion - resize array
        self.embeddings = np.delete(self.embeddings, idx, axis=0)
        
        # Remove chunk ID
        self.chunk_ids.pop(idx)
        self.current_size -= 1
        
        return True
    
    def clear(self) -> None:
        """Clear all chunks from store.
        
        Changed: Dynamic allocation - reset to empty array instead of pre-allocated.
        """
        self.chunks.clear()
        self.embeddings = np.zeros((0, self.dimension), dtype=np.float32)
        self.chunk_ids.clear()
        self.current_size = 0
    
    def count(self) -> int:
        """Get the number of chunks in the store."""
        return self.current_size
    
    def save(self, file_path: str) -> None:
        """Save the vector store to disk."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save chunks as JSON
        chunks_data = {
            chunk_id: {
                "text": chunk.text,
                "chunk_id": chunk.chunk_id,
                "start_index": chunk.start_index,
                "end_index": chunk.end_index,
                "metadata": chunk.metadata,
            }
            for chunk_id, chunk in self.chunks.items()
        }
        
        # Save embeddings as numpy array (only active portion)
        active_embeddings = self.embeddings[:self.current_size]
        np.savez(
            path.with_suffix(".npz"),
            embeddings=active_embeddings,
            chunk_ids=np.array(self.chunk_ids, dtype=object),
            current_size=self.current_size
        )
        
        # Save chunks metadata
        with open(path.with_suffix(".json"), "w") as f:
            json.dump(chunks_data, f, indent=2)
    
    def load(self, file_path: str) -> None:
        """Load the vector store from disk.
        
        Changed: Dynamic allocation - load into dynamically sized array.
        """
        path = Path(file_path)
        
        # Load embeddings
        npz_data = np.load(path.with_suffix(".npz"), allow_pickle=True)
        loaded_embeddings = npz_data["embeddings"]
        self.chunk_ids = npz_data["chunk_ids"].tolist()
        
        # Try to load current_size if available (for newer saves)
        if "current_size" in npz_data:
            self.current_size = int(npz_data["current_size"])
        else:
            self.current_size = len(self.chunk_ids)
        
        # Load chunks
        with open(path.with_suffix(".json"), "r") as f:
            chunks_data = json.load(f)
        
        self.chunks = {
            chunk_id: DocumentChunk(
                text=data["text"],
                chunk_id=data["chunk_id"],
                start_index=data["start_index"],
                end_index=data["end_index"],
                metadata=data["metadata"],
            )
            for chunk_id, data in chunks_data.items()
        }
        
        # Changed: Update dimension and use dynamic allocation
        if loaded_embeddings.shape[0] > 0:
            self.dimension = loaded_embeddings.shape[1]
            # Use loaded data directly instead of pre-allocating
            self.embeddings = loaded_embeddings
        else:
            # Empty store
            self.embeddings = np.zeros((0, self.dimension), dtype=np.float32)
