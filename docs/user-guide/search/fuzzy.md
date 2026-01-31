# Fuzzy Matching

Find approximate matches using RapidFuzz.

## What is Fuzzy Matching?

Fuzzy matching finds strings that are similar but not exactly equal:

| Query | Matches |
|-------|---------|
| "alice" | "Alice", "Alicia", "Allice" |
| "python" | "Python", "Pyhton", "pythn" |
| "john" | "John", "Jon", "Johan" |

## Requirements

Install the search extra:

```bash
pip install pypaginate[search]
```

This includes [RapidFuzz](https://github.com/rapidfuzz/RapidFuzz), a fast fuzzy string matching library.

## Basic Usage

```python
from pypaginate.filters.search import MemorySearchService
from pypaginate.filters.search.options import SearchOptions

service = MemorySearchService(
    options=SearchOptions(
        fields=["name"],
        fuzzy_threshold=0.8,  # 80% similarity required
    )
)

users = [
    {"name": "Alice Smith"},
    {"name": "Alicia Jones"},
    {"name": "Bob Wilson"},
]

# Finds both "Alice" and "Alicia"
results = service.search(users, "alice")
```

## Fuzzy Threshold

The `fuzzy_threshold` controls matching strictness:

| Threshold | Behavior |
|-----------|----------|
| 1.0 | Exact match only |
| 0.9 | Very strict (typos may not match) |
| 0.8 | Recommended (catches common typos) |
| 0.7 | Lenient (more false positives) |
| 0.5 | Very lenient (many false positives) |

```python
# Strict matching
options = SearchOptions(fields=["name"], fuzzy_threshold=0.9)

# Lenient matching (for auto-complete)
options = SearchOptions(fields=["name"], fuzzy_threshold=0.6)
```

## How Similarity Works

RapidFuzz uses various algorithms to compute similarity:

```python
# Example similarity scores:
# "Alice" vs "Alice" = 1.0 (exact match)
# "Alice" vs "alice" = 1.0 (case-insensitive)
# "Alice" vs "Alicia" = 0.83
# "Alice" vs "Bob" = 0.0
```

## Fuzzy Search Strategies

### Ratio (Default)

Standard Levenshtein-based similarity:

```python
options = SearchOptions(
    fields=["name"],
    fuzzy_threshold=0.8,
    # Uses ratio by default
)
```

### Partial Ratio

Good for substring matching:

```python
# "Alice" matches "Alice Smith" with high score
# Useful when query is shorter than field value
```

### Token Sort Ratio

Ignores word order:

```python
# "Smith Alice" matches "Alice Smith"
# Good for name searches
```

## Multi-Word Queries

For multi-word queries:

```python
results = service.search(users, "alice smith")

# Matches:
# - "Alice Smith" (exact)
# - "Smith, Alice" (reordered)
# - "Alicia Smyth" (fuzzy on both words)
```

## Combining Fuzzy with Exact

Sometimes you want both:

```python
# First try exact match
results = service.search(items, query)

# If no results, try with lower threshold
if not results:
    lenient_service = MemorySearchService(
        options=SearchOptions(fields=["name"], fuzzy_threshold=0.6)
    )
    results = lenient_service.search(items, query)
```

## Performance Considerations

Fuzzy matching is more CPU-intensive than exact matching:

| Data Size | Exact Match | Fuzzy Match |
|-----------|-------------|-------------|
| 1,000 | < 1ms | ~5ms |
| 10,000 | ~5ms | ~50ms |
| 100,000 | ~50ms | ~500ms |

### Optimization Tips

1. **Filter first**: Reduce dataset before fuzzy search
2. **Limit fields**: Only search necessary fields
3. **Set max_results**: Stop after finding enough matches
4. **Use SQL for large datasets**: Push search to database

```python
# Good: Filter, then fuzzy search
filtered = filter_engine.filter(items, {"category": {"eq": "electronics"}})
results = service.search(filtered, query)  # Searches smaller set
```

## Accent-Insensitive Search

Match regardless of accents:

```python
options = SearchOptions(
    fields=["name"],
    accent_sensitive=False,  # Default
)

users = [
    {"name": "José García"},
    {"name": "Renée Müller"},
]

# "jose" matches "José"
# "rene" matches "Renée"
# "muller" matches "Müller"
results = service.search(users, "jose")
```

Requires the text extra:

```bash
pip install pypaginate[text]
```

## Real-World Examples

### User Search

```python
service = MemorySearchService(
    options=SearchOptions(
        fields=["name", "email", "username"],
        fuzzy_threshold=0.75,
    )
)

# Find user even with typos
results = service.search(users, "jhon")  # Finds "John"
```

### Product Search

```python
service = MemorySearchService(
    options=SearchOptions(
        fields={
            "title": 2.0,       # Prioritize title
            "description": 1.0,
            "brand": 1.5,
        },
        fuzzy_threshold=0.7,  # Lenient for products
    )
)

# "iphone" finds "iPhone 15 Pro"
# "samung" finds "Samsung Galaxy" (typo tolerance)
```

### Address Search

```python
service = MemorySearchService(
    options=SearchOptions(
        fields=["street", "city", "zip"],
        fuzzy_threshold=0.8,
    )
)

# "main stret" finds "Main Street"
```

## SQL Fuzzy Search

For PostgreSQL with trigram extension:

```python
from pypaginate.filters.search import SqlSearchService

# Uses pg_trgm for fuzzy matching
service = SqlSearchService(
    model=User,
    search_fields=["name"],
    options=SearchOptions(fuzzy=True)
)
```

!!! note "Database Support"
    Fuzzy SQL search depends on database capabilities. PostgreSQL supports pg_trgm, SQLite has limited support.

## Next Steps

- [Text Search](text-search.md) - Basic search guide
- [Filtering](../filtering/index.md) - Combine with filters
