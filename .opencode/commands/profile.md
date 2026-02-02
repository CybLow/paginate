---
description: Profile code performance - CPU, memory, and execution time analysis
agent: performance-profiler
---

# /profile

Analyze code performance using profiling tools.

## Usage

```
/profile [type] [target]
```

## Profile Types

### CPU Profiling

```
/profile cpu src/paginator.py     # Profile CPU usage
/profile cpu tests/benchmark.py   # Profile benchmarks
```

### Memory Profiling

```
/profile memory script.py         # Profile memory usage
/profile memory --leaks           # Focus on memory leaks
```

### Benchmarks

```
/profile benchmark                # Run all benchmarks
/profile benchmark paginate       # Run specific benchmark
/profile benchmark --compare      # Compare to baseline
```

### Full Analysis

```
/profile analyze src/             # Full performance analysis
/profile hotspots                 # Find performance hotspots
```

## Examples

```
/profile cpu the pagination function
/profile memory for memory leaks in the cache
/profile benchmark the filter operations
/profile why is get_users slow
/profile analyze the database queries
```

## What the Profiler Does

1. **Profiles** CPU and memory usage
2. **Identifies** bottlenecks and hot paths
3. **Analyzes** database queries
4. **Recommends** optimizations

## Tools Used

| Tool | Purpose |
|------|---------|
| py-spy | CPU flame graphs |
| memray | Memory profiling |
| scalene | CPU + Memory + GPU |
| pytest-benchmark | Timing benchmarks |

## Output

The profiler provides:
- Flame graphs (SVG/HTML)
- Hot function analysis
- Memory allocation reports
- Query analysis (if PostgreSQL)
- Optimization recommendations

## Quick Commands

```bash
# Benchmarks
uv run pytest --benchmark-only -v

# CPU profile
py-spy record -o profile.svg -- python script.py

# Memory profile
uv run memray run -o mem.bin script.py
uv run memray flamegraph mem.bin
```

## Related

- `/benchmark` - Run performance benchmarks
- `@performance-profiler` - Mention in conversation
- Skills: `perf-core`, `perf-profiling`, `perf-database`
