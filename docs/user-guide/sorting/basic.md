# Basic Sorting

This guide covers single-field sorting for both in-memory collections and SQL queries.

## In-Memory Sorting

### Using `sort_items`

The simplest way to sort a collection is using the `sort_items` function:

```python
from pypaginate.sorting import sort_items

@dataclass
class Product:
    id: int
    name: str
    price: float
    stock: int | None

products = [
    Product(1, "Widget", 29.99, 100),
    Product(2, "Gadget", 49.99, None),
    Product(3, "Gizmo", 19.99, 50),
]

# Sort by price (ascending)
sorted_products = sort_items(
    products,
    sort_field="price",
    reverse=False,
    nulls_position="last",
    tie_breaker_field="id",
)
# Result: [Gizmo, Widget, Gadget]

# Sort by price (descending)
sorted_products = sort_items(
    products,
    sort_field="price",
    reverse=True,
    nulls_position="last",
    tie_breaker_field="id",
)
# Result: [Gadget, Widget, Gizmo]
```

### Using `SortEngine` Directly

For repeated sorting operations, you can use the `SortEngine` class:

```python
from pypaginate.sorting import SortEngine

engine = SortEngine()

# Sort multiple collections with the same engine
sorted_a = engine.sort(
    products_a,
    sort_field="name",
    reverse=False,
    nulls_position="last",
    tie_breaker_field="id",
)

sorted_b = engine.sort(
    products_b,
    sort_field="name",
    reverse=False,
    nulls_position="last",
    tie_breaker_field="id",
)
```

### Factory Function

Use `create_sort_service` for dependency injection scenarios:

```python
from pypaginate.sorting import create_sort_service

# Create a sort service instance
sort_service = create_sort_service()

# Use it to sort items
sorted_items = sort_service.sort(
    items,
    sort_field="created_at",
    reverse=True,
    nulls_position="last",
    tie_breaker_field="id",
)
```

## Null Value Handling

### Nulls First

Place items with `None` values at the beginning:

```python
products = [
    Product(1, "Widget", 29.99, None),  # stock is None
    Product(2, "Gadget", 49.99, 25),
    Product(3, "Gizmo", 19.99, 50),
]

sorted_products = sort_items(
    products,
    sort_field="stock",
    reverse=False,
    nulls_position="first",
    tie_breaker_field="id",
)
# Result: [Widget(None), Gadget(25), Gizmo(50)]
```

### Nulls Last

Place items with `None` values at the end:

```python
sorted_products = sort_items(
    products,
    sort_field="stock",
    reverse=False,
    nulls_position="last",
    tie_breaker_field="id",
)
# Result: [Gadget(25), Gizmo(50), Widget(None)]
```

### Nulls with Reverse Sort

When reversing, null positioning still follows your specification:

```python
# Descending sort with nulls last
sorted_products = sort_items(
    products,
    sort_field="stock",
    reverse=True,
    nulls_position="last",
    tie_breaker_field="id",
)
# Result: [Gizmo(50), Gadget(25), Widget(None)]
```

## SQL Sorting

### Basic ORDER BY

Use `SqlSortAdapter` to build SQLAlchemy ORDER BY expressions:

```python
from sqlalchemy import select
from pypaginate.sorting import SqlSortAdapter

# Ascending order
order_expr = SqlSortAdapter.build_order_expression(
    column=Product.price,
    descending=False,
)
stmt = select(Product).order_by(order_expr)
# SQL: SELECT * FROM product ORDER BY price ASC

# Descending order
order_expr = SqlSortAdapter.build_order_expression(
    column=Product.price,
    descending=True,
)
stmt = select(Product).order_by(order_expr)
# SQL: SELECT * FROM product ORDER BY price DESC
```

### SQL Null Handling

PostgreSQL and other databases support explicit null positioning:

```python
# Nulls first
order_expr = SqlSortAdapter.build_order_expression(
    column=Product.stock,
    descending=False,
    nulls_position="first",
)
# SQL: ORDER BY stock ASC NULLS FIRST

# Nulls last
order_expr = SqlSortAdapter.build_order_expression(
    column=Product.stock,
    descending=True,
    nulls_position="last",
)
# SQL: ORDER BY stock DESC NULLS LAST
```

## Common Patterns

### Sorting by Date

```python
# Most recent first
sorted_posts = sort_items(
    posts,
    sort_field="created_at",
    reverse=True,  # Newest first
    nulls_position="last",
    tie_breaker_field="id",
)
```

### Alphabetical Sorting

```python
# A-Z sorting
sorted_users = sort_items(
    users,
    sort_field="name",
    reverse=False,
    nulls_position="last",
    tie_breaker_field="id",
)
```

### Numeric Sorting

```python
# Highest price first
sorted_products = sort_items(
    products,
    sort_field="price",
    reverse=True,
    nulls_position="last",
    tie_breaker_field="id",
)
```

## Tie-Breaking

### Why Tie-Breaking Matters

Without a tie-breaker, items with the same sort value may appear in arbitrary order:

```python
products = [
    Product(1, "Widget A", 29.99, 100),
    Product(2, "Widget B", 29.99, 100),  # Same price
    Product(3, "Widget C", 29.99, 100),  # Same price
]

# Without tie-breaker: order is not guaranteed
sorted_products = sort_items(
    products,
    sort_field="price",
    reverse=False,
    nulls_position="last",
    tie_breaker_field=None,  # No tie-breaker!
)
# Result: Could be any order among equal items
```

### Using ID as Tie-Breaker

The most common pattern is using the primary key:

```python
sorted_products = sort_items(
    products,
    sort_field="price",
    reverse=False,
    nulls_position="last",
    tie_breaker_field="id",  # Ensures consistent ordering
)
# Result: Always [Widget A, Widget B, Widget C]
```

## Best Practices

1. **Always specify a tie-breaker** for deterministic results
2. **Use `nulls_position`** explicitly rather than relying on defaults
3. **Consider pagination** when sorting large datasets
4. **Use SQL sorting** for database queries (more efficient)
5. **Reserve in-memory sorting** for small collections or post-processing

## Next Steps

- [Multi-Column Sorting](multi-column.md) - Sort by multiple fields
