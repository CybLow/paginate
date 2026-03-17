# Pagination Strategies

pypaginate supports two pagination strategies: **offset-based** (`OffsetParams` /
`OffsetPage`) and **cursor-based** (`CursorParams` / `CursorPage`). Each strategy
has a dedicated params type and page type with no null leakage between them.

---

## Offset Pagination

Offset pagination uses `LIMIT` and `OFFSET` (or list slicing for in-memory) to return
a fixed window of items.

```python
from pypaginate import paginate, OffsetParams

# In-memory
page = paginate(users_list, OffsetParams(page=2, limit=20))
page.total    # 347
page.page     # 2
page.pages    # 18
page.has_next # True
```

### How It Works

```sql
-- Page 1: first 20 items
SELECT * FROM users ORDER BY id LIMIT 20 OFFSET 0;

-- Page 2: skip 20, get next 20
SELECT * FROM users ORDER BY id LIMIT 20 OFFSET 20;
```

For in-memory lists, pypaginate slices directly: `users[offset:offset + limit]`.

### Advantages

- **Random access** -- jump to any page directly.
- **Exact total count** -- "Page 2 of 18 (347 results)" is trivially available.
- **Simple mental model** -- users understand page numbers.

### Disadvantages

- **Performance degrades with depth** -- the database must scan and discard OFFSET rows.
- **Inconsistent under concurrent writes** -- insertions/deletions shift items between pages.

### OffsetParams Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | `int` | `1` | Page number (1-based) |
| `limit` | `int` | `20` | Items per page (max 1000) |
| `offset` | `int` | computed | Zero-based offset: `(page - 1) * limit` |

The `clamp(total)` method returns new params clamped to valid bounds when `OverflowStrategy.CLAMP` is used.

### OffsetPage Fields

| Field | Type | Description |
|-------|------|-------------|
| `items` | `list[T]` | Items on this page |
| `total` | `int` | Total items across all pages |
| `page` | `int` | Current page number |
| `pages` | `int` | Total number of pages |
| `limit` | `int` | Page size |
| `has_next` | `bool` | Whether a next page exists |
| `has_previous` | `bool` | Whether a previous page exists |

---

## Cursor Pagination

Cursor (keyset) pagination uses an opaque cursor string to resume from a specific
position. pypaginate uses a built-in cursor implementation for
SQL-backed cursor pagination.

```python
from pypaginate import paginate, CursorParams
from pypaginate.adapters.sqlalchemy import SQLAlchemyCursorBackend

backend = SQLAlchemyCursorBackend(session)

# First page -- no cursor
page = await paginate(query, CursorParams(limit=20), backend=backend)

# Next page -- use cursor from previous response
if page.has_next:
    next_page = await paginate(
        query,
        CursorParams(limit=20, after=page.next_cursor),
        backend=backend,
    )
```

### How It Works

```sql
-- First page: no cursor
SELECT * FROM users ORDER BY created_at, id LIMIT 20;

-- Next page: WHERE after cursor position (built-in keyset builder handles this)
SELECT * FROM users
WHERE (created_at, id) > ('2024-01-15', 42)
ORDER BY created_at, id LIMIT 20;
```

The WHERE clause uses an efficient index seek instead of scanning and discarding rows.

### Advantages

- **Constant performance** -- same speed regardless of depth.
- **Stable results** -- insertions don't cause duplicates or gaps.
- **Index-friendly** -- uses efficient index seeks, not full scans.

### Disadvantages

- **No random access** -- cannot jump to "page 50" directly.
- **No total count** -- can only say "has more" (by design: `CursorPage` has no `total` field).
- **Requires ORDER BY** -- the query must have an ORDER BY clause for keyset pagination.

### CursorParams Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | `int` | `20` | Items per page (max 1000) |
| `after` | `str \| None` | `None` | Cursor for forward pagination |
| `before` | `str \| None` | `None` | Cursor for backward pagination |

`after` and `before` are mutually exclusive -- a `ValidationError` is raised if both are provided.

### CursorPage Fields

| Field | Type | Description |
|-------|------|-------------|
| `items` | `list[T]` | Items on this page |
| `limit` | `int` | Page size |
| `has_next` | `bool` | Whether a next page exists |
| `has_previous` | `bool` | Whether a previous page exists |
| `next_cursor` | `str \| None` | Cursor for the next page |
| `previous_cursor` | `str \| None` | Cursor for the previous page |

---

## Side-by-Side Comparison

| Aspect | Offset (`OffsetParams`) | Cursor (`CursorParams`) |
|--------|-------------------------|-------------------------|
| **Performance at depth** | O(offset) -- degrades | O(1) -- constant |
| **Random access** | Yes (any page) | No (sequential only) |
| **Total count** | Yes (`OffsetPage.total`) | No |
| **Consistent under writes** | No (items shift) | Yes (stable) |
| **UI pattern** | Page numbers | Infinite scroll, "Load more" |
| **Backend requirement** | `PaginationBackend` or `SyncPaginationBackend` | `CursorBackend` (async only) |
| **In-memory support** | Yes (list slicing) | No (requires database) |

---

## Choosing a Strategy

```{mermaid}
flowchart TD
    Start([Need pagination?]) --> Source{Data source?}

    Source -->|In-memory list| Offset["Use OffsetParams"]
    Source -->|SQLAlchemy query| Size{Dataset size?}

    Size -->|"< 10K rows"| UI{UI pattern?}
    Size -->|"> 10K rows"| Cursor["Use CursorParams"]

    UI -->|Page numbers| Offset
    UI -->|Infinite scroll| Cursor
    UI -->|Load more button| Cursor

    Offset --> Done([Done])
    Cursor --> Done
```

| Situation | Recommendation |
|-----------|----------------|
| Admin panel with page numbers | `OffsetParams` |
| Social media feed / infinite scroll | `CursorParams` |
| API for mobile apps | `CursorParams` (predictable performance) |
| Reports needing exact counts | `OffsetParams` |
| Large product catalog | `CursorParams` |
| Small filtered dataset | `OffsetParams` |

---

## Overflow Handling (Offset Only)

When a user requests a page beyond the total, two strategies are available:

```python
from pypaginate import paginate, OffsetParams
from pypaginate.domain.enums import OverflowStrategy

# EMPTY (default): return empty page with correct metadata
page = paginate(items, OffsetParams(page=999), overflow=OverflowStrategy.EMPTY)
# page.items == [], page.total == 50, page.page == 999

# CLAMP: silently clamp to last valid page
page = paginate(items, OffsetParams(page=999), overflow=OverflowStrategy.CLAMP)
# page.items == [...last page items...], page.page == 3
```
