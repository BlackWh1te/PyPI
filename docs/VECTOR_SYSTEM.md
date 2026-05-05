# Vector System & RAG Implementation for ai-multitool

## Overview
Comprehensive vector system for Retrieval-Augmented Generation (RAG) with support for multiple embedding models, vector databases, and advanced retrieval strategies.

## 1. Embedding Models

### Multi-Provider Embedding Support

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import numpy as np

class BaseEmbeddingModel(ABC):
    """Abstract base class for embedding models"""

    def __init__(self, model_name: str, dimensions: int):
        self.model_name = model_name
        self.dimensions = dimensions

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        pass

    @abstractmethod
    async def embed_query(self, query: str) -> List[float]:
        """Generate embedding optimized for queries"""
        pass

    def get_model_info(self) -> EmbeddingModelInfo:
        return EmbeddingModelInfo(
            name=self.model_name,
            dimensions=self.dimensions,
            max_tokens=8191,
            cost_per_1k_tokens=0.0001
        )

class OpenAIEmbeddingModel(BaseEmbeddingModel):
    """OpenAI text-embedding models"""

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        dimensions: int = 1536
    ):
        super().__init__(model, dimensions)
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model

    async def embed(self, text: str) -> List[float]:
        response = await self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        # Batch processing for efficiency
        batch_size = 100
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = await self.client.embeddings.create(
                model=self.model,
                input=batch
            )
            all_embeddings.extend([item.embedding for item in response.data])

        return all_embeddings

    async def embed_query(self, query: str) -> List[float]:
        # Same as embed for OpenAI
        return await self.embed(query)

class AnthropicEmbeddingModel(BaseEmbeddingModel):
    """Anthropic embedding support via Claude API"""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-sonnet-20240229",
        dimensions: int = 1024
    ):
        super().__init__(model, dimensions)
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def embed(self, text: str) -> List[float]:
        # Anthropic doesn't have native embeddings yet
        # Use OpenAI as fallback or local model
        return await self._fallback_embed(text)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [await self.embed(text) for text in texts]

    async def embed_query(self, query: str) -> List[float]:
        return await self.embed(query)

    async def _fallback_embed(self, text: str) -> List[float]:
        # Fallback to sentence-transformers
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embedding = model.encode(text)
        return embedding.tolist()

class LocalEmbeddingModel(BaseEmbeddingModel):
    """Local embedding models using sentence-transformers"""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        dimensions: int = 384,
        device: str = "cpu"
    ):
        super().__init__(model_name, dimensions)
        self.device = device
        self._model = None

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(
                self.model_name,
                device=self.device
            )

    async def embed(self, text: str) -> List[float]:
        self._load_model()
        embedding = self._model.encode(text)
        return embedding.tolist()

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        self._load_model()
        embeddings = self._model.encode(texts)
        return embeddings.tolist()

    async def embed_query(self, query: str) -> List[float]:
        return await self.embed(query)

class CohereEmbeddingModel(BaseEmbeddingModel):
    """Cohere embedding models"""

    def __init__(
        self,
        api_key: str,
        model: str = "embed-english-v3.0",
        dimensions: int = 1024
    ):
        super().__init__(model, dimensions)
        self.client = cohere.AsyncClient(api_key=api_key)
        self.model = model

    async def embed(self, text: str) -> List[float]:
        response = await self.client.embed(
            texts=[text],
            model=self.model,
            input_type="search_document"
        )
        return response.embeddings[0]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        response = await self.client.embed(
            texts=texts,
            model=self.model,
            input_type="search_document"
        )
        return response.embeddings

    async def embed_query(self, query: str) -> List[float]:
        response = await self.client.embed(
            texts=[query],
            model=self.model,
            input_type="search_query"
        )
        return response.embeddings[0]

class EmbeddingModelFactory:
    """Factory for creating embedding models"""

    @staticmethod
    def create(
        provider: str,
        api_key: str,
        model: Optional[str] = None,
        **kwargs
    ) -> BaseEmbeddingModel:
        providers = {
            "openai": OpenAIEmbeddingModel,
            "anthropic": AnthropicEmbeddingModel,
            "local": LocalEmbeddingModel,
            "cohere": CohereEmbeddingModel,
        }

        if provider not in providers:
            raise ValueError(f"Unknown provider: {provider}")

        return providers[provider](api_key, model, **kwargs)
```

## 2. Vector Stores

### Abstract Vector Store Interface

```python
class BaseVectorStore(ABC):
    """Abstract base class for vector stores"""

    @abstractmethod
    async def add(
        self,
        embeddings: List[List[float]],
        documents: List[str],
        metadata: List[Dict[str, Any]]
    ) -> List[str]:
        """Add documents with embeddings"""
        pass

    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar documents"""
        pass

    @abstractmethod
    async def delete(self, ids: List[str]) -> bool:
        """Delete documents by IDs"""
        pass

    @abstractmethod
    async def update(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadata: List[Dict[str, Any]]
    ) -> bool:
        """Update documents"""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Count total documents"""
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all documents"""
        pass

class SearchResult(BaseModel):
    id: str
    document: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

### ChromaDB Implementation

```python
class ChromaVectorStore(BaseVectorStore):
    """ChromaDB vector store implementation"""

    def __init__(
        self,
        collection_name: str = "ai_multitool",
        persist_directory: Optional[str] = None,
        embedding_function: Optional[Callable] = None
    ):
        import chromadb
        from chromadb.config import Settings

        self.client = chromadb.Client(
            Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False
            )
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_function
        )

    async def add(
        self,
        embeddings: List[List[float]],
        documents: List[str],
        metadata: List[Dict[str, Any]]
    ) -> List[str]:
        ids = [str(uuid.uuid4()) for _ in documents]

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadata
        )

        return ids

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter
        )

        return [
            SearchResult(
                id=results["ids"][0][i],
                document=results["documents"][0][i],
                score=1.0 - results["distances"][0][i],  # Convert distance to similarity
                metadata=results["metadatas"][0][i] if results["metadatas"] else {}
            )
            for i in range(len(results["ids"][0]))
        ]

    async def delete(self, ids: List[str]) -> bool:
        self.collection.delete(ids=ids)
        return True

    async def update(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadata: List[Dict[str, Any]]
    ) -> bool:
        self.collection.update(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadata
        )
        return True

    async def count(self) -> int:
        return self.collection.count()

    async def clear(self) -> bool:
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name
        )
        return True
```

### FAISS Implementation (Local)

```python
class FAISSVectorStore(BaseVectorStore):
    """FAISS-based local vector store"""

    def __init__(
        self,
        dimensions: int = 1536,
        index_type: str = "flat",
        persist_path: Optional[str] = None
    ):
        import faiss
        self.dimensions = dimensions
        self.persist_path = persist_path
        self.documents: Dict[str, str] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}

        # Create FAISS index
        if index_type == "flat":
            self.index = faiss.IndexFlatL2(dimensions)
        elif index_type == "ivf":
            quantizer = faiss.IndexFlatL2(dimensions)
            self.index = faiss.IndexIVFFlat(quantizer, dimensions, 100)
        elif index_type == "hnsw":
            self.index = faiss.IndexHNSWFlat(dimensions, 32)
        else:
            raise ValueError(f"Unknown index type: {index_type}")

        # Load from disk if exists
        if persist_path and os.path.exists(persist_path):
            self._load()

    async def add(
        self,
        embeddings: List[List[float]],
        documents: List[str],
        metadata: List[Dict[str, Any]]
    ) -> List[str]:
        ids = [str(uuid.uuid4()) for _ in documents]

        # Add to FAISS index
        embeddings_array = np.array(embeddings, dtype=np.float32)
        self.index.add(embeddings_array)

        # Store documents and metadata
        for doc_id, doc, meta in zip(ids, documents, metadata):
            self.documents[doc_id] = doc
            self.metadata[doc_id] = meta

        # Persist if path specified
        if self.persist_path:
            self._save()

        return ids

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        query_array = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query_array, top_k)

        results = []
        for i in range(len(indices[0])):
            doc_id = str(indices[0][i])
            if doc_id == "-1":  # FAISS returns -1 for empty results
                continue

            # Apply filter if specified
            if filter:
                meta = self.metadata.get(doc_id, {})
                if not all(meta.get(k) == v for k, v in filter.items()):
                    continue

            results.append(SearchResult(
                id=doc_id,
                document=self.documents[doc_id],
                score=1.0 / (1.0 + distances[0][i]),  # Convert distance to similarity
                metadata=self.metadata.get(doc_id, {})
            ))

        return results

    async def delete(self, ids: List[str]) -> bool:
        # FAISS doesn't support deletion, need to rebuild index
        # For simplicity, just mark as deleted
        for doc_id in ids:
            if doc_id in self.documents:
                del self.documents[doc_id]
            if doc_id in self.metadata:
                del self.metadata[doc_id]
        return True

    async def update(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadata: List[Dict[str, Any]]
    ) -> bool:
        # Delete old, add new
        await self.delete(ids)
        await self.add(embeddings, documents, metadata)
        return True

    async def count(self) -> int:
        return self.index.ntotal

    async def clear(self) -> bool:
        import faiss
        self.index = faiss.IndexFlatL2(self.dimensions)
        self.documents.clear()
        self.metadata.clear()
        return True

    def _save(self):
        import faiss
        faiss.write_index(self.index, f"{self.persist_path}.index")
        with open(f"{self.persist_path}.docs", "wb") as f:
            pickle.dump({"documents": self.documents, "metadata": self.metadata}, f)

    def _load(self):
        import faiss
        self.index = faiss.read_index(f"{self.persist_path}.index")
        with open(f"{self.persist_path}.docs", "rb") as f:
            data = pickle.load(f)
            self.documents = data["documents"]
            self.metadata = data["metadata"]
```

### Pinecone Implementation (Cloud)

```python
class PineconeVectorStore(BaseVectorStore):
    """Pinecone cloud vector store"""

    def __init__(
        self,
        api_key: str,
        index_name: str,
        dimensions: int = 1536,
        environment: str = "us-west1-gcp"
    ):
        import pinecone
        pinecone.init(api_key=api_key, environment=environment)

        self.index_name = index_name
        self.dimensions = dimensions

        # Create index if doesn't exist
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=index_name,
                dimension=dimensions,
                metric="cosine"
            )

        self.index = pinecone.Index(index_name)

    async def add(
        self,
        embeddings: List[List[float]],
        documents: List[str],
        metadata: List[Dict[str, Any]]
    ) -> List[str]:
        ids = [str(uuid.uuid4()) for _ in documents]

        vectors = [
            {
                "id": doc_id,
                "values": embedding,
                "metadata": {"text": doc, **meta}
            }
            for doc_id, embedding, doc, meta in zip(ids, embeddings, documents, metadata)
        ]

        self.index.upsert(vectors)
        return ids

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            filter=filter,
            include_metadata=True
        )

        return [
            SearchResult(
                id=match["id"],
                document=match["metadata"]["text"],
                score=match["score"],
                metadata=match["metadata"]
            )
            for match in results["matches"]
        ]

    async def delete(self, ids: List[str]) -> bool:
        self.index.delete(ids=ids)
        return True

    async def update(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadata: List[Dict[str, Any]]
    ) -> bool:
        vectors = [
            {
                "id": doc_id,
                "values": embedding,
                "metadata": {"text": doc, **meta}
            }
            for doc_id, embedding, doc, meta in zip(ids, embeddings, documents, metadata)
        ]

        self.index.upsert(vectors)
        return True

    async def count(self) -> int:
        return self.index.describe_index_stats()["total_vector_count"]

    async def clear(self) -> bool:
        # Pinecone doesn't support clear, need to delete and recreate
        import pinecone
        pinecone.delete_index(self.index_name)
        pinecone.create_index(
            name=self.index_name,
            dimension=self.dimensions,
            metric="cosine"
        )
        self.index = pinecone.Index(self.index_name)
        return True
```

### Qdrant Implementation

```python
class QdrantVectorStore(BaseVectorStore):
    """Qdrant vector store implementation"""

    def __init__(
        self,
        url: str = "http://localhost:6333",
        collection_name: str = "ai_multitool",
        dimensions: int = 1536,
        api_key: Optional[str] = None
    ):
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams, PointStruct

        self.client = QdrantClient(url=url, api_key=api_key)
        self.collection_name = collection_name
        self.dimensions = dimensions

        # Create collection if doesn't exist
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if collection_name not in collection_names:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=dimensions,
                    distance=Distance.COSINE
                )
            )

    async def add(
        self,
        embeddings: List[List[float]],
        documents: List[str],
        metadata: List[Dict[str, Any]]
    ) -> List[str]:
        ids = [str(uuid.uuid4()) for _ in documents]

        points = [
            PointStruct(
                id=uuid.UUID(doc_id),
                vector=embedding,
                payload={"text": doc, **meta}
            )
            for doc_id, embedding, doc, meta in zip(ids, embeddings, documents, metadata)
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        return ids

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        search_filter = None
        if filter:
            conditions = [
                FieldCondition(
                    key=key,
                    match=MatchValue(value=value)
                )
                for key, value in filter.items()
            ]
            search_filter = Filter(must=conditions)

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=search_filter,
            with_payload=True
        )

        return [
            SearchResult(
                id=str(result.id),
                document=result.payload["text"],
                score=result.score,
                metadata=result.payload
            )
            for result in results
        ]

    async def delete(self, ids: List[str]) -> bool:
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=ids
        )
        return True

    async def update(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadata: List[Dict[str, Any]]
    ) -> bool:
        points = [
            PointStruct(
                id=uuid.UUID(doc_id),
                vector=embedding,
                payload={"text": doc, **meta}
            )
            for doc_id, embedding, doc, meta in zip(ids, embeddings, documents, metadata)
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        return True

    async def count(self) -> int:
        return self.client.count(collection_name=self.collection_name).count

    async def clear(self) -> bool:
        self.client.delete_collection(self.collection_name)
        from qdrant_client.models import Distance, VectorParams
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.dimensions,
                distance=Distance.COSINE
            )
        )
        return True
```

## 3. Advanced Retrieval Strategies

### Hybrid Search (Semantic + Keyword)

```python
class HybridRetriever:
    """Combine semantic and keyword search"""

    def __init__(
        self,
        vector_store: BaseVectorStore,
        embedding_model: BaseEmbeddingModel
    ):
        self.vector_store = vector_store
        self.embedding_model = embedding_model

    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        alpha: float = 0.5  # Weight for semantic vs keyword
    ) -> List[SearchResult]:
        # Semantic search
        query_embedding = await self.embedding_model.embed_query(query)
        semantic_results = await self.vector_store.search(query_embedding, top_k * 2)

        # Keyword search (BM25)
        keyword_results = await self._keyword_search(query, top_k * 2)

        # Combine and re-rank
        combined = self._combine_results(
            semantic_results,
            keyword_results,
            alpha
        )

        return combined[:top_k]

    async def _keyword_search(self, query: str, top_k: int) -> List[SearchResult]:
        # Implement BM25 or similar keyword search
        # This would require indexing documents for keyword search
        return []

    def _combine_results(
        self,
        semantic: List[SearchResult],
        keyword: List[SearchResult],
        alpha: float
    ) -> List[SearchResult]:
        # Combine scores with weighted average
        combined_scores = {}

        for result in semantic:
            combined_scores[result.id] = alpha * result.score

        for result in keyword:
            if result.id in combined_scores:
                combined_scores[result.id] += (1 - alpha) * result.score
            else:
                combined_scores[result.id] = (1 - alpha) * result.score

        # Sort by combined score
        sorted_results = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [SearchResult(id=id, score=score) for id, score in sorted_results]
```

### Re-ranking with Cross-Encoder

```python
class RerankingRetriever:
    """Re-rank results using cross-encoder for better relevance"""

    def __init__(
        self,
        vector_store: BaseVectorStore,
        embedding_model: BaseEmbeddingModel,
        rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.rerank_model = rerank_model
        self._reranker = None

    def _load_reranker(self):
        if self._reranker is None:
            from sentence_transformers import CrossEncoder
            self._reranker = CrossEncoder(self.rerank_model)

    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        rerank_top_k: int = 50
    ) -> List[SearchResult]:
        # Initial retrieval with larger set
        query_embedding = await self.embedding_model.embed_query(query)
        initial_results = await self.vector_store.search(
            query_embedding,
            top_k=rerank_top_k
        )

        # Re-rank with cross-encoder
        self._load_reranker()

        pairs = [
            (query, result.document)
            for result in initial_results
        ]

        scores = self._reranker.predict(pairs)

        # Update scores and re-sort
        for result, score in zip(initial_results, scores):
            result.score = float(score)

        reranked = sorted(initial_results, key=lambda x: x.score, reverse=True)

        return reranked[:top_k]
```

### Multi-Query Retrieval

```python
class MultiQueryRetriever:
    """Generate multiple query variations for better coverage"""

    def __init__(
        self,
        vector_store: BaseVectorStore,
        embedding_model: BaseEmbeddingModel,
        llm_client: BaseLLMClient
    ):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.llm_client = llm_client

    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        num_queries: int = 3
    ) -> List[SearchResult]:
        # Generate query variations
        query_variations = await self._generate_query_variations(
            query,
            num_queries
        )

        # Retrieve for each variation
        all_results = []
        for variation in query_variations:
            query_embedding = await self.embedding_model.embed_query(variation)
            results = await self.vector_store.search(query_embedding, top_k)
            all_results.extend(results)

        # Deduplicate and re-rank
        unique_results = self._deduplicate(all_results)
        reranked = sorted(unique_results, key=lambda x: x.score, reverse=True)

        return reranked[:top_k]

    async def _generate_query_variations(
        self,
        query: str,
        num_queries: int
    ) -> List[str]:
        prompt = f"""Generate {num_queries} different variations of this search query to improve retrieval:
Query: {query}

Variations (one per line):"""

        response = await self.llm_client.chat([
            Message(role="user", content=prompt)
        ])

        variations = response.content.strip().split("\n")
        return [v.strip() for v in variations if v.strip()]

    def _deduplicate(self, results: List[SearchResult]) -> List[SearchResult]:
        seen = set()
        unique = []

        for result in results:
            if result.id not in seen:
                seen.add(result.id)
                unique.append(result)

        return unique
```

### Recursive Retrieval

```python
class RecursiveRetriever:
    """Recursively retrieve related documents"""

    def __init__(
        self,
        vector_store: BaseVectorStore,
        embedding_model: BaseEmbeddingModel,
        max_depth: int = 2,
        branch_factor: int = 3
    ):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.max_depth = max_depth
        self.branch_factor = branch_factor

    async def retrieve(
        self,
        query: str,
        top_k: int = 10
    ) -> List[SearchResult]:
        all_results = []

        async def retrieve_recursive(
            current_query: str,
            depth: int
        ):
            if depth >= self.max_depth:
                return

            query_embedding = await self.embedding_model.embed_query(current_query)
            results = await self.vector_store.search(
                query_embedding,
                self.branch_factor
            )

            for result in results:
                all_results.append(result)

                # Use document as next query
                await retrieve_recursive(result.document, depth + 1)

        await retrieve_recursive(query, 0)

        # Deduplicate and re-rank
        unique_results = self._deduplicate(all_results)
        reranked = sorted(unique_results, key=lambda x: x.score, reverse=True)

        return reranked[:top_k]

    def _deduplicate(self, results: List[SearchResult]) -> List[SearchResult]:
        seen = set()
        unique = []

        for result in results:
            if result.id not in seen:
                seen.add(result.id)
                unique.append(result)

        return unique
```

## 4. Document Processing

### Chunking Strategies

```python
class DocumentChunker:
    """Split documents into chunks for better retrieval"""

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        strategy: str = "fixed"
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy

    async def chunk(self, document: str) -> List[str]:
        if self.strategy == "fixed":
            return self._fixed_chunk(document)
        elif self.strategy == "semantic":
            return await self._semantic_chunk(document)
        elif self.strategy == "recursive":
            return self._recursive_chunk(document)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

    def _fixed_chunk(self, document: str) -> List[str]:
        """Fixed-size chunking with overlap"""
        chunks = []
        start = 0

        while start < len(document):
            end = start + self.chunk_size
            chunk = document[start:end]
            chunks.append(chunk)
            start = end - self.chunk_overlap

        return chunks

    async def _semantic_chunk(self, document: str) -> List[str]:
        """Semantic chunking based on sentence boundaries"""
        import nltk
        nltk.download('punkt')

        sentences = nltk.sent_tokenize(document)
        chunks = []
        current_chunk = ""
        current_length = 0

        for sentence in sentences:
            if current_length + len(sentence) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
                current_length = len(sentence)
            else:
                current_chunk += " " + sentence
                current_length += len(sentence)

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _recursive_chunk(self, document: str) -> List[str]:
        """Recursive character chunking"""
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )

        return splitter.split_text(document)
```

### Metadata Extraction

```python
class MetadataExtractor:
    """Extract metadata from documents"""

    async def extract(self, document: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        metadata = {}

        # File metadata
        if file_path:
            metadata["file_path"] = file_path
            metadata["file_name"] = os.path.basename(file_path)
            metadata["file_extension"] = os.path.splitext(file_path)[1]

        # Content metadata
        metadata["char_count"] = len(document)
        metadata["word_count"] = len(document.split())
        metadata["line_count"] = len(document.split("\n"))

        # Language detection
        metadata["language"] = self._detect_language(document)

        # Extract code-specific metadata if applicable
        if self._is_code(document):
            metadata.update(self._extract_code_metadata(document))

        return metadata

    def _detect_language(self, text: str) -> str:
        from langdetect import detect
        try:
            return detect(text)
        except:
            return "unknown"

    def _is_code(self, text: str) -> bool:
        code_indicators = [
            "def ", "class ", "import ", "function ",
            "const ", "let ", "var ", "function("
        ]
        return any(indicator in text for indicator in code_indicators)

    def _extract_code_metadata(self, code: str) -> Dict[str, Any]:
        metadata = {}

        # Detect programming language
        metadata["programming_language"] = self._detect_programming_language(code)

        # Extract imports
        metadata["imports"] = self._extract_imports(code)

        # Extract functions/classes
        metadata["functions"] = self._extract_functions(code)
        metadata["classes"] = self._extract_classes(code)

        return metadata

    def _detect_programming_language(self, code: str) -> str:
        if "def " in code and "import " in code:
            return "python"
        elif "function " in code or "const " in code:
            return "javascript"
        elif "class " in code and "public " in code:
            return "java"
        else:
            return "unknown"

    def _extract_imports(self, code: str) -> List[str]:
        imports = []
        for line in code.split("\n"):
            if line.strip().startswith("import ") or line.strip().startswith("from "):
                imports.append(line.strip())
        return imports

    def _extract_functions(self, code: str) -> List[str]:
        functions = []
        for line in code.split("\n"):
            if "def " in line or "function " in line:
                functions.append(line.strip())
        return functions

    def _extract_classes(self, code: str) -> List[str]:
        classes = []
        for line in code.split("\n"):
            if line.strip().startswith("class "):
                classes.append(line.strip())
        return classes
```

## 5. RAG System Integration

### Complete RAG Pipeline

```python
class RAGPipeline:
    """Complete RAG pipeline with document processing and retrieval"""

    def __init__(
        self,
        embedding_model: BaseEmbeddingModel,
        vector_store: BaseVectorStore,
        chunker: DocumentChunker,
        retriever: BaseRetriever,
        llm_client: BaseLLMClient
    ):
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.chunker = chunker
        self.retriever = retriever
        self.llm_client = llm_client

    async def add_document(
        self,
        document: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Add document to RAG system"""
        # Chunk document
        chunks = await self.chunker.chunk(document)

        # Extract metadata
        if metadata is None:
            metadata = {}
        doc_metadata = await MetadataExtractor().extract(document)
        metadata = {**metadata, **doc_metadata}

        # Generate embeddings
        embeddings = await self.embedding_model.embed_batch(chunks)

        # Add to vector store
        chunk_metadata = [
            {**metadata, "chunk_index": i, "chunk_count": len(chunks)}
            for i in range(len(chunks))
        ]

        ids = await self.vector_store.add(embeddings, chunks, chunk_metadata)

        return ids

    async def add_file(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Add file to RAG system"""
        with open(file_path, "r") as f:
            content = f.read()

        if metadata is None:
            metadata = {}
        metadata["file_path"] = file_path

        return await self.add_document(content, metadata)

    async def query(
        self,
        query: str,
        top_k: int = 5,
        include_context: bool = True
    ) -> RAGResponse:
        """Query RAG system"""
        # Retrieve relevant documents
        results = await self.retriever.retrieve(query, top_k)

        # Build context
        context = ""
        if include_context:
            context = "\n\n".join([
                f"Document {i+1}:\n{result.document}"
                for i, result in enumerate(results)
            ])

        # Generate response
        if context:
            prompt = f"""Context:
{context}

Question: {query}

Answer:"""
        else:
            prompt = query

        response = await self.llm_client.chat([
            Message(role="user", content=prompt)
        ])

        return RAGResponse(
            answer=response.content,
            context=context,
            sources=results,
            tokens_used=response.tokens_used
        )

    async def delete_document(self, document_id: str) -> bool:
        """Delete document from RAG system"""
        return await self.vector_store.delete([document_id])

    async def clear(self) -> bool:
        """Clear all documents"""
        return await self.vector_store.clear()
```

### RAG Response Model

```python
class RAGResponse(BaseModel):
    answer: str
    context: str
    sources: List[SearchResult]
    tokens_used: int
    latency_ms: Optional[float] = None
```

## 6. Vector Store Factory

```python
class VectorStoreFactory:
    """Factory for creating vector stores"""

    @staticmethod
    def create(
        store_type: str,
        **kwargs
    ) -> BaseVectorStore:
        stores = {
            "chroma": ChromaVectorStore,
            "faiss": FAISSVectorStore,
            "pinecone": PineconeVectorStore,
            "qdrant": QdrantVectorStore,
        }

        if store_type not in stores:
            raise ValueError(f"Unknown store type: {store_type}")

        return stores[store_type](**kwargs)
```

## 7. CLI Commands for Vector System

```python
@app.command()
def index(
    path: str = typer.Argument(..., help="File or directory to index"),
    store: str = typer.Option("chroma", help="Vector store type"),
    chunk_size: int = typer.Option(512, help="Chunk size"),
):
    """Index documents into vector store"""
    console.print(f"[bold cyan]Indexing: {path}[/bold cyan]")

    # Initialize components
    embedding_model = EmbeddingModelFactory.create(
        settings.embedding_provider,
        settings.anthropic_api_key
    )
    vector_store = VectorStoreFactory.create(store)
    chunker = DocumentChunker(chunk_size=chunk_size)

    # Process files
    if os.path.isfile(path):
        with open(path, "r") as f:
            content = f.read()
        ids = await rag_pipeline.add_document(content)
        console.print(f"Indexed document with {len(ids)} chunks")
    elif os.path.isdir(path):
        for file_path in Path(path).rglob("*"):
            if file_path.is_file():
                with open(file_path, "r") as f:
                    content = f.read()
                await rag_pipeline.add_document(content, {"file_path": str(file_path)})
        console.print(f"Indexed directory")

@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    store: str = typer.Option("chroma", help="Vector store type"),
    top_k: int = typer.Option(5, help="Number of results"),
):
    """Search indexed documents"""
    console.print(f"[bold cyan]Searching: {query}[/bold cyan]")

    # Initialize components
    embedding_model = EmbeddingModelFactory.create(
        settings.embedding_provider,
        settings.anthropic_api_key
    )
    vector_store = VectorStoreFactory.create(store)

    # Search
    query_embedding = await embedding_model.embed_query(query)
    results = await vector_store.search(query_embedding, top_k)

    # Display results
    for i, result in enumerate(results):
        console.print(f"\n[bold]Result {i+1}[/bold] (score: {result.score:.4f})")
        console.print(Panel(result.document))
```

## Summary

The vector system provides:

1. **Multiple Embedding Models**: OpenAI, Anthropic, Local (sentence-transformers), Cohere
2. **Multiple Vector Stores**: ChromaDB, FAISS (local), Pinecone (cloud), Qdrant
3. **Advanced Retrieval**: Hybrid search, re-ranking, multi-query, recursive retrieval
4. **Document Processing**: Multiple chunking strategies, metadata extraction
5. **Complete RAG Pipeline**: End-to-end document indexing and querying
6. **CLI Integration**: Commands for indexing and searching

This comprehensive vector system enables powerful retrieval-augmented generation capabilities for ai-multitool.
