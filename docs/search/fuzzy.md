# Fuzzy Matching

Fuzzy matching finds approximate string matches, handling typos, misspellings, and word-order variations.

## Requirements

Install the search extra for rapidfuzz support:

```bash
uv add pypaginate[search]
```

This includes [rapidfuzz](https://github.com/rapidfuzz/RapidFuzz), a fast fuzzy string matching library. Without rapidfuzz, fuzzy matching falls back to simple substring checks.

## FuzzyMode

`FuzzyMode` controls the fuzzy matching algorithm:

```python
from pypaginate import FuzzyMode

FuzzyMode.EXACT       # no fuzzy matching (default)
FuzzyMode.FUZZY       # partial_ratio -- good for substring typos
FuzzyMode.TOKEN_SORT  # token_sort_ratio -- word-order agnostic
```

## Basic Usage

### FuzzyMode.FUZZY

Uses rapidfuzz's `partial_ratio` for substring-aware fuzzy matching:

```python
from pypaginate import SearchSpec, FuzzyMode
from pypaginate.search.engine import SearchEngine

engine = SearchEngine()

users = [
    {"name": "Alice Smith"},
    {"name": "Alicia Jones"},
    {"name": "Bob Wilson"},
]

spec = SearchSpec(
    query="alice",
    fields=("name",),
    fuzzy=FuzzyMode.FUZZY,
    threshold=75,
)
results = engine.apply(users, spec)
# [Alice Smith, Alicia Jones] -- "Alicia" fuzzy-matches "alice"
```

### FuzzyMode.TOKEN_SORT

Uses rapidfuzz's `token_sort_ratio` for word-order-agnostic matching:

```python
spec = SearchSpec(
    query="smith alice",
    fields=("name",),
    fuzzy=FuzzyMode.TOKEN_SORT,
    threshold=75,
)
results = engine.apply(users, spec)
# [Alice Smith] -- word order doesn't matter
```

`TOKEN_SORT` treats the entire query as a single unit (no tokenization), normalizes it, and compares against each field value using token-sorted ratio.

## Threshold

The `threshold` parameter (0-100) controls how strict fuzzy matching is:

```python
from pypaginate import SearchSpec, FuzzyMode

# Strict: only very close matches
SearchSpec(query="alice", fields=("name",), fuzzy=FuzzyMode.FUZZY, threshold=90)

# Moderate (default): catches common typos
SearchSpec(query="alice", fields=("name",), fuzzy=FuzzyMode.FUZZY, threshold=75)

# Lenient: more false positives, fewer misses
SearchSpec(query="alice", fields=("name",), fuzzy=FuzzyMode.FUZZY, threshold=60)
```

| Threshold | Behavior | Use Case |
|-----------|----------|----------|
| 90-100 | Very strict | Exact-ish matching |
| 75-89 | Moderate | General search (recommended) |
| 60-74 | Lenient | Autocomplete, "did you mean" |
| < 60 | Very lenient | Broad discovery |

## Scoring and Ranking

Results are ranked by fuzzy score (highest first):

```python
from pypaginate import SearchSpec, FuzzyMode
from pypaginate.search.engine import SearchEngine

engine = SearchEngine()

users = [
    {"name": "Alice"},       # score ~100 (exact)
    {"name": "Alicia"},      # score ~83 (close)
    {"name": "Alexandra"},   # score ~60 (distant)
    {"name": "Bob"},         # score 0 (no match, filtered out)
]

spec = SearchSpec(
    query="alice",
    fields=("name",),
    fuzzy=FuzzyMode.FUZZY,
    threshold=55,
)
results = engine.apply(users, spec)
# [Alice, Alicia, Alexandra] -- ordered by descending score
```

## Weighted Fuzzy Search

Combine fuzzy matching with field weights for relevance-tuned results:

```python
from pypaginate import SearchSpec, FuzzyMode

spec = SearchSpec(
    query="jhon",  # typo for "john"
    fields=("name", "email", "bio"),
    weights={"name": 3.0, "email": 2.0, "bio": 1.0},
    fuzzy=FuzzyMode.FUZZY,
    threshold=70,
)
# Name matches rank 3x higher than bio matches
```

## How the Algorithms Work

### partial_ratio (FuzzyMode.FUZZY)

Compares the shorter string as a sliding window against the longer string. Good for matching substrings with typos:

```
"alice" vs "Alice Smith"  -> high score (substring match)
"alce"  vs "Alice Smith"  -> moderate score (typo)
"alice" vs "Bob"          -> low score (no similarity)
```

### token_sort_ratio (FuzzyMode.TOKEN_SORT)

Sorts the tokens alphabetically before comparing, making word order irrelevant:

```
"smith alice"  vs "Alice Smith"  -> high score (same words)
"alice s"      vs "Alice Smith"  -> moderate score (partial)
```

### Fallback (no rapidfuzz)

Without rapidfuzz installed, both modes fall back to simple substring containment:

```python
# Without rapidfuzz:
# FuzzyMode.FUZZY -> returns 100 if query is a substring, else 0
# FuzzyMode.TOKEN_SORT -> same fallback
```

## Multi-Field Fuzzy Search

When searching multiple fields with fuzzy mode, the engine picks the best matching field per token:

```python
from pypaginate import SearchSpec, FuzzyMode

spec = SearchSpec(
    query="jhon",
    fields=("name", "email"),
    fuzzy=FuzzyMode.FUZZY,
    threshold=70,
)
# For each item, checks both name and email
# Uses the highest-scoring field match for ranking
```

## Pipeline Integration

```python
from pypaginate import SearchSpec, FuzzyMode, OffsetParams
from pypaginate.adapters.memory import MemoryBackend, MemorySearchBackend
from pypaginate.engine.paginator import Paginator
from pypaginate.engine.pipeline import SyncPipeline

pipeline = SyncPipeline(
    Paginator(MemoryBackend()),
    search_backend=MemorySearchBackend(),
)

page = pipeline.execute(
    users,
    OffsetParams(page=1, limit=20),
    search=SearchSpec(
        query="jhon",
        fields=("name", "email"),
        fuzzy=FuzzyMode.FUZZY,
        threshold=70,
    ),
)
```

## Real-World Examples

### User Search with Typo Tolerance

```python
spec = SearchSpec(
    query="jhon smth",  # typos in both words
    fields=("name",),
    fuzzy=FuzzyMode.FUZZY,
    threshold=70,
)
# Finds "John Smith"
```

### Product Search

```python
spec = SearchSpec(
    query="samung galxy",  # misspelled brand and product
    fields=("title", "brand"),
    weights={"title": 1.0, "brand": 2.0},
    fuzzy=FuzzyMode.FUZZY,
    threshold=65,
)
# Finds "Samsung Galaxy"
```

### Name Search (Order-Agnostic)

```python
spec = SearchSpec(
    query="doe jane",
    fields=("full_name",),
    fuzzy=FuzzyMode.TOKEN_SORT,
    threshold=80,
)
# Finds "Jane Doe" -- word order doesn't matter
```

## Performance Tips

1. **Filter first** -- reduce the dataset before fuzzy search
2. **Set `max_results`** -- stop ranking after enough matches
3. **Raise threshold** -- higher threshold means fewer comparisons pass
4. **Limit fields** -- only search relevant fields
5. **Use SQLAlchemy for large datasets** -- fuzzy search is CPU-intensive in memory

```python
# Efficient: filter, then fuzzy search a smaller set
from pypaginate import FilterSpec

filtered = filter_backend.apply_filters(users, [
    FilterSpec(field="status", value="active"),
])
results = engine.apply(filtered, fuzzy_spec)
```

## Next Steps

- [Text Search](text-search.md) -- Exact text search modes
- [Filtering](../filtering/index.md) -- Combine with declarative filters
