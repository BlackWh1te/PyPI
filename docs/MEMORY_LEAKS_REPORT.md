# Memory Leak Report for ai-multitool

## Critical Memory Leaks Found

### 1. **CRITICAL: MetricsCollector Unbounded Growth**
**File:** `ai_multitool/utils/metrics.py`  
**Lines:** 57, 142  
**Severity:** CRITICAL

**Issue:** The `MetricsCollector` class maintains an unbounded list `self.metrics` that grows indefinitely with every API call. Each call appends to the list and saves to disk, but the list is never cleared or limited.

```python
# Line 57 - Unbounded list
self.metrics: List[APICallMetrics] = []

# Line 142 - Appends without limit
self.metrics.append(metric)
```

**Impact:** With heavy usage, this list can consume gigabytes of RAM as it stores every API call in memory indefinitely.

**Fix:** Implement a maximum size limit and automatic cleanup:
```python
def __init__(self, metrics_file: str = None, max_metrics: int = 10000):
    self.max_metrics = max_metrics
    self.metrics: List[APICallMetrics] = []

def record_call(self, ...):
    # Add metric
    self.metrics.append(metric)
    
    # Enforce size limit
    if len(self.metrics) > self.max_metrics:
        self.metrics = self.metrics[-self.max_metrics:]
```

---

### 2. **CRITICAL: InMemoryVectorStore Unbounded Growth**
**File:** `ai_multitool/rag/vector_store.py`  
**Lines:** 64-66, 93  
**Severity:** CRITICAL

**Issue:** The `InMemoryVectorStore` has no limit on the number of chunks stored. The numpy embeddings array grows indefinitely using `vstack`, which creates a new array copy each time.

```python
# Lines 64-66 - Unbounded data structures
self.chunks: Dict[str, DocumentChunk] = {}
self.embeddings: np.ndarray = np.zeros((0, dimension), dtype=np.float32)
self.chunk_ids: List[str] = []

# Line 93 - Memory-inefficient growth
self.embeddings = np.vstack([self.embeddings, new_embeddings])
```

**Impact:** With large document sets, this can consume massive amounts of RAM. Each `vstack` operation also creates a full copy of the array, doubling memory temporarily.

**Fix:** Pre-allocate memory or use a maximum size limit:
```python
def __init__(self, dimension: int = 1536, max_chunks: int = 10000):
    self.max_chunks = max_chunks
    self.chunks: Dict[str, DocumentChunk] = {}
    self.chunk_ids: List[str] = []
    self.embeddings = np.zeros((max_chunks, dimension), dtype=np.float32)
    self.current_size = 0

def add(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> None:
    if self.current_size + len(chunks) > self.max_chunks:
        raise MemoryError("Vector store at maximum capacity")
    
    # Add to pre-allocated array
    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        idx = self.current_size + i
        self.embeddings[idx] = emb
        self.chunks[chunk.chunk_id] = chunk
        self.chunk_ids.append(chunk.chunk_id)
    
    self.current_size += len(chunks)
```

---

### 3. **HIGH: Advanced Tool Unbounded Cache**
**File:** `ai_multitool/advanced/base.py`  
**Line:** 118  
**Severity:** HIGH

**Issue:** The advanced tool cache has no size limit and no TTL expiration.

```python
# Line 118 - Unbounded cache
self._cache = {}
```

**Impact:** Long-running processes with advanced tools will accumulate cached results indefinitely.

**Fix:** Add size limit and TTL:
```python
def __init__(self, ...):
    self._cache = {}
    self._cache_timestamps = {}
    self._cache_max_size = 1000
    self._cache_ttl = 3600  # 1 hour

async def _get_cached(self, key):
    if key in self._cache:
        if time.time() - self._cache_timestamps[key] > self._cache_ttl:
            del self._cache[key]
            del self._cache_timestamps[key]
        else:
            return self._cache[key]
    return None

async def _set_cached(self, key, value):
    if len(self._cache) >= self._cache_max_size:
        # Remove oldest
        oldest_key = min(self._cache_timestamps, key=self._cache_timestamps.get)
        del self._cache[oldest_key]
        del self._cache_timestamps[oldest_key]
    
    self._cache[key] = value
    self._cache_timestamps[key] = time.time()
```

---

### 4. **MEDIUM: ResponseCache String Concatenation**
**File:** `ai_multitool/core/llm_client.py`  
**Lines:** 66, 81  
**Severity:** MEDIUM

**Issue:** Cache key creation uses list comprehension and string concatenation which creates temporary strings.

```python
# Lines 66, 81 - Inefficient string operations
key_data = f"{[m.content for m in messages]}_{temperature}_{max_tokens}"
```

**Impact:** For large messages, this creates large temporary strings in memory.

**Fix:** Use more efficient key generation:
```python
def _make_key(self, messages, temperature, max_tokens):
    # Use hash of message contents instead of full content
    content_hash = hashlib.sha256(
        str([m.content for m in messages]).encode()
    ).hexdigest()
    return f"{content_hash}_{temperature}_{max_tokens}"
```

---

### 5. **MEDIUM: File Handle Management**
**File:** Multiple files  
**Severity:** MEDIUM

**Issue:** File operations use `with` statements correctly, but some operations load entire files into memory at once.

**Files affected:**
- `ai_multitool/utils/metrics.py` - Lines 64-66 (loads entire metrics JSON)
- `ai_multitool/rag/vector_store.py` - Lines 205-206, 218-219 (loads entire JSON files)

**Impact:** Large metrics files or vector store files can cause memory spikes.

**Fix:** Implement streaming for large files:
```python
# For metrics, only load recent N entries
def _load_metrics(self, max_recent: int = 1000):
    if self.metrics_file.exists():
        with open(self.metrics_file, 'r') as f:
            data = json.load(f)
            # Only load recent entries
            self.metrics = [APICallMetrics(**m) for m in data[-max_recent:]]
```

---

### 6. **LOW: No Memory Cleanup on Object Destruction**
**File:** Multiple classes  
**Severity:** LOW

**Issue:** Many classes don't implement `__del__` or context managers for proper cleanup.

**Classes affected:**
- `MetricsCollector`
- `InMemoryVectorStore`
- `AdvancedTool`
- `BaseAdapter`

**Impact:** When objects are deleted, cached data and large structures may not be freed immediately.

**Fix:** Add cleanup methods:
```python
class MetricsCollector:
    def __del__(self):
        self.clear()
    
    def clear(self):
        self.metrics.clear()
```

---

## Summary of Memory Leaks

| # | Component | Severity | Memory Impact | Fix Priority |
|---|-----------|----------|---------------|-------------|
| 1 | MetricsCollector | CRITICAL | Very High (unbounded) | IMMEDIATE |
| 2 | InMemoryVectorStore | CRITICAL | Very High (unbounded) | IMMEDIATE |
| 3 | Advanced Tool Cache | HIGH | High (long-running) | HIGH |
| 4 | ResponseCache Keys | MEDIUM | Medium (large messages) | MEDIUM |
| 5 | File Loading | MEDIUM | Medium (large files) | MEDIUM |
| 6 | Missing Cleanup | LOW | Low (GC delays) | LOW |

## Recommended Actions

### Immediate (Critical)
1. **Add size limits to MetricsCollector** - Limit to 10,000 entries max
2. **Add size limits to InMemoryVectorStore** - Limit to 10,000 chunks max
3. **Use pre-allocated numpy arrays** instead of vstack

### High Priority
4. **Add TTL to advanced tool cache** - 1 hour default
5. **Add size limit to advanced tool cache** - 1,000 entries max

### Medium Priority
6. **Optimize cache key generation** - Use hashes instead of full content
7. **Implement streaming for large file loads** - Load only what's needed

### Low Priority
8. **Add cleanup methods** - Implement `__del__` and `clear()` methods
9. **Add context managers** - For proper resource cleanup

## Memory Usage Estimates

Based on typical usage:

- **MetricsCollector**: 1KB per entry × unlimited = **UNBOUNDED**
- **InMemoryVectorStore**: 6KB per chunk × unlimited = **UNBOUNDED**  
- **Advanced Tool Cache**: Variable × unlimited = **UNBOUNDED**

With the proposed fixes:
- **MetricsCollector**: 1KB × 10,000 = **10MB max**
- **InMemoryVectorStore**: 6KB × 10,000 = **60MB max**
- **Advanced Tool Cache**: Variable × 1,000 = **~10MB max**

**Total potential memory usage without fixes:** UNBOUNDED (can consume all available RAM)  
**Total potential memory usage with fixes:** ~80MB max

## Testing Recommendations

1. Run memory profiling with `memory_profiler` on long-running operations
2. Test with large document sets (10,000+ chunks)
3. Test with high-frequency API calls (1000+ calls)
4. Monitor memory growth over time
5. Test cleanup by creating/deleting objects repeatedly

## Monitoring

Add memory usage monitoring:
```python
import psutil
import tracemalloc

# Track memory allocations
tracemalloc.start()

# Monitor process memory
process = psutil.Process()
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024} MB")
```

## Conclusion

The codebase has **2 critical memory leaks** that can cause unlimited memory consumption, along with several high and medium priority issues. Immediate action is required on the MetricsCollector and InMemoryVectorStore to prevent production memory exhaustion.
