# ai-multitool Knowledge Graph Report

## Summary Statistics

- **Total Nodes**: 565
- **Total Edges**: 1099
- **Hyperedges**: 3
- **Communities Detected**: 45
- **Input Tokens**: 0
- **Output Tokens**: 0

## File Type Breakdown

- **code**: 284 nodes
- **rationale**: 280 nodes
- **document**: 1 nodes

## Top Source Files by Node Count

- **ai_multitool\core\exceptions.py**: 65 nodes
- **ai_multitool\core\llm_client.py**: 44 nodes
- **ai_multitool\cli\main.py**: 34 nodes
- **ai_multitool\rag\vector_store.py**: 34 nodes
- **ai_multitool\utils\metrics.py**: 31 nodes
- **ai_multitool\rag\embeddings.py**: 30 nodes
- **ai_multitool\utils\key_manager.py**: 30 nodes
- **ai_multitool\parsers\code_parser.py**: 28 nodes
- **ai_multitool\utils\git_utils.py**: 28 nodes
- **ai_multitool\rag\chunkers.py**: 26 nodes
- **ai_multitool\rag\indexer.py**: 22 nodes
- **ai_multitool\utils\context_builder.py**: 22 nodes
- **ai_multitool\utils\sanitizer.py**: 22 nodes
- **release.py**: 18 nodes
- **ai_multitool\rag\retriever.py**: 18 nodes

## Edge Relation Types

- **calls**: 269 edges
- **rationale_for**: 235 edges
- **uses**: 156 edges
- **method**: 133 edges
- **contains**: 118 edges
- **imports_from**: 95 edges
- **inherits**: 42 edges
- **imports**: 24 edges
- **implements**: 11 edges
- **references**: 8 edges
- **complements**: 5 edges
- **conceptually_related_to**: 3 edges

## Edge Confidence Distribution

- **EXTRACTED**: 765 edges
- **INFERRED**: 334 edges

## God Nodes (Top 20 by Connectivity)

1. **ValidationError** (code) - Degree: 55 - File: ai_multitool\core\exceptions.py
2. **str** (code) - Degree: 41 - File: 
3. **main.py** (code) - Degree: 35 - File: ai_multitool\cli\main.py
4. **exceptions.py** (code) - Degree: 24 - File: ai_multitool\core\exceptions.py
5. **APIError** (code) - Degree: 24 - File: ai_multitool\core\exceptions.py
6. **InMemoryVectorStore** (code) - Degree: 20 - File: ai_multitool\rag\vector_store.py
7. **.__init__()** (code) - Degree: 19 - File: ai_multitool\core\exceptions.py
8. **CodeParser** (code) - Degree: 19 - File: ai_multitool\parsers\code_parser.py
9. **AIMultitoolError** (code) - Degree: 18 - File: ai_multitool\core\exceptions.py
10. **FileOperationError** (code) - Degree: 18 - File: ai_multitool\core\exceptions.py
11. **llm_client.py** (code) - Degree: 18 - File: ai_multitool\core\llm_client.py
12. **ResponseCache** (code) - Degree: 18 - File: ai_multitool\core\llm_client.py
13. **AnthropicClient** (code) - Degree: 18 - File: ai_multitool\core\llm_client.py
14. **SmartContextBuilder** (code) - Degree: 18 - File: ai_multitool\utils\context_builder.py
15. **KeyManager** (code) - Degree: 18 - File: ai_multitool\utils\key_manager.py
16. **BaseLLMClient** (code) - Degree: 17 - File: ai_multitool\core\llm_client.py
17. **OpenAIClient** (code) - Degree: 17 - File: ai_multitool\core\llm_client.py
18. **DocumentIndexer** (code) - Degree: 17 - File: ai_multitool\rag\indexer.py
19. **vector_store.py** (code) - Degree: 17 - File: ai_multitool\rag\vector_store.py
20. **GitHelper** (code) - Degree: 17 - File: ai_multitool\utils\git_utils.py

## Community Structure (Top 15)


### Community 2 (73 nodes)

File types: code (39), rationale (34)

Source files: ai_multitool\utils\metrics.py (31), ai_multitool\utils\file_utils.py (12), ai_multitool\rag\embeddings.py (8), ai_multitool\core\exceptions.py (6), ai_multitool\parsers\code_parser.py (4)

Top nodes:
  - ValidationError (code) - Degree: 55
  - str (code) - Degree: 41
  - FileOperationError (code) - Degree: 18
  - metrics.py (code) - Degree: 14
  - MetricsError (code) - Degree: 13

### Community 3 (73 nodes)

File types: code (45), rationale (28)

Source files: ai_multitool\core\llm_client.py (40), ai_multitool\core\exceptions.py (22), ai_multitool\core\models.py (8),  (3)

Top nodes:
  - exceptions.py (code) - Degree: 24
  - APIError (code) - Degree: 24
  - AIMultitoolError (code) - Degree: 18
  - llm_client.py (code) - Degree: 18
  - ResponseCache (code) - Degree: 18

### Community 4 (71 nodes)

File types: code (44), rationale (27)

Source files: ai_multitool\core\exceptions.py (29), ai_multitool\parsers\code_parser.py (22), ai_multitool\utils\context_builder.py (16), ai_multitool\utils\file_utils.py (2), ai_multitool\utils\git_utils.py (2)

Top nodes:
  - .__init__() (code) - Degree: 19
  - CodeParser (code) - Degree: 19
  - SmartContextBuilder (code) - Degree: 18
  - AnalysisContext (code) - Degree: 11
  - .build_context() (code) - Degree: 10

### Community 0 (68 nodes)

File types: code (36), rationale (32)

Source files: ai_multitool\cli\main.py (32), ai_multitool\rag\vector_store.py (18), ai_multitool\config\settings.py (9), ai_multitool\utils\rag_helper.py (4), ai_multitool\utils\context_builder.py (2)

Top nodes:
  - main.py (code) - Degree: 35
  - InMemoryVectorStore (code) - Degree: 20
  - get_key_manager() (code) - Degree: 10
  - get_settings() (code) - Degree: 9
  - rag_search() (code) - Degree: 8

### Community 1 (59 nodes)

File types: code (35), rationale (24)

Source files: ai_multitool\rag\retriever.py (17), ai_multitool\rag\vector_store.py (11), ai_multitool\rag\embeddings.py (7), ai_multitool\rag\chunkers.py (5), ai_multitool\utils\rag_helper.py (4)

Top nodes:
  - vector_store.py (code) - Degree: 17
  - EmbeddingModel (code) - Degree: 13
  - SimilarityRetriever (code) - Degree: 13
  - context_builder.py (code) - Degree: 12
  - code_parser.py (code) - Degree: 11

### Community 5 (36 nodes)

File types: code (18), rationale (18)

Source files: ai_multitool\rag\chunkers.py (20), ai_multitool\rag\indexer.py (16)

Top nodes:
  - DocumentIndexer (code) - Degree: 17
  - RecursiveCharacterChunker (code) - Degree: 9
  - DocumentChunker (code) - Degree: 8
  - FixedSizeChunker (code) - Degree: 5
  - SentenceChunker (code) - Degree: 5

### Community 6 (29 nodes)

File types: code (16), rationale (13)

Source files: ai_multitool\utils\key_manager.py (26), ai_multitool\core\exceptions.py (3)

Top nodes:
  - KeyManager (code) - Degree: 18
  - KeyringError (code) - Degree: 8
  - .get_key() (code) - Degree: 8
  - .set_key() (code) - Degree: 7
  - .delete_key() (code) - Degree: 7

### Community 7 (26 nodes)

File types: rationale (25), document (1)

Source files: VECTOR_SYSTEM.md (10), ADVANCED_FEATURES.md (7), PLAN.md (6), README.md (1), COMPLETE_SUMMARY.md (1)

Top nodes:
  - BaseLLMClient (rationale) - Degree: 8
  - BaseEmbeddingModel (rationale) - Degree: 6
  - ai-multitool (document) - Degree: 5
  - BaseVectorStore (rationale) - Degree: 5
  - RAGSystem (rationale) - Degree: 3

### Community 8 (24 nodes)

File types: code (12), rationale (12)

Source files: ai_multitool\utils\git_utils.py (24)

Top nodes:
  - GitHelper (code) - Degree: 17
  - .get_context() (code) - Degree: 9
  - get_git_helper() (code) - Degree: 5
  - .__init__() (code) - Degree: 4
  - .get_recent_commits() (code) - Degree: 4

### Community 9 (21 nodes)

File types: code (11), rationale (10)

Source files: ai_multitool\utils\sanitizer.py (18), ai_multitool\core\exceptions.py (3)

Top nodes:
  - ContentSanitizer (code) - Degree: 12
  - .sanitize() (code) - Degree: 9
  - SanitizationError (code) - Degree: 8
  - SanitizationResult (code) - Degree: 5
  - get_sanitizer() (code) - Degree: 4

### Community 10 (18 nodes)

File types: code (10), rationale (8)

Source files: release.py (18)

Top nodes:
  - release.py (code) - Degree: 14
  - release() (code) - Degree: 8
  - run_command() (code) - Degree: 4
  - update_changelog() (code) - Degree: 4
  - git_commit() (code) - Degree: 4

### Community 11 (14 nodes)

File types: code (7), rationale (7)

Source files: ai_multitool\rag\embeddings.py (12), ai_multitool\core\exceptions.py (2)

Top nodes:
  - FakeEmbeddings (code) - Degree: 10
  - APIKeyError (code) - Degree: 7
  - .__init__() (code) - Degree: 3
  - .embed() (code) - Degree: 3
  - .embed_batch() (code) - Degree: 3

### Community 12 (8 nodes)

File types: code (4), rationale (4)

Source files: ai_multitool\core\models.py (8)

Top nodes:
  - ChatHistory (code) - Degree: 6
  - .add_message() (code) - Degree: 3
  - ._trim_history() (code) - Degree: 3
  - .get_context_messages() (code) - Degree: 2
  - Chat history with smart trimming (rationale) - Degree: 1

### Community 13 (5 nodes)

File types: rationale (5)

Source files: PLAN.md (3), ADVANCED_FEATURES.md (1), ULTIMATE_FEATURES.md (1)

Top nodes:
  - Message (rationale) - Degree: 3
  - ChatHistory (rationale) - Degree: 2
  - ContentSanitizer (rationale) - Degree: 1
  - LLMResponse (rationale) - Degree: 1
  - ContextWindowManager (rationale) - Degree: 1

### Community 14 (3 nodes)

File types: rationale (3)

Source files: ADVANCED_FEATURES.md (2), PLAN.md (1)

Top nodes:
  - MetricsCollector (rationale) - Degree: 2
  - AuditLogger (rationale) - Degree: 1
  - ModelInfo (rationale) - Degree: 1

## Hyperedges

- **LLM Client Hierarchy** (implement, confidence: 1.0)
  Nodes: plan_basellmclient, plan_anthropicclient, plan_openaiclient, plan_litellmclient

- **Embedding Model Hierarchy** (implement, confidence: 1.0)
  Nodes: vector_system_baseembeddingmodel, vector_system_openaiembeddingmodel, vector_system_anthropicembeddingmodel, vector_system_localembeddingmodel, vector_system_cohereembeddingmodel

- **Vector Store Hierarchy** (implement, confidence: 1.0)
  Nodes: vector_system_basevectorstore, vector_system_chromavectorstore, vector_system_faissvectorstore, vector_system_pineconevectorstore, vector_system_qdrantvectorstore


## Key Insights

1. **Architecture**: The codebase shows a layered architecture with clear separation between:
   - Core LLM client functionality (AnthropicClient, OpenAIClient, BaseLLMClient)
   - Vector/embedding system (BaseEmbeddingModel, various implementations)
   - RAG system components (chunkers, retriever, indexer)
   - Utility modules (file_utils, git_utils, code_parser, context_builder)

2. **Integration Patterns**: Strong connections between:
   - LLM clients and rate limiting/caching components
   - RAG system and embedding models/vector stores
   - Context builders and code parsers

3. **Documentation**: Multiple planning and feature documents exist, suggesting active development and feature planning:
   - VECTOR_SYSTEM.md - vector store architecture
   - ADVANCED_FEATURES.md - advanced component plans
   - ULTIMATE_FEATURES.md - future feature roadmap
   - PLAN.md - implementation planning

4. **Community Structure**: The graph shows 45 distinct communities, indicating modular design with clear boundaries between subsystems.

5. **Code Quality**: AST extraction captured 284 code nodes, showing comprehensive coverage of the Python codebase.

## Recommendations

1. Consider consolidating the numerous planning documents into a single cohesive architecture document
2. The strong modularity suggests good separation of concerns - maintain this pattern
3. The RAG system is well-integrated with the core LLM functionality
4. Consider adding more integration tests between the different communities
