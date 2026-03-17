# In-Memory Pagination

Paginate Python collections (lists, tuples, sequences) without a database.

## Basic Usage

The simplest way to paginate in-memory data -- just pass a list and `OffsetParams` to `paginate()`:

```python
from pypaginate import paginate, OffsetParams

users = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Charlie"},
    {"id": 4, "name": "Diana"},
    {"id": 5, "name": "Eve"},
]

page = paginate(users, OffsetParams(page=1, limit=2))

page.items         # [{"id": 1, ...}, {"id": 2, ...}]
page.total         # 5
page.page          # 1
page.pages         # 3
page.has_next      # True
page.has_previous  # False
```

`paginate()` auto-detects Python sequences and uses in-memory slicing -- no backend needed.

## Page Navigation

```python
# Page 1
page1 = paginate(users, OffsetParams(page=1, limit=2))
# page1.items = [Alice, Bob]

# Page 2
page2 = paginate(users, OffsetParams(page=2, limit=2))
# page2.items = [Charlie, Diana]

# Page 3
page3 = paginate(users, OffsetParams(page=3, limit=2))
# page3.items = [Eve]
# page3.has_next = False
```

## Working with Different Types

### Lists

```python
page = paginate(my_list, OffsetParams(page=1, limit=20))
```

### Tuples

```python
items = tuple(range(100))
page = paginate(items, OffsetParams(page=1, limit=20))
```

### Dataclasses / Pydantic Models

```python
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str

users = [User(1, "Alice"), User(2, "Bob"), User(3, "Charlie")]
page = paginate(users, OffsetParams(page=1, limit=2))
# page.items contains User objects
```

## Overflow Handling

```python
from pypaginate import paginate, OffsetParams, OverflowStrategy

items = list(range(50))

# EMPTY (default): empty page for out-of-range
page = paginate(items, OffsetParams(page=999, limit=20))
page.items  # []

# CLAMP: clamp to last valid page
page = paginate(items, OffsetParams(page=999, limit=20), overflow=OverflowStrategy.CLAMP)
page.page   # 3
page.items  # items 40-49
```

## MemoryBackend

For explicit backend usage (e.g., within a `Paginator` or `SyncPipeline`):

```python
from pypaginate import OffsetParams
from pypaginate.adapters.memory import MemoryBackend
from pypaginate.engine.paginator import Paginator

backend = MemoryBackend()
paginator = Paginator(backend)

page = paginator.paginate(users, OffsetParams(page=1, limit=20))
```

`MemoryBackend` counts via `len()` and fetches via list slicing. It accepts any Python `Sequence` (list, tuple, etc.) but rejects strings and bytes.

## Complete Pipeline

Combine filtering, sorting, search, and pagination with `SyncPipeline`:

```python
from pypaginate import FilterSpec, SortSpec, SortDirection, SearchSpec, OffsetParams
from pypaginate.adapters.memory import (
    MemoryBackend,
    MemoryFilterBackend,
    MemorySortBackend,
    MemorySearchBackend,
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
    sorting=[SortSpec(field="name", direction=SortDirection.ASC)],
    search=SearchSpec(query="alice", fields=("name", "email")),
)

page.items         # filtered, sorted, searched, paginated
page.total         # total after filter/search
page.page          # 1
```

## Step-by-Step Pipeline

For explicit control over each step, use `FilterEngine`, `SortEngine`, and `SearchEngine` individually, then pass the result to `paginate()`. See [First Steps](../getting-started/first-steps.md) for a walkthrough.

## Edge Cases

### Empty Input

```python
page = paginate([], OffsetParams(page=1, limit=20))
page.items  # []
page.total  # 0
page.pages  # 0
```

### Single Item

```python
page = paginate([42], OffsetParams(page=1, limit=20))
page.items     # [42]
page.total     # 1
page.pages     # 1
page.has_next  # False
```

### Limit Exceeds Total

```python
items = [1, 2, 3]
page = paginate(items, OffsetParams(page=1, limit=100))
page.items  # [1, 2, 3]
page.total  # 3
page.pages  # 1
```

## Performance

In-memory pagination requires all data to be loaded into memory. For large datasets:

| Approach | Memory | Latency |
|----------|--------|---------|
| `paginate(list, ...)` | O(n) | O(1) per page |
| SQLAlchemy offset | O(page_size) | O(offset) |
| SQLAlchemy cursor | O(page_size) | O(1) |

### Recommendations

- **< 10,000 items**: in-memory pagination is fast and simple
- **10k-100k items**: consider database pagination if data is in a DB
- **> 100k items**: use SQLAlchemy backends to avoid loading all data

## Next Steps

- [Offset Pagination](offset.md) -- Database-backed offset pagination
- [Cursor/Keyset Pagination](keyset.md) -- For large datasets
- [Filtering](../filtering/index.md) -- Combine with declarative filters
- [Sorting](../sorting/index.md) -- Sort before paginating
