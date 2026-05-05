"""Retriever for searching indexed documents."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from dataclasses import dataclass

from ai_multitool.rag.embeddings import EmbeddingModel
from ai_multitool.rag.vector_store import VectorStore, SearchResult
from ai_multitool.core.exceptions import ValidationError
from ai_multitool.utils.validation import is_empty_string


@dataclass
class RetrievalResult:
    """Result of a retrieval operation."""
    results: List[SearchResult]
    query: str
    total_retrieved: int


class Retriever(ABC):
    """Abstract base class for retrievers."""
    
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> RetrievalResult:
        """Retrieve relevant chunks for a query."""
        pass


class SimilarityRetriever(Retriever):
    """Retriever that uses similarity search."""
    
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_model: Optional[EmbeddingModel] = None
    ):
        """Initialize the similarity retriever.
        
        Args:
            vector_store: Vector store to search
            embedding_model: Model for generating query embeddings
        """
        self.vector_store = vector_store
        self.embedding_model = embedding_model
    
    def retrieve(self, query: str, top_k: int = 5) -> RetrievalResult:
        """Retrieve relevant chunks using similarity search."""
        if is_empty_string(query):
            raise ValidationError("Query cannot be empty", field="query")
        
        if top_k <= 0:
            raise ValidationError("top_k must be positive", field="top_k")
        
        # Generate query embedding
        if self.embedding_model:
            query_embedding = self.embedding_model.embed(query)
        else:
            # If no embedding model, use zero vector (for testing)
            dimension = self.vector_store.dimension if hasattr(self.vector_store, 'dimension') else 1536
            query_embedding = [0.0] * dimension
        
        # Search vector store
        results = self.vector_store.search(query_embedding, top_k=top_k)
        
        return RetrievalResult(
            results=results,
            query=query,
            total_retrieved=len(results)
        )
    
    def retrieve_with_filter(
        self,
        query: str,
        filter_metadata: Dict[str, str],
        top_k: int = 5
    ) -> RetrievalResult:
        """Retrieve with metadata filtering."""
        # First get more results than needed
        retrieval = self.retrieve(query, top_k=top_k * 3)
        
        # Filter by metadata
        filtered_results = []
        for result in retrieval.results:
            match = True
            for key, value in filter_metadata.items():
                if result.chunk.metadata.get(key) != value:
                    match = False
                    break
            
            if match:
                filtered_results.append(result)
            
            if len(filtered_results) >= top_k:
                break
        
        return RetrievalResult(
            results=filtered_results,
            query=query,
            total_retrieved=len(filtered_results)
        )
    
    def format_results(self, retrieval_result: RetrievalResult) -> str:
        """Format retrieval results as a string."""
        if not retrieval_result.results:
            return f"No results found for query: {retrieval_result.query}"
        
        lines = [
            f"Query: {retrieval_result.query}",
            f"Retrieved {retrieval_result.total_retrieved} results:\n"
        ]
        
        for i, result in enumerate(retrieval_result.results, 1):
            lines.append(f"Result {i} (Score: {result.score:.4f}):")
            lines.append(f"  {result.chunk.text[:200]}...")
            if result.chunk.metadata:
                lines.append(f"  Metadata: {result.chunk.metadata}")
            lines.append("")
        
        return "\n".join(lines)
