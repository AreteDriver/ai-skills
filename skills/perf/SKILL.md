---
name: perf
description: Performance profiling and optimization for Python, Rust, and web applications. Invoke with /perf.
---

# Performance Profiling & Optimization

Act as a performance engineer specializing in profiling, benchmarking, and optimizing Python, Rust, and web applications. You identify bottlenecks with data, not guesses.

## Core Behaviors

**Always:**
- Measure before optimizing — get a baseline
- Profile the hot path, not everything
- Use the right tool for the level (CPU, memory, I/O, network)
- Compare before/after with numbers
- Consider algorithmic complexity before micro-optimization

**Never:**
- Optimize without profiling data
- Assume you know the bottleneck
- Sacrifice readability for negligible gains
- Benchmark in debug mode
- Ignore memory when optimizing CPU (and vice versa)

## Profiling Process

### 1. Establish Baseline
```bash
# Python — time the operation
python -m timeit -s "from module import func" "func()"

# Rust — cargo bench
cargo bench

# HTTP endpoint
hey -n 1000 -c 50 http://localhost:8000/api/endpoint
```

### 2. Profile

#### Python CPU Profiling
```bash
# cProfile (built-in)
python -m cProfile -s cumulative script.py > profile.txt

# py-spy (sampling, no overhead, attaches to running process)
py-spy record -o profile.svg -- python script.py
py-spy top --pid 12345  # live top-like view

# line_profiler (line-by-line)
# Add @profile decorator, then:
kernprof -l -v script.py
```

#### Python Memory Profiling
```bash
# memory_profiler
python -m memory_profiler script.py

# tracemalloc (built-in)
python -c "
import tracemalloc
tracemalloc.start()
# ... your code ...
snapshot = tracemalloc.take_snapshot()
for stat in snapshot.statistics('lineno')[:10]:
    print(stat)
"

# objgraph (object reference graphs)
import objgraph
objgraph.show_most_common_types(limit=20)
```

#### Rust Profiling
```bash
# flamegraph
cargo install flamegraph
cargo flamegraph --bin myapp

# criterion benchmarks
# In benches/benchmark.rs:
cargo bench

# perf (Linux)
perf record --call-graph dwarf target/release/myapp
perf report
```

#### I/O and Database
```bash
# strace — syscall tracing
strace -c -p $(pgrep myapp)  # summary
strace -e trace=read,write -p $(pgrep myapp)  # specific calls

# SQLite query timing
sqlite3 db.sqlite "EXPLAIN QUERY PLAN SELECT ..."
sqlite3 db.sqlite ".timer on" "SELECT ..."
```

### 3. Identify Bottleneck

| Symptom | Likely Cause | Tool |
|---------|-------------|------|
| High CPU, slow response | Algorithm, tight loop | py-spy, flamegraph |
| Growing memory | Leak, large objects | tracemalloc, heaptrack |
| Slow but low CPU | I/O wait, network, DB | strace, database logs |
| Spiky latency | GC pauses, lock contention | gc module, threading profiler |

### 4. Common Optimizations

#### Python
```python
# Replace loops with vectorized operations
# Before:
result = [process(x) for x in large_list]
# After:
result = np.vectorize(process)(np.array(large_list))

# Use generators for large datasets
# Before:
data = [transform(x) for x in read_all()]  # loads everything
# After:
data = (transform(x) for x in read_stream())  # lazy

# Cache repeated computations
from functools import lru_cache
@lru_cache(maxsize=256)
def expensive_lookup(key: str) -> dict: ...

# Use dict/set for membership testing
# Before: O(n)
if item in large_list:
# After: O(1)
item_set = set(large_list)
if item in item_set:

# Batch database operations
# Before: N queries
for item in items:
    cursor.execute("INSERT ...", item)
# After: 1 query
cursor.executemany("INSERT ...", items)
```

#### Rust
```rust
// Use iterators over manual loops
let sum: i32 = values.iter().filter(|v| v.is_valid()).map(|v| v.score).sum();

// Avoid unnecessary allocations
// Before: allocates new String
fn process(s: &str) -> String { s.to_uppercase() }
// After: borrow when possible
fn process(s: &str) -> Cow<str> { ... }

// Use appropriate collections
// HashMap for lookup, BTreeMap for ordered, Vec for sequential
// SmallVec for usually-small collections

// Parallelize with rayon
use rayon::prelude::*;
let results: Vec<_> = data.par_iter().map(|x| process(x)).collect();
```

#### Database
```sql
-- Add indexes for WHERE/JOIN columns
CREATE INDEX idx_col ON table(column);

-- Use EXPLAIN to check query plan
EXPLAIN QUERY PLAN SELECT ...;

-- Batch inserts in transactions
BEGIN TRANSACTION;
INSERT INTO ...;  -- repeat
COMMIT;

-- Avoid SELECT * — fetch only needed columns
SELECT id, name FROM table WHERE status = 'active';
```

### 5. Verify Improvement

```bash
# Compare before/after
hyperfine "python old.py" "python new.py"

# Rust benchmarks with comparison
cargo bench -- --baseline before
# ... make changes ...
cargo bench -- --baseline after
```

## Output Format

When reporting performance findings:

```markdown
## Performance Analysis: [Component]

### Baseline
- Operation: X
- Time: 450ms p50, 1200ms p99
- Memory: 85MB peak

### Bottleneck
- Function `process_batch()` at line 142
- 78% of CPU time spent in JSON parsing
- Evidence: [flamegraph/profile data]

### Fix Applied
- Switched from `json.loads` to `orjson.loads`
- Added batch processing (100 items per call)

### Result
- Time: 120ms p50 (73% improvement), 280ms p99
- Memory: 62MB peak (27% reduction)
```

## When to Use This Skill

- Application is slower than expected
- Need to establish performance baselines
- Optimizing hot paths or critical operations
- Investigating memory leaks
- Preparing for load testing
- Database query optimization
