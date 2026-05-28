# /profile - Performance Profiling Guide

Profile code performance and identify bottlenecks.

## Usage
```
/profile path/to/script.py    # Profile Python script
/profile --memory             # Memory profiling
/profile --flame              # Generate flame graph
/profile cargo run            # Profile Rust binary
```

## What This Skill Does

1. **Run Profiler** - CPU, memory, or I/O profiling
2. **Analyze Results** - Identify hotspots
3. **Visualize** - Flame graphs, call trees
4. **Recommend Fixes** - Optimization suggestions
5. **Verify Improvement** - Before/after comparison

## Python Profiling

### CPU Profiling (cProfile)
```bash
# Profile and save stats
python -m cProfile -o profile.stats script.py

# View stats
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)
"
```

### Line-by-Line (line_profiler)
```python
# Add @profile decorator to functions
@profile
def slow_function():
    ...

# Run with kernprof
# kernprof -l -v script.py
```

### Memory Profiling (memory_profiler)
```python
from memory_profiler import profile

@profile
def memory_heavy():
    ...

# Run: python -m memory_profiler script.py
```

### Async Profiling (py-spy)
```bash
# Profile running process
py-spy record -o profile.svg --pid 12345

# Profile script
py-spy record -o profile.svg -- python script.py
```

## Rust Profiling

### CPU (perf + flamegraph)
```bash
# Install flamegraph
cargo install flamegraph

# Profile
cargo flamegraph --bin myapp

# With perf directly
perf record --call-graph=dwarf ./target/release/myapp
perf report
```

### Memory (heaptrack)
```bash
heaptrack ./target/release/myapp
heaptrack_gui heaptrack.myapp.*.gz
```

## Profile Report Format

```markdown
# Performance Profile: [Script/Binary]

## Summary
| Metric | Value |
|--------|-------|
| Total Time | 5.23s |
| Peak Memory | 256 MB |
| Hottest Function | `process_data` (45%) |

## Top 10 Functions by Time

| Function | Calls | Total Time | % |
|----------|-------|------------|---|
| process_data | 1000 | 2.35s | 45% |
| parse_json | 5000 | 1.12s | 21% |
| db_query | 100 | 0.89s | 17% |

## Flame Graph
![Flame Graph](profile.svg)

## Bottleneck Analysis

### 1. `process_data` - 45% of time
**Issue**: Nested loops with O(n²) complexity
**Location**: module.py:123

**Current**:
```python
for item in items:
    for other in items:  # O(n²)
        if item.matches(other):
            ...
```

**Suggested Fix**:
```python
item_index = {item.key: item for item in items}  # O(n)
for item in items:
    if item.key in item_index:  # O(1) lookup
        ...
```

**Expected Improvement**: ~10x for large datasets

## Memory Issues

### Large Allocation: `load_all_data`
**Issue**: Loading entire file into memory
**Fix**: Use streaming/chunked reading

## Recommendations
1. **High Impact**: Optimize `process_data` loop
2. **Medium Impact**: Cache `parse_json` results
3. **Low Impact**: Batch `db_query` calls
```

## Instructions for Claude

When /profile is invoked:

1. **Identify target** - Script, function, or binary
2. **Choose profiler** - CPU, memory, or both
3. **Run profiling** - Capture performance data
4. **Analyze results** - Find hotspots
5. **Generate visualizations** - Flame graphs if possible
6. **Identify bottlenecks** - Top time consumers
7. **Analyze complexity** - O(n) issues
8. **Suggest optimizations** - Concrete code changes
9. **Estimate improvement** - Expected speedup
