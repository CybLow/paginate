# Core Module

The core module provides the fundamental types for pagination: `Page`, `PageParams`, and pagination context utilities.

## Page

The generic result container for paginated data. Provides computed properties for pagination metadata like `has_next`, `has_previous`, and `pages`.

```{eval-rst}
.. autoclass:: pypaginate.core.Page
   :members:
   :show-inheritance:
```

## PageParams

Immutable pagination parameters with validation. Use this for offset-based pagination.

```{eval-rst}
.. autoclass:: pypaginate.core.PageParams
   :members:
   :show-inheritance:
```

## KeysetPageParams

Parameters for cursor-based (keyset) pagination. More efficient than offset pagination for large datasets.

```{eval-rst}
.. autoclass:: pypaginate.core.KeysetPageParams
   :members:
   :show-inheritance:
```

## Pagination Context

Internal context object used during pagination execution.

```{eval-rst}
.. autoclass:: pypaginate.core.PaginationContext
   :members:
   :show-inheritance:
   :no-index:
```

```{eval-rst}
.. autofunction:: pypaginate.core.clamp_page_params
```

## Snapshots

Internal snapshot objects returned by pagination engines.

```{eval-rst}
.. autoclass:: pypaginate.core.PaginationSnapshot
   :members:
   :show-inheritance:
   :no-index:
```

```{eval-rst}
.. autoclass:: pypaginate.core.KeysetPaginationSnapshot
   :members:
   :show-inheritance:
   :no-index:
```

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
