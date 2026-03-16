# Filtering

pypaginate provides declarative filtering through `FilterSpec` objects and composable `And`/`Or` groups.

:::{tip} Quick Start
```python
from pypaginate import FilterSpec

filters = [
    FilterSpec(field="status", operator="eq", value="active"),
    FilterSpec(field="age", operator="gte", value=18),
]
```
:::

## Overview

| Feature | Description |
|---------|-------------|
| [Basic Filtering](basic.md) | FilterSpec, flat lists, AND/OR logic |
| [Operators Reference](operators.md) | All 20 built-in operators with examples |
| [JSON Logic](json-logic.md) | Nested groups via `And()` / `Or()` builders |

## Quick Example

```python
from pypaginate import FilterSpec, paginate, OffsetParams

users = [
    {"name": "Alice", "age": 30, "status": "active"},
    {"name": "Bob", "age": 25, "status": "inactive"},
    {"name": "Charlie", "age": 35, "status": "active"},
]

# Filter + paginate in one call using the pipeline
from pypaginate.adapters.memory import MemoryBackend, MemoryFilterBackend
from pypaginate.engine.pipeline import SyncPipeline
from pypaginate.engine.paginator import Paginator

pipeline = SyncPipeline(
    Paginator(MemoryBackend()),
    filter_backend=MemoryFilterBackend(),
)
page = pipeline.execute(
    users,
    OffsetParams(page=1, limit=10),
    filters=[
        FilterSpec(field="status", operator="eq", value="active"),
        FilterSpec(field="age", operator="gte", value=30),
    ],
)
# page.items = [{"name": "Alice", ...}, {"name": "Charlie", ...}]
```

## FilterSpec

`FilterSpec` is an immutable Pydantic model describing a single filter condition:

```python
from pypaginate import FilterSpec

# field + operator + value
FilterSpec(field="age", operator="gte", value=18)

# operator defaults to "eq"
FilterSpec(field="name", value="Alice")

# logic defaults to FilterLogic.AND
from pypaginate import FilterLogic
FilterSpec(field="role", operator="in", value=["admin", "mod"], logic=FilterLogic.OR)
```

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `field` | `str` | required | Field name to filter on |
| `operator` | `FilterOperator` | `"eq"` | One of 20 built-in operators |
| `value` | `Any` | `None` | Comparison value |
| `logic` | `FilterLogic` | `AND` | How to combine with other filters |

## Combining Filters

### Flat List (all AND)

```python
filters = [
    FilterSpec(field="age", operator="gte", value=18),
    FilterSpec(field="status", operator="eq", value="active"),
]
# Equivalent to: age >= 18 AND status = "active"
```

### Mixed AND/OR

```python
from pypaginate import FilterLogic

filters = [
    FilterSpec(field="age", operator="gte", value=18),
    FilterSpec(field="role", operator="eq", value="admin", logic=FilterLogic.OR),
    FilterSpec(field="role", operator="eq", value="mod", logic=FilterLogic.OR),
]
# Equivalent to: age >= 18 AND (role = "admin" OR role = "mod")
```

### Nested Groups

```python
from pypaginate import And, Or, FilterSpec

group = And(
    Or(FilterSpec(field="role", value="admin"), FilterSpec(field="role", value="mod")),
    Or(FilterSpec(field="status", value="active"), FilterSpec(field="status", value="pending")),
)
# (role=admin OR role=mod) AND (status=active OR status=pending)
```

## Backend Support

| Backend | Import | Notes |
|---------|--------|-------|
| In-memory | `from pypaginate.adapters.memory import MemoryFilterBackend` | Compiles to fast closures |
| In-memory (engine) | `from pypaginate.filtering.engine import FilterEngine` | Direct engine for sequences |
| SQLAlchemy | `from pypaginate.adapters.sqlalchemy import SQLAlchemyFilterBackend` | Generates WHERE clauses |

## Next Steps

- [Basic Filtering](basic.md) -- FilterSpec fundamentals and usage patterns
- [Operators Reference](operators.md) -- All 20 operators with examples
- [JSON Logic](json-logic.md) -- Nested `And()`/`Or()` groups
