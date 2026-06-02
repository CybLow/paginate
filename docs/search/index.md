# Search

pypaginate provides declarative text search through `SearchSpec` with support for multi-field search, weighted fields, and fuzzy matching (rapidfuzz-based, native).

:::{tip} Quick Start
```python
from pypaginate import SearchSpec

spec = SearchSpec(query="alice", fields=("name", "email"))
```
:::

## Overview

| Feature | Description |
|---------|-------------|
| [Text Search](text-search.md) | Contains, prefix, and exact modes across multiple fields |
| [Fuzzy Matching](fuzzy.md) | Approximate matching with FuzzyMode (rapidfuzz-based, native) |

## Quick Example

```python
from pypaginate import SearchSpec, SearchFieldMode
from pypaginate.search.engine import SearchEngine

engine = SearchEngine()

users = [
    {"name": "Alice Smith", "email": "alice@example.com"},
    {"name": "Bob Johnson", "email": "bob@example.com"},
    {"name": "Alicia Keys", "email": "alicia@example.com"},
]

spec = SearchSpec(query="alice", fields=("name", "email"))
results = engine.apply(users, spec)
# [Alice Smith, Alicia Keys] (ranked by relevance score)
```

## SearchSpec

`SearchSpec` is an immutable Pydantic model describing a search operation:

```python
from pypaginate import SearchSpec, SearchFieldMode, FuzzyMode

spec = SearchSpec(
    query="alice smith",
    fields=("name", "email", "bio"),
    weights={"name": 2.0, "email": 1.0, "bio": 0.5},
    mode=SearchFieldMode.CONTAINS,
    fuzzy=FuzzyMode.EXACT,
    threshold=75,
    min_length=1,
    max_results=100,
)
```

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | required | Search query string (max 500 chars) |
| `fields` | `tuple[str, ...]` | required | Fields to search in |
| `weights` | `dict[str, float] \| None` | `None` | Per-field relevance weights |
| `mode` | `SearchFieldMode` | `CONTAINS` | Matching mode |
| `fuzzy` | `FuzzyMode` | `EXACT` | Fuzzy matching strategy |
| `threshold` | `int` | `75` | Minimum fuzzy score (0-100) |
| `min_length` | `int` | `1` | Minimum query length to search |
| `max_results` | `int \| None` | `None` | Cap on returned results |

## SearchFieldMode Enum

Controls how tokens are matched against field values:

```python
from pypaginate import SearchFieldMode

SearchFieldMode.CONTAINS  # token appears anywhere in the field (default)
SearchFieldMode.PREFIX    # field value starts with the token
SearchFieldMode.EXACT     # field value equals the token exactly
```

## FuzzyMode Enum

Controls the fuzzy matching algorithm:

```python
from pypaginate import FuzzyMode

FuzzyMode.EXACT       # no fuzzy matching, only exact token match (default)
FuzzyMode.FUZZY       # partial_ratio (rapidfuzz-based, substring matching)
FuzzyMode.TOKEN_SORT  # token_sort_ratio (rapidfuzz-based, word-order agnostic)
```

## Backend Support

| Backend | Import | Notes |
|---------|--------|-------|
| In-memory (engine) | `from pypaginate.search.engine import SearchEngine` | Relevance ranking, weights |
| In-memory (backend) | `from pypaginate.adapters.memory import MemorySearchBackend` | Pipeline-compatible |
| SQLAlchemy | `from pypaginate.adapters.sqlalchemy import SQLAlchemySearchBackend` | ILIKE-based search |

## Next Steps

- [Text Search](text-search.md) -- Contains, prefix, exact modes and weights
- [Fuzzy Matching](fuzzy.md) -- FuzzyMode.FUZZY, TOKEN_SORT, and threshold tuning
