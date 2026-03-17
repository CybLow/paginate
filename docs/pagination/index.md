# Pagination

pypaginate provides offset and cursor pagination with a unified `paginate()` entry point.

:::{tip} Quick Decision Guide
- **Small datasets (<100k rows)?** -- Use [Offset Pagination](offset.md)
- **Large datasets or infinite scroll?** -- Use [Cursor/Keyset Pagination](keyset.md)
- **In-memory data?** -- Use [Memory Pagination](memory.md)
:::

## Overview

| Strategy | Best For | Performance |
|----------|----------|-------------|
| [Offset](offset.md) | Small-medium datasets, UI with page numbers | O(n) for deep pages |
| [Cursor/Keyset](keyset.md) | Large datasets, infinite scroll | O(1) constant time |
| [In-Memory](memory.md) | Python collections, cached data | Depends on collection size |

## Universal paginate() Function

The `paginate()` function auto-detects the backend and returns the correct page type based on the params type:

```python
from pypaginate import paginate, OffsetParams, CursorParams

# Offset: OffsetParams -> OffsetPage
page = paginate(users, OffsetParams(page=1, limit=20))
page.total    # int
page.pages    # int

# Cursor: CursorParams -> CursorPage (async)
page = await paginate(query, CursorParams(limit=20, after="abc"), backend=cursor_backend)
page.next_cursor  # str | None
```

## OffsetParams

Immutable parameters for offset-based pagination:

```python
from pypaginate import OffsetParams

params = OffsetParams(page=2, limit=20)

params.page    # 2 (1-indexed)
params.limit   # 20 (items per page, max 1000)
params.offset  # 20 (computed: (page - 1) * limit)
```

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | `int` | `1` | Page number (>= 1) |
| `limit` | `int` | `20` | Items per page (1-1000) |
| `offset` | `int` | computed | Zero-based offset for queries |

## CursorParams

Parameters for cursor-based pagination:

```python
from pypaginate import CursorParams

# First page
params = CursorParams(limit=20)

# Next page
params = CursorParams(limit=20, after="cursor_token")

# Previous page
params = CursorParams(limit=20, before="cursor_token")
```

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `int` | `20` | Items per page (1-1000) |
| `after` | `str \| None` | `None` | Cursor for the next page |
| `before` | `str \| None` | `None` | Cursor for the previous page |

`after` and `before` are mutually exclusive.

## OffsetPage

Result from offset pagination:

```python
from pypaginate import OffsetPage

page.items         # list[T] -- items for this page
page.total         # int -- total count across all pages
page.page          # int -- current page number
page.pages         # int -- total number of pages
page.limit         # int -- items per page
page.has_next      # bool -- True if more pages exist
page.has_previous  # bool -- True if not on first page
```

`OffsetPage` supports iteration and indexing:

```python
for item in page:
    print(item)

first = page[0]
count = len(page)
```

## CursorPage

Result from cursor pagination:

```python
from pypaginate import CursorPage

page.items            # list[T] -- items for this page
page.limit            # int -- items per page
page.has_next         # bool -- True if next page exists
page.has_previous     # bool -- True if previous page exists
page.next_cursor      # str | None -- cursor for the next page
page.previous_cursor  # str | None -- cursor for the previous page
```

No `total` or `page` number -- those are offset-only concepts.

## OverflowStrategy

Controls what happens when page exceeds total pages:

```python
from pypaginate import OverflowStrategy

OverflowStrategy.EMPTY  # return empty page (default)
OverflowStrategy.CLAMP  # clamp to last valid page
```

```python
from pypaginate import paginate, OffsetParams, OverflowStrategy

# Request page 999 of a 10-page dataset
page = paginate(items, OffsetParams(page=999, limit=20), overflow=OverflowStrategy.CLAMP)
# page.page == 10 (clamped to last page)

page = paginate(items, OffsetParams(page=999, limit=20), overflow=OverflowStrategy.EMPTY)
# page.items == [] (empty result)
```

## Quick Comparison

```python
from pypaginate import OffsetParams, CursorParams

# Offset: "Give me page 5 with 20 items"
offset_params = OffsetParams(page=5, limit=20)
# SQL: SELECT ... OFFSET 80 LIMIT 20

# Cursor: "Give me 20 items after this cursor"
cursor_params = CursorParams(limit=20, after="eyJpZCI6MTAwfQ==")
# SQL: WHERE (sort_cols) > (cursor_values) LIMIT 20
```

## Next Steps

- [Offset Pagination](offset.md) -- Detailed guide with examples
- [Cursor/Keyset Pagination](keyset.md) -- For large datasets
- [In-Memory Pagination](memory.md) -- For Python collections
