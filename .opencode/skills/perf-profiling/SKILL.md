---
name: perf-profiling
description: >
  Advanced Python profiling tools. Covers CPU profiling with py-spy and Scalene,
  memory profiling with memray, line-by-line profiling, and async profiling with yappi.
related:
  - perf-core
  - perf-database
  - perf-ops
---

## ADVANCED PROFILING

Deep performance analysis tools.

---

### CPU Profiling with py-spy

```bash
# Profile running process
py-spy top --pid 12345

# Generate flame graph
py-spy record -o profile.svg --pid 12345

# Profile script directly
py-spy record -o profile.svg -- python my_script.py

# Profile with rate limiting (less overhead)
py-spy record --rate 100 -o profile.svg --pid 12345
```

### Scalene Profiler

```bash
# Run with Scalene (CPU, memory, GPU)
scalene my_script.py

# Generate HTML report
scalene --html --outfile profile.html my_script.py

# Profile specific functions
scalene --profile-only "my_module" my_script.py
```

```python
# Programmatic profiling with Scalene
from scalene import scalene_profiler

@scalene_profiler.profile
def expensive_function():
    # Function to profile
    data = []
    for i in range(1000000):
        data.append(i ** 2)
    return sum(data)
```

### Memory Profiling with memray

```bash
# Record memory allocations
memray run my_script.py

# Generate flame graph
memray flamegraph memray-my_script.py.12345.bin

# Live view of memory usage
memray run --live my_script.py

# Show memory leaks
memray run --trace-python-allocators my_script.py
```

### Line-by-line Profiling

```python
# line_profiler for detailed analysis
from line_profiler import profile


@profile
def slow_function(n: int) -> int:
    total = 0
    for i in range(n):
        total += i ** 2    # Line timing
    return total
```

```bash
# Run with line_profiler
kernprof -l -v my_script.py
```

### Async Profiling

```python
# Profile async code with yappi
import yappi

async def main():
    yappi.set_clock_type("wall")  # Wall clock time for async
    yappi.start()
    
    await run_async_workload()
    
    yappi.stop()
    
    # Get stats
    func_stats = yappi.get_func_stats()
    func_stats.sort("ttot", "desc")  # Sort by total time
    func_stats.print_all()


# Output coroutine-aware statistics
yappi.get_func_stats().save("async_profile.pstat", type="pstat")
```

---

## STANDARD LIBRARY PROFILING

### cProfile

```python
import cProfile
import pstats

# Profile a function
def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()

    # Code to profile
    result = my_function()

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("cumulative")
    stats.print_stats(10)  # Top 10 time consumers

    return result
```

```bash
# Command-line profiling
python -m cProfile -o output.pstat my_script.py

# View with snakeviz (visual)
pip install snakeviz
snakeviz output.pstat
```

### timeit for Microbenchmarks

```python
import timeit

# Time a simple expression
time = timeit.timeit('sum(range(100))', number=10000)
print(f"Average: {time/10000:.6f}s")

# Time a function
def my_func():
    return [x**2 for x in range(1000)]

time = timeit.timeit(my_func, number=1000)
print(f"Average: {time/1000:.6f}s")

# Compare implementations
setup = "data = list(range(10000))"
stmt1 = "[x**2 for x in data]"
stmt2 = "list(map(lambda x: x**2, data))"

t1 = timeit.timeit(stmt1, setup, number=1000)
t2 = timeit.timeit(stmt2, setup, number=1000)
print(f"List comp: {t1:.4f}s, Map: {t2:.4f}s")
```

---

## MEMORY PROFILING

### memory_profiler

```python
from memory_profiler import profile

@profile
def memory_heavy_function():
    data = []
    for i in range(1000000):
        data.append({"id": i, "name": f"item_{i}"})
    return data
```

```bash
# Run with memory profiler
python -m memory_profiler my_script.py

# Track memory over time
mprof run my_script.py
mprof plot  # Generate plot
```

### tracemalloc

```python
import tracemalloc

tracemalloc.start()

# Code to analyze
result = process_data()

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("Top 10 memory allocations:")
for stat in top_stats[:10]:
    print(stat)
```

---

## FLAME GRAPHS

### Generating Flame Graphs

```bash
# With py-spy
py-spy record -o profile.svg -- python my_script.py

# With memray (memory)
memray flamegraph memray-*.bin -o memory.html

# Convert pstat to flame graph
pip install flameprof
flameprof profile.pstat > profile.svg
```

### Interpreting Flame Graphs

```
Reading a flame graph:
- Width = time spent (CPU) or memory allocated
- Y-axis = call stack depth
- Colors = function categorization (usually random)

Look for:
- Wide bars = bottlenecks
- Tall stacks = deep recursion
- Repeated patterns = optimization opportunities
```

---

## QUICK REFERENCE

### Profiling Commands

```bash
# CPU profiling
py-spy record -o flame.svg --pid $PID
scalene --html --outfile report.html script.py
python -m cProfile -o profile.pstat script.py

# Memory profiling
memray run script.py
memray flamegraph memray-*.bin
python -m memory_profiler script.py

# Line profiling
kernprof -l -v script.py

# Async profiling
python -c "import yappi; yappi.start(); ... yappi.get_func_stats().print_all()"
```

### Tool Comparison

| Tool | CPU | Memory | Line | Async | Overhead |
|------|-----|--------|------|-------|----------|
| py-spy | Yes | No | No | No | Very low |
| Scalene | Yes | Yes | Yes | No | Low |
| cProfile | Yes | No | No | No | Medium |
| memray | No | Yes | No | No | Low |
| line_profiler | Yes | No | Yes | No | High |
| yappi | Yes | No | No | Yes | Medium |

### When to Use Each

| Scenario | Recommended Tool |
|----------|------------------|
| Production profiling | py-spy |
| Development profiling | Scalene |
| Memory leaks | memray |
| Line-by-line analysis | line_profiler |
| Async code | yappi |
| Quick microbenchmarks | timeit |
