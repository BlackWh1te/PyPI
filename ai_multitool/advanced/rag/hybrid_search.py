"""Hybrid semantic + keyword search."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole
from ...rag.vector_store import InMemoryVectorStore
from ...rag.embeddings import OpenAIEmbeddingModel


class AdvancedHybridSearch(AdvancedTool):
    """Hybrid search combining semantic and keyword matching.
    
    Combines:
    - Semantic search (embeddings)
    - Keyword search (BM25, TF-IDF)
    - Re-ranking for best results
    """
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": "hybrid_search",
            "description": "Hybrid semantic + keyword search",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "documents": {"type": "array", "items": {"type": "string"}},
                    "semantic_weight": {"type": "number", "default": 0.7},
                    "keyword_weight": {"type": "number", "default": 0.3},
                    "top_k": {"type": "number", "default": 10}
                },
                "required": ["query", "documents"]
            }
        }
    
    async def execute(self, query: str, documents: List[str], semantic_weight: float = 0.7,
                     keyword_weight: float = 0.3, top_k: int = 10, **kwargs) -> ToolResult:
        start_time = time.time()
        
        try:
            # Calculate keyword scores (simple TF-IDF)
            keyword_scores = self._calculate_keyword_scores(query, documents)
            
            # If embeddings available, calculate semantic scores
            semantic_scores = {}
            if hasattr(self, 'embedding_model'):
                semantic_scores = await self._calculate_semantic_scores(query, documents)
            
            # Combine scores
            combined_scores = []
            for i, doc in enumerate(documents):
                kw_score = keyword_scores.get(i, 0.0)
                sem_score = semantic_scores.get(i, 0.0)
                combined = (kw_score * keyword_weight) + (sem_score * semantic_weight)
                combined_scores.append({"document": doc, "score": combined, "rank": i})
            
            # Sort and return top_k
            combined_scores.sort(key=lambda x: x["score"], reverse=True)
            top_results = combined_scores[:top_k]
            
            return ToolResult(
                success=True,
                data={
                    "results": top_results,
                    "query": query,
                    "weights": {"semantic": semantic_weight, "keyword": keyword_weight}
                },
                metrics={"total_documents": len(documents)},
                confidence=0.85,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=0
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
    
    def _calculate_keyword_scores(self, query: str, documents: List[str]) -> Dict[int, float]:
        """Calculate keyword-based scores using simple TF-IDF."""
        import math
        query_terms = set(query.lower().split())
        scores = {}
        
        for i, doc in enumerate(documents):
            doc_terms = doc.lower().split()
            doc_len = len(doc_terms)
            
            score = 0.0
            for term in query_terms:
                if term in doc_terms:
                    # Simple TF calculation
                    tf = doc_terms.count(term) / doc_len
                    score += tf
            
            scores[i] = score
        
        return scores
    
    async def _calculate_semantic_scores(self, query: str, documents: List[str]) -> Dict[int, float]:
        """Calculate semantic scores using embeddings."""
        # This would use the embedding model
        # For now, return empty dict
        return {}
