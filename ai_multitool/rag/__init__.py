"""RAG (Retrieval-Augmented Generation) module for document indexing and search."""

from ai_multitool.rag.embeddings import EmbeddingModel, OpenAIEmbeddings
from ai_multitool.rag.chunkers import DocumentChunker, RecursiveCharacterChunker
from ai_multitool.rag.vector_store import VectorStore, InMemoryVectorStore
from ai_multitool.rag.indexer import DocumentIndexer
from ai_multitool.rag.retriever import Retriever, SimilarityRetriever

__all__ = [
    'EmbeddingModel',
    'OpenAIEmbeddings',
    'DocumentChunker',
    'RecursiveCharacterChunker',
    'VectorStore',
    'InMemoryVectorStore',
    'DocumentIndexer',
    'Retriever',
    'SimilarityRetriever',
]
