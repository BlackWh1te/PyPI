"""Document indexer for creating and managing document indices."""

from typing import List, Optional, Dict
from pathlib import Path
from dataclasses import dataclass

from ai_multitool.rag.embeddings import EmbeddingModel
from ai_multitool.rag.chunkers import DocumentChunker, RecursiveCharacterChunker
from ai_multitool.rag.vector_store import VectorStore, InMemoryVectorStore
from ai_multitool.core.exceptions import ValidationError
from ai_multitool.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class Document:
    """A document with text and metadata."""
    text: str
    doc_id: str
    metadata: dict


class DocumentIndexer:
    """Index documents for retrieval."""
    
    def __init__(
        self,
        embedding_model: Optional[EmbeddingModel] = None,
        chunker: Optional[DocumentChunker] = None,
        vector_store: Optional[VectorStore] = None
    ):
        """Initialize the document indexer.
        
        Args:
            embedding_model: Model for generating embeddings
            chunker: Strategy for chunking documents
            vector_store: Store for embeddings and chunks
        """
        self.embedding_model = embedding_model
        self.chunker = chunker or RecursiveCharacterChunker()
        self.vector_store = vector_store
        
        # If vector_store is provided, use its dimension
        if self.vector_store and isinstance(self.vector_store, InMemoryVectorStore):
            self.dimension = self.vector_store.dimension
        elif self.embedding_model:
            self.dimension = self.embedding_model.get_dimension()
        else:
            self.dimension = 1536  # Default
        
        # Create vector store if not provided
        if self.vector_store is None:
            self.vector_store = InMemoryVectorStore(dimension=self.dimension)
    
    def add_document(self, document: Document) -> None:
        """Add a single document to the index."""
        if not document.text:
            raise ValidationError("Document text cannot be empty", field="text")
        
        if not document.doc_id:
            raise ValidationError("Document ID cannot be empty", field="doc_id")
        
        # Chunk the document
        chunks = self.chunker.chunk(document.text, document.metadata)
        
        # Add doc_id to chunk metadata
        for chunk in chunks:
            chunk.metadata["doc_id"] = document.doc_id
        
        # Generate embeddings
        if self.embedding_model:
            chunk_texts = [chunk.text for chunk in chunks]
            embeddings = self.embedding_model.embed_batch(chunk_texts)
        else:
            # If no embedding model, use dummy embeddings (for testing)
            embeddings = [[0.0] * self.dimension for _ in chunks]
        
        # Add to vector store
        self.vector_store.add(chunks, embeddings)
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add multiple documents to the index."""
        if not documents:
            return
        
        all_chunks = []
        all_embeddings = []
        
        for document in documents:
            if not document.text:
                continue
            
            # Chunk the document
            chunks = self.chunker.chunk(document.text, document.metadata)
            
            # Add doc_id to chunk metadata
            for chunk in chunks:
                chunk.metadata["doc_id"] = document.doc_id
            
            all_chunks.extend(chunks)
        
        # Generate embeddings for all chunks
        if self.embedding_model and all_chunks:
            chunk_texts = [chunk.text for chunk in all_chunks]
            all_embeddings = self.embedding_model.embed_batch(chunk_texts)
        else:
            all_embeddings = [[0.0] * self.dimension for _ in all_chunks]
        
        # Add to vector store
        self.vector_store.add(all_chunks, all_embeddings)
    
    def index_directory(
        self,
        directory: str,
        pattern: str = "*.md",
        metadata: Optional[dict] = None,
        max_files: int = 1000,
        max_total_size: int = 100_000_000,  # 100MB
        batch_size: int = 50
    ) -> int:
        """Index all files in a directory with memory limits.
        
        Args:
            directory: Path to directory
            pattern: File pattern to match (e.g., "*.md", "*.txt")
            metadata: Additional metadata to add to all documents
            max_files: Maximum number of files to index (default: 1000)
            max_total_size: Maximum total size in bytes (default: 100MB)
            batch_size: Number of documents to process at once (default: 50)
            
        Returns:
            Number of documents indexed
        """
        logger.info(f"Indexing directory: {directory} with pattern: {pattern}")
        logger.info(f"Memory limits: max_files={max_files}, max_total_size={max_total_size/1024/1024:.1f}MB")
        from ai_multitool.utils.file_utils import read_file
        
        dir_path = Path(directory)
        if not dir_path.exists():
            raise ValidationError(f"Directory not found: {directory}", field="directory")
        
        documents = []
        total_size = 0
        file_count = 0
        
        for file_path in dir_path.rglob(pattern):
            if file_path.is_file():
                # Check file count limit
                if file_count >= max_files:
                    logger.warning(f"Reached max_files limit ({max_files}), skipping remaining files")
                    break
                
                # Check total size limit
                file_size = file_path.stat().st_size
                if total_size + file_size > max_total_size:
                    logger.warning(f"Reached max_total_size limit ({max_total_size/1024/1024:.1f}MB), skipping remaining files")
                    break
                
                try:
                    text = read_file(str(file_path))
                    doc_metadata = {
                        "file_path": str(file_path),
                        "file_name": file_path.name,
                        "file_extension": file_path.suffix,
                        "file_size": file_size,
                    }
                    if metadata:
                        doc_metadata.update(metadata)
                    
                    document = Document(
                        text=text,
                        doc_id=str(file_path),
                        metadata=doc_metadata
                    )
                    documents.append(document)
                    total_size += file_size
                    file_count += 1
                    
                    # Process in batches to reduce memory usage
                    if len(documents) >= batch_size:
                        self.add_documents(documents)
                        documents = []  # Clear to free memory
                        logger.info(f"Processed batch of {batch_size} documents, total indexed: {file_count}")
                        
                except Exception as e:
                    logger.warning(f"Skipping file {file_path}: {e}")
                    continue
        
        # Process remaining documents in final batch
        if documents:
            self.add_documents(documents)
        
        logger.info(f"Indexing complete: {file_count} documents indexed, total size: {total_size/1024/1024:.1f}MB")
        return file_count
    
    def get_stats(self) -> dict:
        """Get statistics about the index."""
        return {
            "total_chunks": self.vector_store.count(),
            "dimension": self.dimension,
            "embedding_model": type(self.embedding_model).__name__ if self.embedding_model else "None",
            "chunker": type(self.chunker).__name__,
            "vector_store": type(self.vector_store).__name__,
        }
    
    def save(self, file_path: str) -> None:
        """Save the index to disk."""
        if isinstance(self.vector_store, InMemoryVectorStore):
            self.vector_store.save(file_path)
        else:
            raise NotImplementedError("Saving is only supported for InMemoryVectorStore")
    
    def load(self, file_path: str) -> None:
        """Load the index from disk."""
        if isinstance(self.vector_store, InMemoryVectorStore):
            self.vector_store.load(file_path)
        else:
            raise NotImplementedError("Loading is only supported for InMemoryVectorStore")
    
    def clear(self) -> None:
        """Clear all documents from the index."""
        self.vector_store.clear()
