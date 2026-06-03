# Multi-Column Sorting

Multi-column sorting defines a hierarchy of sort criteria. When two items have equal values in the primary sort field, the secondary field determines their order, and so on.

## How It Works

Pass multiple `SortSpec` objects in priority order -- the first spec has the highest priority:

```python
from pypaginate import SortSpec, SortDirection, NullsPosition
from pypaginate.sorting.engine import SortEngine

engine = SortEngine()

employees = [
    {"name": "Alice", "department": "Engineering", "salary": 120000},
    {"name": "Bob", "department": "Engineering", "salary": 100000},
    {"name": "Charlie", "department": "Sales", "salary": 90000},
    {"name": "Diana", "department": "Engineering", "salary": 110000},
]

# Sort by department ASC, then by salary DESC within each department
sorted_employees = engine.apply(employees, [
    SortSpec(field="department"),
    SortSpec(field="salary", direction=SortDirection.DESC),
])
# Engineering: Alice(120k), Diana(110k), Bob(100k)
# Sales: Charlie(90k)
```

## Stable Sort Guarantee

`SortEngine` uses Python's stable sort. Specs are applied in reverse order so the first spec in the list has the highest priority. Items with equal values in a sort field keep their relative order from the previous sort pass.

## In-Memory Multi-Column

### Two-Level Sort

```python
from pypaginate import SortSpec, SortDirection
from pypaginate.sorting.engine import SortEngine

engine = SortEngine()

# Sort by department ASC, then by name ASC
sorted_items = engine.apply(employees, [
    SortSpec(field="department"),
    SortSpec(field="name"),
])
```

### Three-Level Sort with Mixed Directions

```python
# Department ASC, salary DESC, name ASC
sorted_items = engine.apply(employees, [
    SortSpec(field="department", direction=SortDirection.ASC),
    SortSpec(field="salary", direction=SortDirection.DESC),
    SortSpec(field="name", direction=SortDirection.ASC),
])
```

### Nulls Handling Per-Column

Each spec independently controls null placement:

```python
from pypaginate import SortSpec, SortDirection, NullsPosition

sorted_items = engine.apply(employees, [
    SortSpec(field="department", nulls=NullsPosition.LAST),
    SortSpec(field="manager", nulls=NullsPosition.FIRST),
    SortSpec(field="name"),
])
```

## SQLAlchemy Multi-Column

`SQLAlchemySortBackend.apply_sorting()` generates multiple ORDER BY clauses:

```python
from sqlalchemy import select
from pypaginate import SortSpec, SortDirection, NullsPosition
from pypaginate.adapters.sqlalchemy import SQLAlchemySortBackend

backend = SQLAlchemySortBackend()

stmt = select(Employee)
sorted_stmt = backend.apply_sorting(stmt, [
    SortSpec(field="department"),
    SortSpec(field="salary", direction=SortDirection.DESC),
    SortSpec(field="name"),
])
# SELECT * FROM employee
# ORDER BY department ASC NULLS LAST, salary DESC NULLS LAST, name ASC NULLS LAST
```

### With Null Handling

```python
sorted_stmt = backend.apply_sorting(stmt, [
    SortSpec(field="department", nulls=NullsPosition.LAST),
    SortSpec(field="name", nulls=NullsPosition.FIRST),
])
# ORDER BY department ASC NULLS LAST, name ASC NULLS FIRST
```

## Pipeline Integration

Combine multi-column sorting with filtering and pagination:

```python
from pypaginate import FilterSpec, SortSpec, SortDirection, OffsetParams
from pypaginate.adapters.memory import MemoryBackend, MemoryFilterBackend, MemorySortBackend
from pypaginate.engine.paginator import Paginator
from pypaginate.engine.pipeline import SyncPipeline

pipeline = SyncPipeline(
    Paginator(MemoryBackend()),
    filter_backend=MemoryFilterBackend(),
    sort_backend=MemorySortBackend(),
)

page = pipeline.execute(
    employees,
    OffsetParams(page=1, limit=20),
    filters=[FilterSpec(field="status", value="active")],
    sorting=[
        SortSpec(field="department"),
        SortSpec(field="salary", direction=SortDirection.DESC),
    ],
)
```

### Async SQLAlchemy Pipeline

```python
from pypaginate import SortSpec, SortDirection, OffsetParams
from pypaginate.adapters.sqlalchemy import (
    SQLAlchemyBackend,
    SQLAlchemySortBackend,
)
from pypaginate.engine.paginator import AsyncPaginator
from pypaginate.engine.pipeline import AsyncPipeline

pipeline = AsyncPipeline(
    AsyncPaginator(SQLAlchemyBackend(session)),
    sort_backend=SQLAlchemySortBackend(),
)

page = await pipeline.execute(
    select(Employee),
    OffsetParams(page=1, limit=20),
    sorting=[
        SortSpec(field="department"),
        SortSpec(field="hire_date", direction=SortDirection.DESC),
    ],
)
```

## Common Use Cases

### Leaderboard

```python
# Highest score first, earliest achievement for ties
sorting = [
    SortSpec(field="score", direction=SortDirection.DESC),
    SortSpec(field="achieved_at", direction=SortDirection.ASC),
]
```

### Product Catalog

```python
# By category, then cheapest first
sorting = [
    SortSpec(field="category"),
    SortSpec(field="price"),
]
```

### User Directory

```python
# By department, then by last name, then by first name
sorting = [
    SortSpec(field="department", nulls=NullsPosition.LAST),
    SortSpec(field="last_name"),
    SortSpec(field="first_name"),
]
```

### Deterministic Tie-Breaking

Always include a unique field (like `id`) as the last sort spec to guarantee deterministic ordering:

```python
sorting = [
    SortSpec(field="department"),
    SortSpec(field="salary", direction=SortDirection.DESC),
    SortSpec(field="id"),  # tie-breaker ensures stable order
]
```

## Performance Tips

1. **Index sort columns** -- multi-column sorts benefit from composite indexes
2. **Limit sort fields** -- each additional field adds overhead
3. **Include a unique tie-breaker** -- deterministic ordering prevents pagination anomalies
4. **Use SQL for databases** -- `SQLAlchemySortBackend` pushes sorting to the DB engine

### Composite Indexes for Common Sort Patterns

```python
from sqlalchemy import Index

Index(
    "idx_employee_dept_salary",
    Employee.department,
    Employee.salary.desc(),
)
```

## See Also

- [Basic Sorting](basic.md) -- Single-field sorting fundamentals
- [Pagination](../pagination/index.md) -- Combine sorting with pagination
