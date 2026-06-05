# Fuzzy Matching

Fuzzy matching finds approximate string matches, handling typos, misspellings, and word-order variations.

Fuzzy matching is built into the native engine and always available -- no extra dependency
to install. It uses **trigram similarity** (the same model as PostgreSQL's `pg_trgm`): each
string is split into overlapping 3-character chunks and similarity is the overlap of the two
trigram sets. This is fast (no edit-distance scan), length-normalized, and
transposition-tolerant -- and strongest on names, titles, and multi-word text (it is weaker
on very short single-word typos than the old edit-distance scoring).

## FuzzyMode

`FuzzyMode` controls the fuzzy matching algorithm:

```python
from pypaginate import FuzzyMode

FuzzyMode.EXACT       # no fuzzy matching (default)
FuzzyMode.FUZZY       # trigram containment -- query trigrams found in the field
FuzzyMode.TOKEN_SORT  # trigram Jaccard -- word-order agnostic
```

## Basic Usage

### FuzzyMode.FUZZY

Uses `partial_ratio` for substring-aware fuzzy matching:

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

Uses `token_sort_ratio` for word-order-agnostic matching:

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

The `threshold` parameter (0-100) is the minimum **trigram similarity** to count as a match.
Trigram scores run lower than the old edit-distance scores, so the default is **30** (matching
pg_trgm's 0.3). Tune it to your data:

```python
from pypaginate import SearchSpec, FuzzyMode

# Strict: only very close matches
SearchSpec(query="alice", fields=("name",), fuzzy=FuzzyMode.FUZZY, threshold=60)

# Moderate (default): catches common typos
SearchSpec(query="alice", fields=("name",), fuzzy=FuzzyMode.FUZZY, threshold=30)

# Lenient: more false positives, fewer misses
SearchSpec(query="alice", fields=("name",), fuzzy=FuzzyMode.FUZZY, threshold=20)
```

| Threshold | Behavior | Use Case |
|-----------|----------|----------|
| 60-100 | Very strict | Near-exact matching |
| 30-59 | Moderate | General search (recommended) |
| 20-29 | Lenient | Autocomplete, "did you mean" |
| < 20 | Very lenient | Broad discovery |

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

Both modes work on **trigram sets**. A string is lowercased, split on non-alphanumeric
boundaries, each word padded with two leading and one trailing space, then sliced into
3-character chunks: `"cat"` -> `{"  c", " ca", "cat", "at "}`.

### Containment (FuzzyMode.FUZZY)

`|query ∩ field| / |query|` -- the fraction of the query's trigrams present in the field. Not
diluted by field length, so a short query still scores high inside a long title:

```
"alice" vs "Alice Smith"  -> high score (all query trigrams present)
"alce"  vs "Alice Smith"  -> moderate score (typo drops a few trigrams)
"alice" vs "Bob"          -> 0 (no shared trigrams)
```

### Jaccard (FuzzyMode.TOKEN_SORT)

`|query ∩ field| / |query ∪ field|` -- a symmetric set overlap, so word order is irrelevant
(the trigram set is the same either way):

```
"smith alice"  vs "Alice Smith"  -> high score (identical word set)
"alice s"      vs "Alice Smith"  -> moderate score (partial overlap)
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
