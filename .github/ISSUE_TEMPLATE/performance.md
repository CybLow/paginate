---
name: ⚡ Performance Issue
about: Report a performance problem or regression
title: '[PERF] '
labels: ['performance', 'needs-triage']
assignees: ''
---

## Performance Issue Description

<!-- Describe the performance problem -->

## Current Performance

<!-- What is the current performance? Include metrics if available -->

- **Operation**: 
- **Time taken**: 
- **Memory usage**: 
- **Dataset size**: 

## Expected Performance

<!-- What performance do you expect? -->

## Benchmark / Profiling Results

<details>
<summary>Benchmark results (click to expand)</summary>

```
# Include benchmark output here
# You can use: uv run pytest tests/benchmarks --benchmark-only
```

</details>

## Minimal Reproducible Example

```python
import time
from pypaginate import ...

# Code that demonstrates the performance issue
data = [...]  # Sample data

start = time.perf_counter()
# The slow operation
result = ...
elapsed = time.perf_counter() - start

print(f"Time: {elapsed:.4f}s")
```

## Environment

- **pypaginate version**: 
- **Python version**: 
- **Operating System**: 
- **CPU**: 
- **RAM**: 

## Potential Causes

<!-- Optional: If you have ideas about what might be causing the issue -->

## Suggested Optimization

<!-- Optional: If you have ideas on how to improve performance -->

## Additional Context

<!-- Any other context, profiling outputs, or information -->

## Checklist

- [ ] I have verified this is a performance issue, not expected behavior
- [ ] I have provided reproducible benchmark code
- [ ] I have tested with the latest version of pypaginate
