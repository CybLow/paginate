# Text Search

This guide covers exact text search with `SearchSpec`, including contains/prefix/exact modes, multi-field search, weighted fields, and pipeline integration.

## Basic Usage

### SearchEngine

`SearchEngine` searches in-memory sequences with relevance ranking:

```python
from pypaginate import SearchSpec
from pypaginate.search.engine import SearchEngine

engine = SearchEngine()

products = [
    {"title": "Python Book", "description": "Learn Python programming"},
    {"title": "JavaScript Guide", "description": "Master JS development"},
    {"title": "Go Handbook", "description": "Golang essentials"},
]

spec = SearchSpec(query="python", fields=("title", "description"))
results = engine.apply(products, spec)
# [Python Book] -- matches both title and description
```

### MemorySearchBackend

`MemorySearchBackend` satisfies the `SearchBackend` protocol for pipeline use:

```python
from pypaginate import SearchSpec
from pypaginate.adapters.memory import MemorySearchBackend

backend = MemorySearchBackend()

filtered = backend.apply_search(products, SearchSpec(
    query="python",
    fields=("title", "description"),
))
```

## Search Modes

### CONTAINS (Default)

Matches when the token appears anywhere in the field value:

```python
from pypaginate import SearchSpec, SearchFieldMode

spec = SearchSpec(
    query="python",
    fields=("title",),
    mode=SearchFieldMode.CONTAINS,  # default
)
# "Python Book" matches (contains "python")
# "Learn Python Programming" matches
```

### PREFIX

Matches when the field value starts with the token:

```python
spec = SearchSpec(
    query="py",
    fields=("title",),
    mode=SearchFieldMode.PREFIX,
)
# "Python Book" matches (starts with "py")
# "Learn Python" does NOT match
```

### EXACT

Matches when the normalized field value equals the normalized token:

```python
spec = SearchSpec(
    query="python book",
    fields=("title",),
    mode=SearchFieldMode.EXACT,
)
# "Python Book" matches (normalizes to "python book")
# "Python Book 2nd Edition" does NOT match
```

## Multi-Field Search

Search across multiple fields simultaneously. A result matches if any field contains the token:

```python
from pypaginate import SearchSpec
from pypaginate.search.engine import SearchEngine

engine = SearchEngine()

employees = [
    {"name": "Alice Smith", "email": "alice@corp.com", "department": "Engineering"},
    {"name": "Bob Johnson", "email": "bob@corp.com", "department": "Sales"},
]

spec = SearchSpec(query="alice", fields=("name", "email", "department"))
results = engine.apply(employees, spec)
# [Alice Smith] -- matches in both name and email
```

## Weighted Fields

Assign different weights to fields to control relevance ranking. Higher weights make matches in that field rank higher:

```python
from pypaginate import SearchSpec
from pypaginate.search.engine import SearchEngine

engine = SearchEngine()

products = [
    {"title": "Python", "description": "A snake species"},
    {"title": "Cobra", "description": "A python library for CLI"},
]

# Title matches are twice as important as description matches
spec = SearchSpec(
    query="python",
    fields=("title", "description"),
    weights={"title": 2.0, "description": 1.0},
)
results = engine.apply(products, spec)
# [{"title": "Python", ...}, {"title": "Cobra", ...}]
# "Python" ranks higher (title match with 2x weight)
```

Default weight is `1.0` for fields not specified in the weights dict.

## Multi-Word Queries

Queries with multiple words are tokenized. All tokens must match for an item to be included:

```python
spec = SearchSpec(query="alice smith", fields=("name",))
# Tokenized to ["alice", "smith"]
# Both tokens must match somewhere in the searched fields
```

## Nested Field Access

Search in nested attributes or dictionary keys with dot notation:

```python
spec = SearchSpec(
    query="developer",
    fields=("user.profile.bio",),
)
# Accesses item["user"]["profile"]["bio"] or item.user.profile.bio
```

## Max Results

Limit the number of search results:

```python
spec = SearchSpec(
    query="python",
    fields=("title",),
    max_results=10,  # return at most 10 matches
)
```

## Min Query Length

Skip search for very short queries:

```python
spec = SearchSpec(
    query="a",
    fields=("name",),
    min_length=2,  # skip search if query < 2 chars
)
# Returns all items unfiltered (query too short)
```

## SQLAlchemy Search

`SQLAlchemySearchBackend` generates ILIKE WHERE clauses:

```python
from sqlalchemy import select
from pypaginate import SearchSpec, SearchFieldMode
from pypaginate.adapters.sqlalchemy import SQLAlchemySearchBackend

backend = SQLAlchemySearchBackend()

stmt = select(User)
searched_stmt = backend.apply_search(stmt, SearchSpec(
    query="alice",
    fields=("name", "email"),
))
# SELECT * FROM user
# WHERE (name ILIKE '%alice%' OR email ILIKE '%alice%')
```

Mode affects the ILIKE pattern:

| Mode | Pattern |
|------|---------|
| `CONTAINS` | `%token%` |
| `PREFIX` | `token%` |
| `EXACT` | `token` (no wildcards) |

Multi-word queries generate AND-combined conditions:

```python
# query="alice smith", fields=("name", "email")
# WHERE (name ILIKE '%alice%' OR email ILIKE '%alice%')
#   AND (name ILIKE '%smith%' OR email ILIKE '%smith%')
```

## Pipeline Integration

Combine search with filtering, sorting, and pagination:

```python
from pypaginate import (
    FilterSpec, SortSpec, SortDirection, SearchSpec, OffsetParams,
)
from pypaginate.adapters.memory import (
    MemoryBackend, MemoryFilterBackend, MemorySortBackend, MemorySearchBackend,
)
from pypaginate.engine.paginator import Paginator
from pypaginate.engine.pipeline import SyncPipeline

pipeline = SyncPipeline(
    Paginator(MemoryBackend()),
    filter_backend=MemoryFilterBackend(),
    sort_backend=MemorySortBackend(),
    search_backend=MemorySearchBackend(),
)

page = pipeline.execute(
    users,
    OffsetParams(page=1, limit=20),
    filters=[FilterSpec(field="status", value="active")],
    sorting=[SortSpec(field="name")],
    search=SearchSpec(query="alice", fields=("name", "email")),
)
```

## Text Normalization

Both field values and query tokens are normalized before comparison:

- Unicode normalization (NFC)
- Lowercased
- Whitespace trimmed

This means searches are case-insensitive and accent-aware by default.

## Next Steps

- [Fuzzy Matching](fuzzy.md) -- Approximate matching for typo tolerance
- [Filtering](../filtering/index.md) -- Combine with declarative filters
