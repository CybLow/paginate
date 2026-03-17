# Basic Sorting

This guide covers single-field sorting with `SortSpec` for both in-memory collections and SQLAlchemy queries.

## SortSpec

Create a `SortSpec` to describe how to sort:

```python
from pypaginate import SortSpec, SortDirection, NullsPosition

# Sort by name ascending (defaults)
SortSpec(field="name")

# Sort by created_at descending, nulls last
SortSpec(field="created_at", direction=SortDirection.DESC, nulls=NullsPosition.LAST)
```

## In-Memory Sorting

### Using SortEngine

`SortEngine` sorts Python sequences directly:

```python
from pypaginate import SortSpec, SortDirection
from pypaginate.sorting.engine import SortEngine

engine = SortEngine()

products = [
    {"name": "Widget", "price": 29.99},
    {"name": "Gadget", "price": 49.99},
    {"name": "Gizmo", "price": 19.99},
]

# Sort by price ascending
sorted_products = engine.apply(products, [
    SortSpec(field="price"),
])
# [Gizmo(19.99), Widget(29.99), Gadget(49.99)]

# Sort by price descending
sorted_products = engine.apply(products, [
    SortSpec(field="price", direction=SortDirection.DESC),
])
# [Gadget(49.99), Widget(29.99), Gizmo(19.99)]
```

### Using MemorySortBackend

`MemorySortBackend` satisfies the `SortBackend` protocol for pipeline use:

```python
from pypaginate import SortSpec, SortDirection
from pypaginate.adapters.memory import MemorySortBackend

backend = MemorySortBackend()

sorted_items = backend.apply_sorting(products, [
    SortSpec(field="price", direction=SortDirection.DESC),
])
```

## Null Value Handling

`NullsPosition` controls where `None` values appear in sorted results:

```python
from pypaginate import SortSpec, SortDirection, NullsPosition
from pypaginate.sorting.engine import SortEngine

engine = SortEngine()

products = [
    {"name": "Widget", "stock": None},
    {"name": "Gadget", "stock": 25},
    {"name": "Gizmo", "stock": 50},
]

# Nulls first
sorted_products = engine.apply(products, [
    SortSpec(field="stock", nulls=NullsPosition.FIRST),
])
# [Widget(None), Gadget(25), Gizmo(50)]

# Nulls last (default)
sorted_products = engine.apply(products, [
    SortSpec(field="stock", nulls=NullsPosition.LAST),
])
# [Gadget(25), Gizmo(50), Widget(None)]
```

Null positioning is independent of sort direction:

```python
# Descending sort with nulls last
sorted_products = engine.apply(products, [
    SortSpec(field="stock", direction=SortDirection.DESC, nulls=NullsPosition.LAST),
])
# [Gizmo(50), Gadget(25), Widget(None)]
```

## SQLAlchemy Sorting

`SQLAlchemySortBackend` translates `SortSpec` to ORDER BY clauses:

```python
from sqlalchemy import select
from pypaginate import SortSpec, SortDirection, NullsPosition
from pypaginate.adapters.sqlalchemy import SQLAlchemySortBackend

backend = SQLAlchemySortBackend()

stmt = select(Product)
sorted_stmt = backend.apply_sorting(stmt, [
    SortSpec(field="price", direction=SortDirection.DESC, nulls=NullsPosition.LAST),
])
# SELECT * FROM product ORDER BY price DESC NULLS LAST
```

The backend generates proper SQLAlchemy expressions:

- `SortDirection.ASC` -> `column.asc()`
- `SortDirection.DESC` -> `column.desc()`
- `NullsPosition.FIRST` -> `.nulls_first()`
- `NullsPosition.LAST` -> `.nulls_last()`

## Pipeline Usage

Pass sorting specs to `SyncPipeline.execute()` or `AsyncPipeline.execute()` via the `sorting=` parameter. See [Multi-Column Sorting](multi-column.md) for pipeline examples with sorting, filtering, and pagination combined.

## Common Patterns

### Sort by Date

```python
from pypaginate import SortSpec, SortDirection

# Most recent first
SortSpec(field="created_at", direction=SortDirection.DESC)

# Oldest first
SortSpec(field="created_at", direction=SortDirection.ASC)
```

### Alphabetical Sort

```python
# A-Z
SortSpec(field="name", direction=SortDirection.ASC)

# Z-A
SortSpec(field="name", direction=SortDirection.DESC)
```

### Numeric Sort

```python
# Highest price first
SortSpec(field="price", direction=SortDirection.DESC)

# Lowest score first
SortSpec(field="score", direction=SortDirection.ASC)
```

## Error Handling

`SortError` is raised when field values cannot be compared (e.g., mixed types):

```python
from pypaginate import SortError, SortSpec
from pypaginate.sorting.engine import SortEngine

engine = SortEngine()
items = [{"val": "abc"}, {"val": 123}]

try:
    engine.apply(items, [SortSpec(field="val")])
except SortError as e:
    print(f"Sort error: {e}")
```

## Next Steps

- [Multi-Column Sorting](multi-column.md) -- Sort by multiple fields with priority
