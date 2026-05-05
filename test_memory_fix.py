#!/usr/bin/env python3
"""
Test script to verify memory fixes for InMemoryVectorStore.
This tests that dynamic allocation reduces memory usage from ~58MB to near-zero when empty.
"""

import sys
import psutil
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_multitool.rag.vector_store import InMemoryVectorStore
from ai_multitool.rag.chunkers import DocumentChunk

def get_memory_mb():
    """Get current process memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def test_empty_store_memory():
    """Test that empty store uses minimal memory."""
    print("Testing empty InMemoryVectorStore memory usage...")
    
    # Measure memory before
    mem_before = get_memory_mb()
    print(f"Memory before: {mem_before:.2f} MB")
    
    # Create empty store
    store = InMemoryVectorStore(max_chunks=10000, dimension=1536)
    
    # Measure memory after
    mem_after = get_memory_mb()
    print(f"Memory after: {mem_after:.2f} MB")
    mem_used = mem_after - mem_before
    print(f"Memory used: {mem_used:.2f} MB")
    
    # With dynamic allocation, should use < 1 MB for empty store
    # Old implementation used ~58.59 MB
    if mem_used < 1.0:
        print("[PASS] Empty store uses < 1 MB (dynamic allocation working)")
        return True
    else:
        print(f"[FAIL] Empty store uses {mem_used:.2f} MB (expected < 1 MB)")
        return False

def test_add_chunks_memory():
    """Test that adding chunks grows memory gradually."""
    print("\nTesting memory growth when adding chunks...")
    
    # Create empty store
    store = InMemoryVectorStore(max_chunks=10000, dimension=1536)
    mem_before = get_memory_mb()
    print(f"Memory before adding: {mem_before:.2f} MB")
    
    # Add 10 chunks
    chunks = []
    embeddings = []
    for i in range(10):
        chunk = DocumentChunk(
            text=f"Test chunk {i}",
            chunk_id=f"chunk_{i}",
            start_index=0,
            end_index=10,
            metadata={"index": i}
        )
        chunks.append(chunk)
        # Create dummy embedding (1536 dimensions)
        embeddings.append([0.1] * 1536)
    
    store.add(chunks, embeddings)
    mem_after = get_memory_mb()
    print(f"Memory after adding 10 chunks: {mem_after:.2f} MB")
    mem_used = mem_after - mem_before
    print(f"Memory used: {mem_used:.2f} MB")
    
    # Should be roughly: 10 chunks * 1536 dims * 4 bytes = ~60KB
    # Plus overhead, so < 1 MB is reasonable
    if mem_used < 2.0:
        print("[PASS] Adding 10 chunks uses < 2 MB")
        return True
    else:
        print(f"[FAIL] Adding 10 chunks uses {mem_used:.2f} MB (expected < 2 MB)")
        return False

def test_clear_memory():
    """Test that clearing releases memory."""
    print("\nTesting memory release after clear...")
    
    # Create store with chunks
    store = InMemoryVectorStore(max_chunks=10000, dimension=1536)
    chunks = []
    embeddings = []
    for i in range(100):
        chunk = DocumentChunk(
            text=f"Test chunk {i}",
            chunk_id=f"chunk_{i}",
            start_index=0,
            end_index=10,
            metadata={"index": i}
        )
        chunks.append(chunk)
        embeddings.append([0.1] * 1536)
    
    store.add(chunks, embeddings)
    mem_with_data = get_memory_mb()
    print(f"Memory with 100 chunks: {mem_with_data:.2f} MB")
    
    # Clear store
    store.clear()
    mem_after_clear = get_memory_mb()
    print(f"Memory after clear: {mem_after_clear:.2f} MB")
    
    # Should be close to original, though Python may not release all to OS
    # But it should be significantly less than with data
    if mem_after_clear < mem_with_data:
        print("[PASS] Clearing reduces memory usage")
        return True
    else:
        print("[FAIL] Clearing did not reduce memory usage")
        return False

def main():
    print("=" * 60)
    print("Memory Fix Verification Test")
    print("=" * 60)
    
    results = []
    
    # Test 1: Empty store memory
    results.append(test_empty_store_memory())
    
    # Test 2: Add chunks memory
    results.append(test_add_chunks_memory())
    
    # Test 3: Clear memory
    results.append(test_clear_memory())
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("[PASS] All memory fixes verified successfully!")
        return 0
    else:
        print("[FAIL] Some memory tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
