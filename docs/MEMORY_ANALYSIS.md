# Memory Analysis Report

**Date:** 2026-05-05  
**Issue:** PC freezing when running Python files  
**Severity:** CRITICAL

## Root Causes Identified

### 1. **Unlimited Directory Indexing** (CRITICAL)
**Location:** `ai_multitool/rag/indexer.py:113-162`

**Problem:** The `index_directory()` method reads ALL files matching a pattern recursively without any limits:
```python
for file_path in dir_path.rglob(pattern):  # NO LIMIT
    if file_path.is_file():
        text = read_file(str(file_path))  # Loads entire file into memory
        documents.append(document)  # Accumulates ALL documents
```

**Impact:** If indexing a directory with 1000 files of 1MB each, this loads 1GB+ into memory instantly.

**Fix:** Add file count and total size limits with batch processing.

---

### 2. **Batch Document Processing** (HIGH)
**Location:** `ai_multitool/rag/indexer.py:82-111`

**Problem:** `add_documents()` processes all documents at once:
```python
all_chunks = []
all_embeddings = []
for document in documents:  # Could be thousands
    chunks = self.chunker.chunk(document.text, document.metadata)
    all_chunks.extend(chunks)  # Accumulates ALL chunks
all_embeddings = self.embedding_model.embed_batch(chunk_texts)  # ALL at once
```

**Impact:** Memory grows linearly with document count. 1000 documents × 10 chunks each = 10,000 chunks in memory.

**Fix:** Process documents in batches with periodic cleanup.

---

### 3. **CLI Directory Analysis** (HIGH)
**Location:** `ai_multitool/cli/main.py:284-289`

**Problem:** Directory analysis concatenates multiple files into memory:
```python
content = ""
for file_path in [s.file_path for s in structures[:10]]:  # Up to 10 files
    file_content = read_file(file_path)  # Each could be 10MB
    content += f"\n\n# File: {file_path}\n{file_content}"  # Concatenates ALL
```

**Impact:** 10 files × 10MB each = 100MB+ in memory, plus string concatenation overhead.

**Fix:** Add total size limit and implement streaming.

---

### 4. **Synchronous File Operations** (MEDIUM)
**Location:** `ai_multitool/utils/file_utils.py:16-67`

**Problem:** `read_file()` loads entire files synchronously:
```python
return path.read_text(encoding="utf-8")  # Loads entire file at once
```

**Impact:** Large files block the event loop and consume memory instantly.

**Fix:** Implement streaming file readers for large files.

---

### 5. **No Memory Monitoring** (MEDIUM)
**Problem:** No memory usage tracking or limits enforced during operations.

**Impact:** Operations can consume unlimited memory until system freezes.

**Fix:** Add memory monitoring and automatic cleanup.

---

## Memory Usage Estimates

| Operation | Current Behavior | Memory Impact | Risk Level |
|-----------|-----------------|---------------|------------|
| Index 1000 files | Load all at once | ~1GB+ | CRITICAL |
| CLI analyze dir | Concatenate 10 files | ~100MB+ | HIGH |
| Batch embeddings | Process all chunks | ~500MB+ | HIGH |
| File reading | Load entire file | Up to 10MB/file | MEDIUM |

## Recommended Fixes

### Priority 1: Add Limits to Directory Indexing
```python
def index_directory(
    self,
    directory: str,
    pattern: str = "*.md",
    max_files: int = 1000,  # NEW: Limit file count
    max_total_size: int = 100_000_000,  # NEW: Limit total size (100MB)
    batch_size: int = 50,  # NEW: Process in batches
):
```

### Priority 2: Implement Batch Processing
```python
def add_documents(self, documents: List[Document], batch_size: int = 50):
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        # Process batch
        # Clear memory between batches
```

### Priority 3: Add Memory Monitoring
```python
import psutil

def check_memory_usage(threshold: float = 0.8) -> bool:
    """Check if memory usage exceeds threshold."""
    return psutil.virtual_memory().percent > threshold * 100
```

### Priority 4: Implement Streaming File Readers
```python
def read_file_streaming(file_path: str, chunk_size: int = 8192):
    """Read file in chunks to reduce memory usage."""
    with open(file_path, 'r') as f:
        while chunk := f.read(chunk_size):
            yield chunk
```

## Testing Recommendations

1. Test with large directories (1000+ files)
2. Monitor memory usage during operations
3. Test memory cleanup after operations
4. Add memory usage limits to tests
5. Profile memory with `memory_profiler`

## Immediate Actions

1. ✅ Add file count limits to `index_directory()`
2. ✅ Implement batch processing in `add_documents()`
3. ✅ Add total size limits to CLI directory analysis
4. ✅ Add memory monitoring utility
5. ✅ Implement streaming for large file operations
