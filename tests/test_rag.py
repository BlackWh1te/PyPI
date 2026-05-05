"""Tests for RAG (Retrieval-Augmented Generation) functionality."""

import pytest
from unittest.mock import Mock, patch
import numpy as np
from ai_multitool import (
    Document,
    DocumentIndexer,
    EmbeddingModel,
    OpenAIEmbeddings,
    FakeEmbeddings,
    VectorStore,
    InMemoryVectorStore,
    SimilarityRetriever,
    DocumentChunker,
    RecursiveCharacterChunker,
    FixedSizeChunker,
    SentenceChunker,
)


class TestDocument:
    """Test Document model."""
    
    def test_document_creation(self):
        """Test creating a document."""
        doc = Document(
            text="Sample document text",
            doc_id="doc1",
            metadata={"source": "test.txt"}
        )
        assert doc.text == "Sample document text"
        assert doc.doc_id == "doc1"
        assert doc.metadata["source"] == "test.txt"
    
    def test_document_without_metadata(self):
        """Test creating a document without metadata."""
        doc = Document(text="Sample text", doc_id="doc1")
        assert doc.metadata == {}


class TestFakeEmbeddings:
    """Test fake embeddings for testing."""
    
    def test_fake_embeddings_dimension(self):
        """Test fake embeddings return correct dimension."""
        embeddings = FakeEmbeddings(dimension=768)
        vector = embeddings.embed("Sample text")
        assert len(vector) == 768
    
    def test_fake_embeddings_consistency(self):
        """Test that same text produces different embeddings (fake)."""
        embeddings = FakeEmbeddings(dimension=768)
        vector1 = embeddings.embed("Same text")
        vector2 = embeddings.embed("Same text")
        # Fake embeddings should be different (random)
        assert vector1 != vector2


class TestInMemoryVectorStore:
    """Test in-memory vector store."""
    
    def test_vector_store_initialization(self):
        """Test vector store initialization."""
        store = InMemoryVectorStore(dimension=768)
        assert store.dimension == 768
        assert len(store.vectors) == 0
    
    def test_vector_store_add_vector(self):
        """Test adding a vector to the store."""
        store = InMemoryVectorStore(dimension=3)
        vector = [0.1, 0.2, 0.3]
        doc = Document(text="Test", doc_id="doc1")
        
        store.add_vector(vector, doc)
        assert len(store.vectors) == 1
    
    def test_vector_store_search(self):
        """Test searching for similar vectors."""
        store = InMemoryVectorStore(dimension=3)
        
        # Add some vectors
        docs = [
            Document(text="Python programming", doc_id="doc1"),
            Document(text="JavaScript tutorial", doc_id="doc2"),
            Document(text="Machine learning", doc_id="doc3"),
        ]
        
        vectors = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9],
        ]
        
        for doc, vector in zip(docs, vectors):
            store.add_vector(vector, doc)
        
        # Search for similar vector
        query_vector = [0.15, 0.25, 0.35]
        results = store.search(query_vector, k=2)
        
        assert len(results) == 2
        assert results[0][0].doc_id == "doc1"  # Most similar
    
    def test_max_chunks_limit(self):
        """Test that vector store respects max_chunks limit."""
        store = InMemoryVectorStore(dimension=3, max_chunks=5)
        
        # Try to add more chunks than the limit
        chunks = []
        embeddings = []
        for i in range(10):
            from ai_multitool import DocumentChunk
            chunk = DocumentChunk(
                text=f"chunk_{i}",
                chunk_id=f"chunk_{i}",
                start_index=0,
                end_index=10,
                metadata={}
            )
            chunks.append(chunk)
            embeddings.append([0.1, 0.2, 0.3])
        
        # Should raise MemoryError when exceeding limit
        try:
            store.add(chunks, embeddings)
            assert False, "Should have raised MemoryError"
        except MemoryError as e:
            assert "max capacity" in str(e)
    
    def test_custom_max_chunks(self):
        """Test custom max_chunks value."""
        store = InMemoryVectorStore(dimension=3, max_chunks=3)
        
        assert store.max_chunks == 3
        assert store.current_size == 0
    
    def test_context_manager(self):
        """Test vector store as context manager."""
        from ai_multitool import DocumentChunk
        store = InMemoryVectorStore(dimension=3, max_chunks=10)
        
        # Add some chunks
        chunks = [
            DocumentChunk(text="chunk1", chunk_id="chunk1", start_index=0, end_index=10, metadata={}),
            DocumentChunk(text="chunk2", chunk_id="chunk2", start_index=0, end_index=10, metadata={})
        ]
        embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        store.add(chunks, embeddings)
        
        assert store.count() == 2
        
        # Use as context manager
        with store:
            assert store._is_open == True
        
        # After context, should be cleared
        assert store.count() == 0
        assert store._is_open == False


class TestDocumentChunker:
    """Test document chunking."""
    
    def test_recursive_character_chunker(self):
        """Test recursive character chunker."""
        chunker = RecursiveCharacterChunker(chunk_size=100, chunk_overlap=20)
        text = "A" * 250  # 250 characters
        
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 100 for chunk in chunks)
    
    def test_fixed_size_chunker(self):
        """Test fixed size chunker."""
        chunker = FixedSizeChunker(chunk_size=50, chunk_overlap=10)
        text = "A" * 150  # 150 characters
        
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 3  # 150 / 50 = 3 chunks
        assert all(len(chunk) == 50 for chunk in chunks)
    
    def test_sentence_chunker(self):
        """Test sentence chunker."""
        chunker = SentenceChunker()
        text = "This is sentence one. This is sentence two. This is sentence three."
        
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 3
        assert "sentence one" in chunks[0]
        assert "sentence two" in chunks[1]
        assert "sentence three" in chunks[2]


class TestDocumentIndexer:
    """Test document indexer."""
    
    def test_indexer_initialization(self, mock_embedding_model, mock_vector_store):
        """Test indexer initialization."""
        indexer = DocumentIndexer(
            embedding_model=mock_embedding_model,
            vector_store=mock_vector_store
        )
        assert indexer.embedding_model == mock_embedding_model
        assert indexer.vector_store == mock_vector_store
    
    def test_add_document(self, mock_embedding_model, mock_vector_store, sample_document):
        """Test adding a document to the index."""
        indexer = DocumentIndexer(
            embedding_model=mock_embedding_model,
            vector_store=mock_vector_store
        )
        
        indexer.add_document(sample_document)
        
        # Verify embedding was called
        mock_embedding_model.embed.assert_called_once()
        # Verify vector was added to store
        mock_vector_store.add_vector.assert_called_once()
    
    def test_add_documents_batch(self, mock_embedding_model, mock_vector_store):
        """Test adding multiple documents at once."""
        indexer = DocumentIndexer(
            embedding_model=mock_embedding_model,
            vector_store=mock_vector_store
        )
        
        docs = [
            Document(text="Doc 1", doc_id="doc1"),
            Document(text="Doc 2", doc_id="doc2"),
            Document(text="Doc 3", doc_id="doc3"),
        ]
        
        indexer.add_documents(docs)
        
        # Verify all documents were processed
        assert mock_embedding_model.embed.call_count == 3
        assert mock_vector_store.add_vector.call_count == 3


class TestSimilarityRetriever:
    """Test similarity retriever."""
    
    def test_retriever_initialization(self, mock_vector_store):
        """Test retriever initialization."""
        retriever = SimilarityRetriever(
            vector_store=mock_vector_store,
            embedding_model=Mock(),
            top_k=5
        )
        assert retriever.vector_store == mock_vector_store
        assert retriever.top_k == 5
    
    def test_retrieve(self, mock_vector_store, mock_embedding_model):
        """Test retrieving similar documents."""
        retriever = SimilarityRetriever(
            vector_store=mock_vector_store,
            embedding_model=mock_embedding_model,
            top_k=2
        )
        
        results = retriever.retrieve("test query")
        
        assert len(results) == 2
        # Verify embedding was called for query
        mock_embedding_model.embed.assert_called_once_with("test query")
        # Verify search was called
        mock_vector_store.search.assert_called_once()


class TestOpenAIEmbeddings:
    """Test OpenAI embedding model."""
    
    def test_initialization(self, mock_openai_api_key):
        """Test OpenAI embedding model initialization."""
        model = OpenAIEmbeddings(api_key=mock_openai_api_key)
        assert model.api_key == mock_openai_api_key
        assert model.model == "text-embedding-3-small"
    
    def test_embed_text(self, mock_openai_api_key):
        """Test embedding text with OpenAI."""
        with patch('ai_multitool.rag.embeddings.openai.OpenAI') as mock_openai:
            # Setup mock
            mock_response = Mock()
            mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
            
            mock_client = Mock()
            mock_client.embeddings.create = Mock(return_value=mock_response)
            mock_openai.return_value = mock_client
            
            # Test
            model = OpenAIEmbeddings(api_key=mock_openai_api_key)
            embedding = model.embed("Sample text")
            
            assert embedding == [0.1, 0.2, 0.3]
    
    def test_embed_batch(self, mock_openai_api_key):
        """Test embedding multiple texts."""
        with patch('ai_multitool.rag.embeddings.openai.OpenAI') as mock_openai:
            # Setup mock
            mock_response = Mock()
            mock_response.data = [
                Mock(embedding=[0.1, 0.2, 0.3]),
                Mock(embedding=[0.4, 0.5, 0.6]),
            ]
            
            mock_client = Mock()
            mock_client.embeddings.create = Mock(return_value=mock_response)
            mock_openai.return_value = mock_client
            
            # Test
            model = OpenAIEmbeddings(api_key=mock_openai_api_key)
            embeddings = model.embed_batch(["Text 1", "Text 2"])
            
            assert len(embeddings) == 2
            assert embeddings[0] == [0.1, 0.2, 0.3]
            assert embeddings[1] == [0.4, 0.5, 0.6]


class TestRAGIntegration:
    """Test RAG integration scenarios."""
    
    def test_end_to_end_rag(self, mock_embedding_model, mock_vector_store):
        """Test end-to-end RAG workflow."""
        # Setup
        indexer = DocumentIndexer(
            embedding_model=mock_embedding_model,
            vector_store=mock_vector_store
        )
        
        # Index documents
        docs = [
            Document(text="Python is a programming language", doc_id="doc1"),
            Document(text="JavaScript is used for web development", doc_id="doc2"),
        ]
        indexer.add_documents(docs)
        
        # Retrieve
        retriever = SimilarityRetriever(
            vector_store=mock_vector_store,
            embedding_model=mock_embedding_model,
            top_k=1
        )
        
        results = retriever.retrieve("programming")
        
        assert len(results) > 0
        assert results[0][0].text is not None
