# Sorting

pypaginate provides declarative sorting through `SortSpec` objects with `SortDirection` and `NullsPosition` enums.

:::{tip} Quick Start
```python
from pypaginate import SortSpec, SortDirection

sorting = [
    SortSpec(field="created_at", direction=SortDirection.DESC),
    SortSpec(field="name"),  # defaults to ASC
]
```
:::

## Overview

| Feature | Description |
|---------|-------------|
| [Basic Sorting](basic.md) | Single-column sorting with SortSpec |
| [Multi-Column Sorting](multi-column.md) | Priority-based multi-field sorting |

## Quick Example

```python
from pypaginate import SortSpec, SortDirection, NullsPosition

users = [
    {"name": "Charlie", "age": 35},
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": None},
]

# Sort by age ascending, nulls at the end
from pypaginate.sorting.engine import SortEngine

engine = SortEngine()
sorted_users = engine.apply(users, [
    SortSpec(field="age", direction=SortDirection.ASC, nulls=NullsPosition.LAST),
])
# [Alice(30), Charlie(35), Bob(None)]
```

## SortSpec

`SortSpec` is an immutable Pydantic model describing a sort criterion:

```python
from pypaginate import SortSpec, SortDirection, NullsPosition

spec = SortSpec(
    field="created_at",
    direction=SortDirection.DESC,
    nulls=NullsPosition.LAST,
)
```

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `field` | `str` | required | Field name to sort on |
| `direction` | `SortDirection` | `ASC` | `ASC` or `DESC` |
| `nulls` | `NullsPosition` | `LAST` | `FIRST` or `LAST` -- where to place `None` values |

## SortDirection Enum

```python
from pypaginate import SortDirection

SortDirection.ASC    # ascending (A-Z, 0-9, oldest first)
SortDirection.DESC   # descending (Z-A, 9-0, newest first)
```

## NullsPosition Enum

```python
from pypaginate import NullsPosition

NullsPosition.FIRST  # None values appear before non-None
NullsPosition.LAST   # None values appear after non-None (default)
```

## Backend Support

| Backend | Import | Notes |
|---------|--------|-------|
| In-memory (engine) | `from pypaginate.sorting.engine import SortEngine` | Direct sort on sequences |
| In-memory (backend) | `from pypaginate.adapters.memory import MemorySortBackend` | Pipeline-compatible |
| SQLAlchemy | `from pypaginate.adapters.sqlalchemy import SQLAlchemySortBackend` | Generates ORDER BY |

## Next Steps

- [Basic Sorting](basic.md) -- Single-field sorting fundamentals
- [Multi-Column Sorting](multi-column.md) -- Complex sorting scenarios
