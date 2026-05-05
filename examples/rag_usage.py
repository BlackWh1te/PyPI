"""RAG (Retrieval-Augmented Generation) usage example."""

import asyncio
from ai_multitool import (
    AnthropicClient,
    DocumentIndexer,
    Document,
    OpenAIEmbeddingModel,
    InMemoryVectorStore,
    SimilarityRetriever,
    Message,
    MessageRole,
)


async def main():
    """RAG usage example."""
    # Setup RAG components
    print("Setting up RAG...")
    embedding_model = OpenAIEmbeddingModel(api_key="your-openai-api-key")
    vector_store = InMemoryVectorStore(dimension=1536)
    indexer = DocumentIndexer(
        embedding_model=embedding_model,
        vector_store=vector_store
    )

    # Index documents
    print("Indexing documents...")
    documents = [
        Document(
            text="Python is a high-level programming language known for its simplicity and readability.",
            doc_id="doc1",
            metadata={"source": "intro.txt"}
        ),
        Document(
            text="JavaScript is primarily used for web development and runs in browsers.",
            doc_id="doc2",
            metadata={"source": "web.txt"}
        ),
        Document(
            text="Rust is a systems programming language focused on safety and performance.",
            doc_id="doc3",
            metadata={"source": "systems.txt"}
        ),
    ]

    for doc in documents:
        indexer.add_document(doc)

    print(f"Indexed {len(documents)} documents")

    # Retrieve relevant documents
    print("\nRetrieving relevant documents...")
    retriever = SimilarityRetriever(vector_store)
    results = retriever.retrieve("web development languages", top_k=2)

    print(f"Found {len(results)} relevant documents:")
    for result in results:
        print(f"  - {result.text[:80]}... (score: {result.score:.3f})")

    # Use retrieved context in chat
    print("\nChatting with AI using RAG context...")
    client = AnthropicClient(
        api_key="your-anthropic-api-key",
        model="claude-3-sonnet-20240229"
    )

    context = "\n\n".join([r.text for r in results])
    system_prompt = f"Use the following context to answer questions:\n\n{context}"

    response = await client.chat([
        Message(role=MessageRole.USER, content="What language is used for web development?")
    ], system_prompt=system_prompt)

    print(f"AI Response: {response.content}")


if __name__ == "__main__":
    asyncio.run(main())
