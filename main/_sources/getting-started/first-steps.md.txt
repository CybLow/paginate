# First Steps

This guide walks through filtering, sorting, and search using the v0.2 API.

## Filtering with FilterSpec

Use `FilterSpec` to declare filters, then apply them with a backend:

```python
from pypaginate import FilterSpec, OffsetParams
from pypaginate.adapters.memory import MemoryFilterBackend, MemoryBackend
from pypaginate.engine.pipeline import SyncPipeline
from pypaginate.engine.paginator import Paginator

users = [
    {"name": "Alice", "age": 30, "status": "active"},
    {"name": "Bob", "age": 25, "status": "inactive"},
    {"name": "Charlie", "age": 35, "status": "active"},
    {"name": "Diana", "age": 28, "status": "active"},
]

# Define filter specs
filters = [
    FilterSpec(field="status", operator="eq", value="active"),
    FilterSpec(field="age", operator="gte", value=28),
]

# Build a pipeline with filter + pagination backends
pipeline = SyncPipeline(
    Paginator(MemoryBackend()),
    filter_backend=MemoryFilterBackend(),
)

page = pipeline.execute(users, OffsetParams(page=1, limit=10), filters=filters)

print(page.items)  # [{"name": "Alice", ...}, {"name": "Charlie", ...}, {"name": "Diana", ...}]
print(page.total)  # 3
```

For the full list of all 20 operators and nested `And`/`Or` group examples, see [Filtering](../examples/filtering.md).

## Sorting with SortSpec

```python
from pypaginate import SortSpec, SortDirection, OffsetParams
from pypaginate.adapters.memory import MemorySortBackend, MemoryBackend
from pypaginate.engine.pipeline import SyncPipeline
from pypaginate.engine.paginator import Paginator

users = [
    {"name": "Charlie", "age": 35},
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
]

sorting = [
    SortSpec(field="age", direction=SortDirection.DESC),
]

pipeline = SyncPipeline(
    Paginator(MemoryBackend()),
    sort_backend=MemorySortBackend(),
)

page = pipeline.execute(users, OffsetParams(page=1, limit=10), sorting=sorting)

print(page.items)  # [Charlie (35), Alice (30), Bob (25)]
```

### Multi-column sorting

```python
from pypaginate import SortSpec, SortDirection

sorting = [
    SortSpec(field="status"),                              # ASC by default
    SortSpec(field="age", direction=SortDirection.DESC),   # then DESC by age
]
```

## Search with SearchSpec

```python
from pypaginate import SearchSpec, OffsetParams
from pypaginate.adapters.memory import MemorySearchBackend, MemoryBackend
from pypaginate.engine.pipeline import SyncPipeline
from pypaginate.engine.paginator import Paginator

users = [
    {"name": "Alice Smith", "email": "alice@example.com"},
    {"name": "Bob Johnson", "email": "bob@example.com"},
    {"name": "Alicia Keys", "email": "alicia@example.com"},
]

search = SearchSpec(query="alice", fields=("name", "email"))

pipeline = SyncPipeline(
    Paginator(MemoryBackend()),
    search_backend=MemorySearchBackend(),
)

page = pipeline.execute(users, OffsetParams(page=1, limit=10), search=search)

print(page.items)  # [Alice Smith, Alicia Keys] (contains match)
```

### Fuzzy search

```python
from pypaginate import SearchSpec, FuzzyMode

search = SearchSpec(
    query="alic",
    fields=("name",),
    fuzzy=FuzzyMode.FUZZY,
    threshold=75,
)
```

## Combining Everything

The pipeline composes filter, sort, search, and pagination in one call:

```python
from pypaginate import FilterSpec, SortSpec, SearchSpec, OffsetParams, SortDirection
from pypaginate.adapters.memory import (
    MemoryBackend,
    MemoryFilterBackend,
    MemorySortBackend,
    MemorySearchBackend,
)
from pypaginate.engine.pipeline import SyncPipeline
from pypaginate.engine.paginator import Paginator

pipeline = SyncPipeline(
    Paginator(MemoryBackend()),
    filter_backend=MemoryFilterBackend(),
    sort_backend=MemorySortBackend(),
    search_backend=MemorySearchBackend(),
)

page = pipeline.execute(
    users,
    OffsetParams(page=1, limit=10),
    filters=[FilterSpec(field="status", operator="eq", value="active")],
    sorting=[SortSpec(field="name", direction=SortDirection.ASC)],
    search=SearchSpec(query="smith", fields=("name",)),
)
```

## Overflow Handling

See [Basic Pagination: Overflow handling](../examples/basic-pagination.md#overflow-handling) for controlling behavior when `page` exceeds total pages (empty result vs. clamping).

## What's Next?

- [Examples: Basic Pagination](../examples/basic-pagination.md) -- In-memory and SQLAlchemy
- [Examples: Filtering](../examples/filtering.md) -- FilterSpec, And/Or groups
- [Examples: Keyset Pagination](../examples/keyset.md) -- CursorParams and CursorPage
- [Examples: FastAPI](../examples/fastapi.md) -- Full app with dependencies
