"""Vector store for storing and searching document embeddings."""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
import json
from pathlib import Path
import numpy as np

from ai_multitool.rag.chunkers import DocumentChunk
from ai_multitool.core.exceptions import ValidationError


@dataclass
class SearchResult:
    """A search result with similarity score."""
    chunk: DocumentChunk
    score: float
    metadata: dict


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
    
    def __init__(self, dimension: int = 1536):
        """Initialize the in-memory vector store.
        
        Args:
            dimension: Dimension of the embedding vectors
        """
        if dimension <= 0:
            raise ValueError("dimension must be positive")
        
        self.dimension = dimension
        self.chunks: Dict[str, DocumentChunk] = {}
        self.embeddings: np.ndarray = np.zeros((0, dimension), dtype=np.float32)
        self.chunk_ids: List[str] = []
    
    def add(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> None:
        """Add document chunks with their embeddings to the store."""
        if len(chunks) != len(embeddings):
            raise ValidationError(
                "Number of chunks must match number of embeddings",
                field="chunks"
            )
        
        if not chunks:
            return
        
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
        
        # Add embeddings
        new_embeddings = np.array(embeddings, dtype=np.float32)
        self.embeddings = np.vstack([self.embeddings, new_embeddings])
        
        # Track chunk IDs
        self.chunk_ids.extend([chunk.chunk_id for chunk in chunks])
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResult]:
        """Search for similar chunks using cosine similarity."""
        if len(query_embedding) != self.dimension:
            raise ValidationError(
                f"Query embedding dimension mismatch: expected {self.dimension}, got {len(query_embedding)}",
                field="query_embedding"
            )
        
        if top_k <= 0:
            raise ValidationError("top_k must be positive", field="top_k")
        
        if self.count() == 0:
            return []
        
        # Calculate cosine similarity
        query_vector = np.array(query_embedding, dtype=np.float32)
        query_norm = np.linalg.norm(query_vector)
        
        if query_norm == 0:
            return []
        
        # Normalize embeddings
        embeddings_norm = np.linalg.norm(self.embeddings, axis=1)
        embeddings_norm[embeddings_norm == 0] = 1  # Avoid division by zero
        
        similarities = np.dot(self.embeddings, query_vector) / (embeddings_norm * query_norm)
        
        # Get top-k indices
        top_k = min(top_k, len(similarities))
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
        """Delete a chunk by ID."""
        if chunk_id not in self.chunks:
            return False
        
        # Find index of chunk
        try:
            idx = self.chunk_ids.index(chunk_id)
        except ValueError:
            return False
        
        # Remove chunk
        del self.chunks[chunk_id]
        
        # Remove embedding
        self.embeddings = np.delete(self.embeddings, idx, axis=0)
        
        # Remove chunk ID
        self.chunk_ids.pop(idx)
        
        return True
    
    def clear(self) -> None:
        """Clear all chunks from the store."""
        self.chunks.clear()
        self.embeddings = np.zeros((0, self.dimension), dtype=np.float32)
        self.chunk_ids.clear()
    
    def count(self) -> int:
        """Get the number of chunks in the store."""
        return len(self.chunks)
    
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
        
        # Save embeddings as numpy array
        np.savez(
            path.with_suffix(".npz"),
            embeddings=self.embeddings,
            chunk_ids=np.array(self.chunk_ids, dtype=object)
        )
        
        # Save chunks metadata
        with open(path.with_suffix(".json"), "w") as f:
            json.dump(chunks_data, f, indent=2)
    
    def load(self, file_path: str) -> None:
        """Load the vector store from disk."""
        path = Path(file_path)
        
        # Load embeddings
        npz_data = np.load(path.with_suffix(".npz"), allow_pickle=True)
        self.embeddings = npz_data["embeddings"]
        self.chunk_ids = npz_data["chunk_ids"].tolist()
        
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
        
        # Update dimension
        if self.embeddings.shape[0] > 0:
            self.dimension = self.embeddings.shape[1]
