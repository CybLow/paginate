# Multi-Column Sorting

This guide covers advanced sorting scenarios with multiple sort fields.

## Overview

Multi-column sorting allows you to define a hierarchy of sort criteria. When two items have equal values in the primary sort field, the secondary field determines their order, and so on.

## SQL Multi-Column Sorting

The `SqlSortAdapter` is designed for building individual ORDER BY expressions that can be combined for multi-column sorting.

### Basic Multi-Column

```python
from sqlalchemy import select
from pypaginator.sorting import SqlSortAdapter

# Sort by department (ASC), then by salary (DESC)
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
# SQL: ORDER BY department ASC, salary DESC
```

### With Null Handling

```python
# Sort by department (nulls last), then by name (nulls first)
stmt = select(Employee).order_by(
    SqlSortAdapter.build_order_expression(
        column=Employee.department,
        descending=False,
        nulls_position="last",
    ),
    SqlSortAdapter.build_order_expression(
        column=Employee.name,
        descending=False,
        nulls_position="first",
    ),
)
# SQL: ORDER BY department ASC NULLS LAST, name ASC NULLS FIRST
```

### Dynamic Multi-Column Sorting

Build sort expressions dynamically from user input:

```python
from pypaginator.sorting import SqlSortAdapter

def build_order_by(sort_specs: list[dict]) -> list:
    """
    Build ORDER BY expressions from sort specifications.
    
    Args:
        sort_specs: List of dicts with 'field', 'descending', 'nulls' keys
    
    Returns:
        List of SQLAlchemy order expressions
    """
    expressions = []
    
    for spec in sort_specs:
        column = getattr(Employee, spec["field"])
        expr = SqlSortAdapter.build_order_expression(
            column=column,
            descending=spec.get("descending", False),
            nulls_position=spec.get("nulls"),
        )
        expressions.append(expr)
    
    return expressions

# Usage
sort_specs = [
    {"field": "department", "descending": False, "nulls": "last"},
    {"field": "hire_date", "descending": True},
    {"field": "name", "descending": False},
]

stmt = select(Employee).order_by(*build_order_by(sort_specs))
```

## In-Memory Multi-Column Sorting

For in-memory sorting with multiple columns, use the tie-breaker mechanism or chain sorts:

### Using Tie-Breaker

The `tie_breaker_field` parameter handles the most common case of secondary sorting:

```python
from pypaginator.sorting import sort_items

# Sort by department, then by name within each department
sorted_employees = sort_items(
    employees,
    sort_field="department",
    reverse=False,
    nulls_position="last",
    tie_breaker_field="name",  # Secondary sort
)
```

### Chained Sorting for Complex Cases

For more than two sort fields, chain multiple sorts (starting with the least significant):

```python
from pypaginator.sorting import sort_items

# Sort by: 1) department, 2) role, 3) name
# Apply in reverse order of significance

# Step 1: Sort by name (least significant)
result = sort_items(
    employees,
    sort_field="name",
    reverse=False,
    nulls_position="last",
    tie_breaker_field="id",
)

# Step 2: Sort by role (more significant)
result = sort_items(
    result,
    sort_field="role",
    reverse=False,
    nulls_position="last",
    tie_breaker_field="id",
)

# Step 3: Sort by department (most significant)
result = sort_items(
    result,
    sort_field="department",
    reverse=False,
    nulls_position="last",
    tie_breaker_field="id",
)
```

### Custom Multi-Column Sort Function

Create a helper function for complex in-memory multi-column sorting:

```python
from pypaginator.sorting import sort_items
from typing import TypeVar

T = TypeVar("T")

def multi_sort(
    items: list[T],
    sort_specs: list[tuple[str, bool, str | None]],
    nulls_position: str = "last",
) -> list[T]:
    """
    Sort items by multiple fields.
    
    Args:
        items: List of items to sort
        sort_specs: List of (field, reverse, tie_breaker) tuples
                   Order from most to least significant
        nulls_position: Where to place null values
    
    Returns:
        Sorted list
    """
    result = list(items)
    
    # Apply sorts in reverse order (least significant first)
    for field, reverse, tie_breaker in reversed(sort_specs):
        result = sort_items(
            result,
            sort_field=field,
            reverse=reverse,
            nulls_position=nulls_position,
            tie_breaker_field=tie_breaker,
        )
    
    return result

# Usage
sorted_employees = multi_sort(
    employees,
    [
        ("department", False, "id"),    # Primary: department ASC
        ("salary", True, "id"),         # Secondary: salary DESC
        ("name", False, "id"),          # Tertiary: name ASC
    ],
)
```

## FastAPI Integration

### Query Parameter Parsing

Parse multi-column sort parameters from URL:

```python
from fastapi import FastAPI, Query
from pypaginator.sorting import SqlSortAdapter

app = FastAPI()

@app.get("/employees")
async def list_employees(
    sort: list[str] = Query(
        default=["department", "-salary"],
        description="Sort fields (prefix with - for descending)"
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    List employees with multi-column sorting.
    
    Query examples:
        /employees?sort=department&sort=-salary
        /employees?sort=name
        /employees?sort=-hire_date&sort=department
    """
    stmt = select(Employee)
    
    for field in sort:
        descending = field.startswith("-")
        field_name = field.lstrip("-")
        
        # Validate field exists
        if not hasattr(Employee, field_name):
            raise HTTPException(400, f"Invalid sort field: {field_name}")
        
        column = getattr(Employee, field_name)
        order_expr = SqlSortAdapter.build_order_expression(
            column=column,
            descending=descending,
            nulls_position="last",
        )
        stmt = stmt.order_by(order_expr)
    
    result = await session.execute(stmt)
    return result.scalars().all()
```

### Comma-Separated Sort Parameter

Alternative format using comma-separated values:

```python
@app.get("/employees")
async def list_employees(
    sort: str = Query(
        default="department,-salary",
        description="Comma-separated sort fields"
    ),
):
    """
    Query examples:
        /employees?sort=department,-salary
        /employees?sort=name,hire_date
    """
    sort_fields = [f.strip() for f in sort.split(",") if f.strip()]
    
    stmt = select(Employee)
    for field in sort_fields:
        descending = field.startswith("-")
        field_name = field.lstrip("-")
        
        column = getattr(Employee, field_name)
        order_expr = SqlSortAdapter.build_order_expression(
            column=column,
            descending=descending,
        )
        stmt = stmt.order_by(order_expr)
    
    # ... rest of implementation
```

## Common Use Cases

### Leaderboard Sorting

```python
# Sort by score (DESC), then by earliest achievement (ASC)
stmt = select(Player).order_by(
    SqlSortAdapter.build_order_expression(
        column=Player.score,
        descending=True,
    ),
    SqlSortAdapter.build_order_expression(
        column=Player.achieved_at,
        descending=False,
    ),
)
```

### Product Catalog

```python
# Sort by category, then by price within category
stmt = select(Product).order_by(
    SqlSortAdapter.build_order_expression(
        column=Product.category,
        descending=False,
    ),
    SqlSortAdapter.build_order_expression(
        column=Product.price,
        descending=False,
    ),
)
```

### User Directory

```python
# Sort by department, then by last name, then by first name
stmt = select(User).order_by(
    SqlSortAdapter.build_order_expression(
        column=User.department,
        descending=False,
        nulls_position="last",
    ),
    SqlSortAdapter.build_order_expression(
        column=User.last_name,
        descending=False,
    ),
    SqlSortAdapter.build_order_expression(
        column=User.first_name,
        descending=False,
    ),
)
```

## Performance Considerations

1. **Index your sort columns** - Multi-column sorts benefit from composite indexes
2. **Limit sort fields** - More fields = more work for the database
3. **Consider pagination** - Always paginate sorted results
4. **Validate user input** - Prevent arbitrary column access

### Creating Composite Indexes

```python
from sqlalchemy import Index

# Create composite index for common sort patterns
Index(
    "idx_employee_dept_salary",
    Employee.department,
    Employee.salary.desc(),
)
```

## Best Practices

1. **Validate sort fields** against an allowed list
2. **Limit the number of sort fields** (e.g., max 3-5)
3. **Always include a unique field** as the final tie-breaker
4. **Document available sort fields** in your API
5. **Use SQL sorting** for database queries when possible
6. **Consider caching** for frequently-used sort combinations

## See Also

- [Basic Sorting](basic.md) - Single-field sorting fundamentals
- [Pagination](../pagination/index.md) - Combine sorting with pagination
