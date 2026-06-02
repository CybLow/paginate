# Search & Relevance

pypaginate provides a search engine that tokenizes queries, matches them against
fields, scores results by relevance, and supports rapidfuzz-based fuzzy matching
(reimplemented natively in the bundled engine, always available).

---

## Search Pipeline

```{mermaid}
graph LR
    Q["SearchSpec"] --> T["Tokenize query"]
    T --> N["normalize_text()"]
    N --> M["Match & score per item"]
    M --> R["Sort by score (descending)"]
    R --> O["Ranked results"]
```

1. **Parse** -- the engine tokenizes the query into tokens (handles quotes, whitespace).
2. **Normalize** -- each token and field value is Unicode-normalized (lowercased, accents removed).
3. **Match** -- each item is scored across the specified fields.
4. **Rank** -- items are sorted by score (highest first), then optionally truncated by `max_results`.

---

## SearchSpec

A `SearchSpec` is an immutable Pydantic model:

```python
from pypaginate import SearchSpec
from pypaginate.domain.enums import FuzzyMode, SearchFieldMode

# Basic search
SearchSpec(query="john doe", fields=("name", "email"))

# Fuzzy search with weights
SearchSpec(
    query="jhn",
    fields=("name", "email"),
    weights={"name": 2.0, "email": 1.0},
    fuzzy=FuzzyMode.FUZZY,
    threshold=75,
)

# Token-sort matching (word-order agnostic)
SearchSpec(
    query="doe john",
    fields=("name",),
    fuzzy=FuzzyMode.TOKEN_SORT,
)
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `query` | `str` | required | Search query (max 500 characters) |
| `fields` | `tuple[str, ...]` | required | Fields to search |
| `weights` | `dict[str, float] \| None` | `None` | Per-field weight multipliers |
| `mode` | `SearchFieldMode` | `CONTAINS` | How tokens match field values |
| `fuzzy` | `FuzzyMode` | `EXACT` | Fuzzy matching strategy |
| `threshold` | `int` | `75` | Minimum fuzzy score (0-100) |
| `min_length` | `int` | `1` | Minimum query length (below this, all items returned) |
| `max_results` | `int \| None` | `None` | Limit number of results |

---

## Search Modes (SearchFieldMode)

| Mode | Behavior | Example |
|------|----------|---------|
| `EXACT` | Field value must equal the normalized token | `"john" matches "john"` only |
| `PREFIX` | Field value must start with the token | `"joh" matches "john", "johnson"` |
| `CONTAINS` | Token must appear anywhere in the field value | `"ohn" matches "john", "johnson"` |

---

## Fuzzy Modes (FuzzyMode)

| Mode | Algorithm | Use Case |
|------|-----------|----------|
| `EXACT` | No fuzzy -- exact/prefix/contains matching only | Fast, precise results |
| `FUZZY` | `partial_ratio` (substring matching) | Typo tolerance |
| `TOKEN_SORT` | `token_sort_ratio` (word-order agnostic) | "John Doe" matches "Doe John" |

Both fuzzy modes are implemented natively in the bundled engine (a Rust
reimplementation of rapidfuzz's `partial_ratio` / `token_sort_ratio`) and are always
available -- no extra dependency to install.

---

## Scoring

### Exact Scoring

In exact mode (`FuzzyMode.EXACT`), each matching token contributes a fixed score of 100.
All tokens must match (AND logic) -- if any token fails to match any field, the item
scores 0.

### Fuzzy Scoring

In fuzzy mode, `partial_ratio` returns a score from 0-100 for each
(token, field_value) pair. Only scores at or above the `threshold` count as a match.
A score below threshold is treated as 0 (no match).

### Weighted Scoring

When `weights` are provided, each field's score is multiplied by its weight:

```python
SearchSpec(
    query="john",
    fields=("name", "email", "bio"),
    weights={"name": 3.0, "email": 1.0, "bio": 0.5},
)
```

For multi-field search, the engine finds the **best weighted score** across all fields
for each token, then sums across tokens.

### Scoring Example

Given `weights={"name": 2.0, "email": 1.0}` and query `"john"`:

| Item | Name Score | Email Score | Best Weighted | Total |
|------|-----------|-------------|---------------|-------|
| `name="John Doe", email="john@x.com"` | 100 * 2.0 = 200 | 100 * 1.0 = 100 | 200 | 200 |
| `name="Jane", email="john.doe@x.com"` | 0 | 100 * 1.0 = 100 | 100 | 100 |
| `name="Bob", email="bob@x.com"` | 0 | 0 | 0 | 0 (excluded) |

---

## Single-Field vs Multi-Field

The `SearchEngine` has two optimized paths:

- **Single field** -- avoids list allocation per item, direct accessor call.
- **Multi-field** -- extracts and normalizes all field values, finds best weighted match.

```python
# Single field (fast path)
SearchSpec(query="john", fields=("name",))

# Multi-field with weights
SearchSpec(query="john", fields=("name", "email", "bio"), weights={"name": 2.0})
```

---

## Text Normalization

All text (queries and field values) is normalized before matching:

```python
from pypaginate.text.normalize import normalize_text

normalize_text("Cafe\u0301")   # "cafe"  (accent removed, lowercased)
normalize_text("HELLO World")  # "hello world"
```

Normalization includes:
- Unicode NFKD decomposition
- Accent/diacritic removal
- Lowercase conversion

This makes search accent-insensitive and case-insensitive by default.

---

## In-Memory Search

```python
from pypaginate.search.engine import SearchEngine
from pypaginate import SearchSpec

engine = SearchEngine()
results = engine.apply(
    items,
    SearchSpec(query="john doe", fields=("name", "email")),
)
# Returns items sorted by relevance score (highest first)
```

---

## SQLAlchemy Search

The `SQLAlchemySearchBackend` translates `SearchSpec` into SQL LIKE/ILIKE conditions:

```python
from pypaginate.adapters.sqlalchemy import SQLAlchemySearchBackend

backend = SQLAlchemySearchBackend()
modified_query = backend.apply_search(select(User), search_spec)
```

---

## Pipeline Integration

Search integrates with the pipeline alongside filters and sorting:

```python
from pypaginate.engine.pipeline import AsyncPipeline
from pypaginate.engine.paginator import AsyncPaginator
from pypaginate.adapters.sqlalchemy import (
    SQLAlchemyBackend, SQLAlchemyFilterBackend,
    SQLAlchemySortBackend, SQLAlchemySearchBackend,
)
from pypaginate import OffsetParams, FilterSpec, SortSpec, SearchSpec

pipeline = AsyncPipeline(
    AsyncPaginator(SQLAlchemyBackend(session)),
    filter_backend=SQLAlchemyFilterBackend(),
    sort_backend=SQLAlchemySortBackend(),
    search_backend=SQLAlchemySearchBackend(),
)

result = await pipeline.execute(
    select(User),
    OffsetParams(page=1, limit=20),
    filters=[FilterSpec(field="status", value="active")],
    sorting=[SortSpec(field="name")],
    search=SearchSpec(query="john", fields=("name", "email")),
)
```

The pipeline applies operations in order: **filter -> sort -> search -> paginate**.

---

## Performance Tips

- Search fewer fields for faster results.
- Use `EXACT` mode when fuzzy matching is not needed.
- Set `max_results` to limit scoring work on large datasets.
- For SQL backends, ensure searched columns have appropriate indexes (GIN for
  PostgreSQL full-text, trigram for fuzzy).
