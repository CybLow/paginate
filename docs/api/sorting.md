# Sorting Module

The sorting module provides sorting capabilities for both in-memory collections and SQL queries.

## SortEngine

Generic sorting engine for in-memory collections.

::: pypaginate.sorting.engine.SortEngine
    options:
      show_source: true
      members:
        - sort

## SqlSortAdapter

SQL adapter for building SQLAlchemy ORDER BY expressions.

::: pypaginate.sorting.sql_adapter.SqlSortAdapter
    options:
      show_source: true
      members:
        - build_order_expression

## Helper Functions

::: pypaginate.sorting.engine.sort_items
    options:
      show_source: true

::: pypaginate.sorting.engine.create_sort_service
    options:
      show_source: true

## Types

::: pypaginate.sorting.engine.Nulls
    options:
      show_source: false

## Usage Examples

### In-Memory Sorting

```python
from pypaginate.sorting import SortEngine, sort_items

# Using sort_items helper
sorted_users = sort_items(
    users,
    sort_field="name",
    reverse=False,
    nulls_position="last",
    tie_breaker_field="id",
)

# Using SortEngine directly
engine = SortEngine()
sorted_users = engine.sort(
    users,
    sort_field="created_at",
    reverse=True,
    nulls_position="last",
    tie_breaker_field="id",
)
```

### SQL Sorting

```python
from sqlalchemy import select
from pypaginate.sorting import SqlSortAdapter

# Simple ascending sort
order_expr = SqlSortAdapter.build_order_expression(
    column=User.name,
    descending=False,
)
stmt = select(User).order_by(order_expr)

# Descending with null positioning
order_expr = SqlSortAdapter.build_order_expression(
    column=User.created_at,
    descending=True,
    nulls_position="last",
)
stmt = select(User).order_by(order_expr)
```

### Multi-Column Sorting

```python
# Sort by multiple columns
stmt = select(Employee).order_by(
    SqlSortAdapter.build_order_expression(
        column=Employee.department,
        descending=False,
    ),
    SqlSortAdapter.build_order_expression(
        column=Employee.salary,
        descending=True,
    ),
)
```

### Null Handling

```python
# Nulls first
sorted_items = sort_items(
    items,
    sort_field="optional_field",
    reverse=False,
    nulls_position="first",
    tie_breaker_field="id",
)

# Nulls last
sorted_items = sort_items(
    items,
    sort_field="optional_field",
    reverse=False,
    nulls_position="last",
    tie_breaker_field="id",
)
```

### Dynamic Sorting

```python
def apply_sort(stmt, sort_field: str, descending: bool = False):
    """Apply dynamic sorting to a query."""
    column = getattr(User, sort_field)
    order_expr = SqlSortAdapter.build_order_expression(
        column=column,
        descending=descending,
        nulls_position="last",
    )
    return stmt.order_by(order_expr)

# Usage
stmt = select(User)
stmt = apply_sort(stmt, "name", descending=False)
```

## Parameters Reference

### SortEngine.sort / sort_items

| Parameter | Type | Description |
|-----------|------|-------------|
| `items` | list[T] | List of items to sort |
| `sort_field` | str | Attribute name for primary ordering |
| `reverse` | bool | True for descending order |
| `nulls_position` | "first" \| "last" | Where to place None values |
| `tie_breaker_field` | str \| None | Secondary sort field for stability |

### SqlSortAdapter.build_order_expression

| Parameter | Type | Description |
|-----------|------|-------------|
| `column` | Column | SQLAlchemy column to sort by |
| `descending` | bool | True for DESC, False for ASC |
| `nulls_position` | str \| None | "first", "last", or None |

**Returns:** SQLAlchemy UnaryExpression for ORDER BY clause
