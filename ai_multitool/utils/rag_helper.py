"""Helper functions for RAG integration with CLI commands."""

from pathlib import Path
from typing import Optional, List

from ai_multitool.rag.embeddings import OpenAIEmbeddings
from ai_multitool.rag.retriever import SimilarityRetriever
from ai_multitool.rag.vector_store import InMemoryVectorStore
from ai_multitool.config.settings import get_settings
from ai_multitool.core.exceptions import ValidationError


def get_rag_context(
    query: str,
    index_path: Optional[str] = None,
    top_k: int = 3,
    provider: str = "openai"
) -> str:
    """Retrieve relevant context from RAG index.
    
    Args:
        query: Search query
        index_path: Path to index file (default: ~/.ai-multitool/index)
        top_k: Number of results to retrieve
        provider: Embedding provider (openai)
        
    Returns:
        Formatted context string with retrieved chunks
    """
    # Determine index path
    if index_path is None:
        index_path = str(Path.home() / ".ai-multitool" / "index")
    
    # Check if index exists
    if not Path(index_path).with_suffix(".json").exists():
        return ""
    
    try:
        settings = get_settings()
        
        # Get API key for embeddings
        if provider == "openai":
            api_key = settings.get_openai_key()
            if not api_key:
                return ""
            
            embedding_model = OpenAIEmbeddings(api_key=api_key)
        else:
            return ""
        
        # Load vector store
        vector_store = InMemoryVectorStore(dimension=1536)
        vector_store.load(index_path)
        
        # Initialize retriever
        retriever = SimilarityRetriever(vector_store=vector_store, embedding_model=embedding_model)
        
        # Search
        result = retriever.retrieve(query, top_k=top_k)
        
        if not result.results:
            return ""
        
        # Format context
        context_parts = [f"Relevant context from {len(result.results)} documents:"]
        
        for i, search_result in enumerate(result.results, 1):
            chunk = search_result.chunk
            context_parts.append(f"\n--- Document {i} (Score: {search_result.score:.4f}) ---")
            context_parts.append(chunk.text)
            
            # Add metadata if available
            if chunk.metadata:
                meta_parts = []
                if "file_path" in chunk.metadata:
                    meta_parts.append(f"File: {chunk.metadata['file_path']}")
                if "doc_id" in chunk.metadata:
                    meta_parts.append(f"ID: {chunk.metadata['doc_id']}")
                if meta_parts:
                    context_parts.append(f"[Metadata: {', '.join(meta_parts)}]")
        
        return "\n".join(context_parts)
    
    except Exception:
        # If RAG fails, return empty string and continue without context
        return ""


def check_rag_available(index_path: Optional[str] = None) -> bool:
    """Check if RAG index is available.
    
    Args:
        index_path: Path to index file (default: ~/.ai-multitool/index)
        
    Returns:
        True if index exists and can be loaded
    """
    if index_path is None:
        index_path = str(Path.home() / ".ai-multitool" / "index")
    
    return Path(index_path).with_suffix(".json").exists()


def get_rag_stats(index_path: Optional[str] = None) -> dict:
    """Get statistics about RAG index.
    
    Args:
        index_path: Path to index file (default: ~/.ai-multitool/index)
        
    Returns:
        Dictionary with index statistics
    """
    if index_path is None:
        index_path = str(Path.home() / ".ai-multitool" / "index")
    
    if not Path(index_path).with_suffix(".json").exists():
        return {"available": False}
    
    try:
        vector_store = InMemoryVectorStore(dimension=1536)
        vector_store.load(index_path)
        
        return {
            "available": True,
            "total_chunks": vector_store.count(),
            "dimension": vector_store.dimension,
        }
    except Exception:
        return {"available": False}
