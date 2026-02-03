# Core Module

The core module provides the fundamental types for pagination: `Page`, `PageParams`, and pagination context utilities.

## Page

::: pypaginate.core.pages.Page
    options:
      show_source: true
      members:
        - items
        - total
        - page
        - limit
        - pages
        - has_next
        - has_previous
        - create

## PageParams

::: pypaginate.core.pages.PageParams
    options:
      show_source: true
      members:
        - page
        - limit
        - offset

## KeysetPageParams

::: pypaginate.core.pages.KeysetPageParams
    options:
      show_source: true

## Pagination Context

::: pypaginate.core.context.PaginationContext
    options:
      show_source: true

::: pypaginate.core.context.clamp_page_params
    options:
      show_source: true

## Snapshots

::: pypaginate.core.snapshots.PaginationSnapshot
    options:
      show_source: true

::: pypaginate.core.snapshots.KeysetPaginationSnapshot
    options:
      show_source: true

## Usage Examples

### Creating a Page

```python
from pypaginate.core import Page, PageParams

# Create page from data
items = [user1, user2, user3]
total = 100
params = PageParams(page=1, limit=20)

page = Page.create(items, total, params)

print(page.items)        # [user1, user2, user3]
print(page.total)        # 100
print(page.page)         # 1
print(page.limit)        # 20
print(page.pages)        # 5
print(page.has_next)     # True
print(page.has_previous) # False
```

### Working with PageParams

```python
from pypaginate.core import PageParams

params = PageParams(page=3, limit=25)

print(params.page)    # 3
print(params.limit)   # 25
print(params.offset)  # 50 (computed: (page-1) * limit)
```

### Using Pagination Context

```python
from pypaginate.core.context import PaginationContext, clamp_page_params

# Create context for pagination execution
context = PaginationContext(
    params=PageParams(page=1, limit=20),
    count_query=None,
    unique=False,
)

# Clamp params to valid range
total = 100
clamped = clamp_page_params(total, PageParams(page=10, limit=20))
# If page 10 exceeds total pages, it's clamped to the last valid page
```
