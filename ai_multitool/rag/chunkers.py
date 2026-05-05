"""Document chunking strategies for splitting text into manageable pieces."""

from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
import re


@dataclass
class DocumentChunk:
    """A chunk of text with metadata."""
    text: str
    chunk_id: str
    start_index: int
    end_index: int
    metadata: dict


class DocumentChunker(ABC):
    """Abstract base class for document chunkers."""
    
    @abstractmethod
    def chunk(self, text: str, metadata: Optional[dict] = None) -> List[DocumentChunk]:
        """Split text into chunks."""
        pass


class RecursiveCharacterChunker(DocumentChunker):
    """Recursive character-based chunker that respects sentence boundaries."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None
    ):
        """Initialize the recursive character chunker.
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            separators: List of separators to try, in order of preference
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be non-negative and less than chunk_size")
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        if separators is None:
            self.separators = ["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " ", ""]
        else:
            self.separators = separators
    
    def chunk(self, text: str, metadata: Optional[dict] = None) -> List[DocumentChunk]:
        """Split text into chunks using recursive character splitting."""
        if not text:
            return []
        
        if metadata is None:
            metadata = {}
        
        chunks = []
        current_position = 0
        
        while current_position < len(text):
            # Determine the end position for this chunk
            end_position = min(current_position + self.chunk_size, len(text))
            
            # If we're not at the end, try to split at a separator
            if end_position < len(text):
                # Try each separator to find a good split point
                split_position = None
                for separator in self.separators:
                    # Find the last occurrence of this separator before end_position
                    sep_pos = text.rfind(separator, current_position, end_position)
                    if sep_pos != -1:
                        # Include the separator in the chunk
                        split_position = sep_pos + len(separator)
                        break
                
                if split_position:
                    end_position = split_position
            
            # Extract the chunk
            chunk_text = text[current_position:end_position].strip()
            
            if chunk_text:  # Only add non-empty chunks
                chunk = DocumentChunk(
                    text=chunk_text,
                    chunk_id=f"chunk_{len(chunks)}",
                    start_index=current_position,
                    end_index=end_position,
                    metadata={
                        **metadata,
                        "chunk_index": len(chunks),
                        "chunk_size": len(chunk_text),
                    }
                )
                chunks.append(chunk)
            
            # Move to next position with overlap
            current_position = end_position - self.chunk_overlap
            if current_position >= len(text):
                break
        
        return chunks


class FixedSizeChunker(DocumentChunker):
    """Simple fixed-size chunker without considering boundaries."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 0):
        """Initialize the fixed-size chunker.
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be non-negative and less than chunk_size")
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk(self, text: str, metadata: Optional[dict] = None) -> List[DocumentChunk]:
        """Split text into fixed-size chunks."""
        if not text:
            return []
        
        if metadata is None:
            metadata = {}
        
        chunks = []
        current_position = 0
        
        while current_position < len(text):
            end_position = min(current_position + self.chunk_size, len(text))
            chunk_text = text[current_position:end_position]
            
            chunk = DocumentChunk(
                text=chunk_text,
                chunk_id=f"chunk_{len(chunks)}",
                start_index=current_position,
                end_index=end_position,
                metadata={
                    **metadata,
                    "chunk_index": len(chunks),
                    "chunk_size": len(chunk_text),
                }
            )
            chunks.append(chunk)
            
            current_position = end_position - self.chunk_overlap
            if current_position >= len(text):
                break
        
        return chunks


class SentenceChunker(DocumentChunker):
    """Chunker that splits by sentences."""
    
    def __init__(self, max_sentences: int = 5, overlap_sentences: int = 1):
        """Initialize the sentence chunker.
        
        Args:
            max_sentences: Maximum number of sentences per chunk
            overlap_sentences: Number of sentences to overlap between chunks
        """
        if max_sentences <= 0:
            raise ValueError("max_sentences must be positive")
        
        if overlap_sentences < 0 or overlap_sentences >= max_sentences:
            raise ValueError("overlap_sentences must be non-negative and less than max_sentences")
        
        self.max_sentences = max_sentences
        self.overlap_sentences = overlap_sentences
    
    def chunk(self, text: str, metadata: Optional[dict] = None) -> List[DocumentChunk]:
        """Split text into sentence-based chunks."""
        if not text:
            return []
        
        if metadata is None:
            metadata = {}
        
        # Split into sentences (simple approach)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return []
        
        chunks = []
        current_index = 0
        
        while current_index < len(sentences):
            end_index = min(current_index + self.max_sentences, len(sentences))
            chunk_sentences = sentences[current_index:end_index]
            chunk_text = " ".join(chunk_sentences)
            
            # Calculate start and end positions in original text
            start_char = text.find(chunk_sentences[0])
            end_char = text.find(chunk_sentences[-1]) + len(chunk_sentences[-1])
            
            chunk = DocumentChunk(
                text=chunk_text,
                chunk_id=f"chunk_{len(chunks)}",
                start_index=start_char,
                end_index=end_char,
                metadata={
                    **metadata,
                    "chunk_index": len(chunks),
                    "sentence_count": len(chunk_sentences),
                }
            )
            chunks.append(chunk)
            
            current_index = end_index - self.overlap_sentences
            if current_index >= len(sentences):
                break
        
        return chunks
