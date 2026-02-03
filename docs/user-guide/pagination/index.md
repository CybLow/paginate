# Pagination

pypaginate provides multiple pagination strategies to suit different use cases.

!!! tip "Quick Decision Guide"
    - **Small datasets (<100k rows)?** → Use [Offset Pagination](offset.md)
    - **Large datasets or infinite scroll?** → Use [Keyset Pagination](keyset.md)
    - **In-memory data?** → Use [Memory Pagination](memory.md)

## Overview

| Strategy | Best For | Performance |
|----------|----------|-------------|
| [Offset](offset.md) | Small-medium datasets, UI with page numbers | O(n) for deep pages |
| [Keyset/Cursor](keyset.md) | Large datasets, infinite scroll | O(1) constant time |
| [In-Memory](memory.md) | Python collections, cached data | Depends on collection size |

## Choosing a Strategy

### Use Offset Pagination When:

- You need page numbers in your UI
- Your dataset is small to medium (< 100k rows)
- Users rarely go beyond page 10
- You need random access to any page

### Use Keyset/Cursor Pagination When:

- You have large datasets (100k+ rows)
- You're building infinite scroll
- Performance on deep pages matters
- You can use opaque cursors instead of page numbers

### Use In-Memory Pagination When:

- Data is already loaded in Python
- You're processing files or API responses
- You need to paginate cached data
- No database is involved

## Quick Comparison

```python
from pypaginate import PageParams
from pypaginate.core import KeysetPageParams

# Offset: "Give me page 5 with 20 items"
offset_params = PageParams(page=5, limit=20)
# SQL: OFFSET 80 LIMIT 20

# Keyset: "Give me 20 items after this cursor"
keyset_params = KeysetPageParams(limit=20, after="eyJpZCI6MTAwfQ==")
# SQL: WHERE id > 100 LIMIT 20
```

## Core Concepts

### PageParams

Immutable parameters for offset-based pagination:

```python
from pypaginate import PageParams

params = PageParams(page=1, limit=20)

# Properties
params.page    # Current page (1-indexed)
params.limit   # Items per page
params.offset  # Calculated offset: (page - 1) * limit
```

### Page[T]

Generic container for paginated results:

```python
from pypaginate import Page

# A Page contains:
page.items        # List of items for current page
page.total        # Total count across all pages
page.page         # Current page number
page.limit        # Items per page
page.pages        # Total number of pages (calculated)
page.has_next     # True if there are more pages
page.has_previous # True if not on first page
```

### KeysetPageParams

Parameters for cursor-based pagination:

```python
from pypaginate.core import KeysetPageParams

# First page
params = KeysetPageParams(limit=20)

# Next page using cursor
params = KeysetPageParams(limit=20, after="cursor_token")

# Previous page
params = KeysetPageParams(limit=20, before="cursor_token")
```

## Next Steps

- [Offset Pagination](offset.md) - Detailed guide
- [Keyset Pagination](keyset.md) - For large datasets
- [In-Memory Pagination](memory.md) - For collections
