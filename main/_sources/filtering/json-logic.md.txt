# Nested Filter Groups

pypaginate supports arbitrarily nested AND/OR filter expressions via `FilterGroup`, `And()`, and `Or()` builder functions.

:::{note}
The name "JSON Logic" is historical. pypaginate v0.2 uses typed Python objects (`FilterGroup`, `And`, `Or`) instead of raw JSON dicts. These compose into nested boolean trees that both in-memory and SQLAlchemy backends evaluate natively.
:::

## And / Or Builders

The `And()` and `Or()` functions create `FilterGroup` objects:

```python
from pypaginate import And, Or, FilterSpec

# Simple OR: either condition matches
group = Or(
    FilterSpec(field="role", value="admin"),
    FilterSpec(field="role", value="moderator"),
)
# role = "admin" OR role = "moderator"

# Simple AND: both conditions must match
group = And(
    FilterSpec(field="status", value="active"),
    FilterSpec(field="age", operator="gte", value=18),
)
# status = "active" AND age >= 18
```

## Nesting Groups

Groups can contain other groups for complex boolean expressions:

```python
from pypaginate import And, Or, FilterSpec

# (role=admin OR role=mod) AND (status=active OR status=pending)
group = And(
    Or(
        FilterSpec(field="role", value="admin"),
        FilterSpec(field="role", value="moderator"),
    ),
    Or(
        FilterSpec(field="status", value="active"),
        FilterSpec(field="status", value="pending"),
    ),
)
```

```python
# age >= 18 AND (country=US OR (country=UK AND verified=True))
group = And(
    FilterSpec(field="age", operator="gte", value=18),
    Or(
        FilterSpec(field="country", value="US"),
        And(
            FilterSpec(field="country", value="UK"),
            FilterSpec(field="verified", value=True),
        ),
    ),
)
```

## Depth Limit

`FilterGroup` validates nesting depth at construction time. The maximum depth is 5 levels. Exceeding this raises a `ValueError`:

```python
from pypaginate import And, FilterSpec

# This would raise ValueError: "FilterGroup nesting must not exceed 5 levels"
# deeply_nested = And(And(And(And(And(And(FilterSpec(...)))))))
```

## FilterGroup Model

Under the hood, `And()` and `Or()` return `FilterGroup` objects:

```python
from pypaginate import FilterGroup, FilterLogic, FilterSpec

# Direct construction (prefer And/Or builders)
group = FilterGroup(
    logic=FilterLogic.AND,
    conditions=(
        FilterSpec(field="a", value=1),
        FilterSpec(field="b", value=2),
    ),
)
```

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `logic` | `FilterLogic` | `AND` | How to combine the conditions |
| `conditions` | `tuple[FilterSpec \| FilterGroup, ...]` | required | Child conditions |

## In-Memory Usage

`FilterEngine.apply()` accepts both flat lists and `FilterGroup`:

```python
from pypaginate import And, Or, FilterSpec
from pypaginate.filtering.engine import FilterEngine
from pypaginate.filtering.registry import create_default_registry

engine = FilterEngine(registry=create_default_registry())

users = [
    {"name": "Alice", "role": "admin", "status": "active"},
    {"name": "Bob", "role": "user", "status": "active"},
    {"name": "Charlie", "role": "moderator", "status": "inactive"},
    {"name": "Diana", "role": "admin", "status": "inactive"},
]

# Nested group
group = And(
    Or(
        FilterSpec(field="role", value="admin"),
        FilterSpec(field="role", value="moderator"),
    ),
    FilterSpec(field="status", value="active"),
)

result = engine.apply(users, group)
# [{"name": "Alice", "role": "admin", "status": "active"}]
```

## Pipeline Usage

Groups work with the `paginate()` function by applying group filters first, then paginating the results:

```python
from pypaginate import And, Or, FilterSpec, OffsetParams, paginate
from pypaginate.filtering.engine import FilterEngine
from pypaginate.filtering.registry import create_default_registry

engine = FilterEngine(registry=create_default_registry())

# Apply nested group, then paginate
group = And(
    Or(FilterSpec(field="role", value="admin"), FilterSpec(field="role", value="mod")),
    FilterSpec(field="status", value="active"),
)

filtered = engine.apply(users, group)

page = paginate(filtered, OffsetParams(page=1, limit=20))
```

## FilterInput Type

The `FilterInput` type alias accepts either form:

```python
from pypaginate.domain.specs import FilterInput

# Both are valid FilterInput:
flat: FilterInput = [FilterSpec(field="a", value=1)]
nested: FilterInput = And(FilterSpec(field="a", value=1), FilterSpec(field="b", value=2))
```

## Real-World Examples

### E-commerce Product Filter

```python
from pypaginate import And, Or, FilterSpec

product_filter = And(
    FilterSpec(field="category", operator="in", value=["electronics", "computers"]),
    FilterSpec(field="price", operator="between", value=(100, 1000)),
    FilterSpec(field="in_stock", operator="ne", value=0),
    Or(
        FilterSpec(field="rating", operator="gte", value=4),
        FilterSpec(field="reviews_count", operator="gte", value=100),
    ),
)
```

### User Search with Permissions

```python
user_filter = And(
    FilterSpec(field="status", value="active"),
    FilterSpec(field="email_verified", operator="is_not_null"),
    Or(
        FilterSpec(field="role", value="admin"),
        And(
            FilterSpec(field="role", value="user"),
            FilterSpec(field="permission_level", operator="gte", value=5),
        ),
    ),
)
```

## Comparison: Flat vs Nested

| Feature | Flat `list[FilterSpec]` | `FilterGroup` (And/Or) |
|---------|------------------------|------------------------|
| Simple AND | All specs with default logic | `And(spec1, spec2)` |
| Mixed AND/OR | `logic=FilterLogic.OR` per spec | `And(Or(...), spec)` |
| Nested groups | Not possible | Unlimited (up to depth 5) |
| Pipeline compat | Yes | Yes (via FilterEngine) |
| SQLAlchemy | Yes (via backend) | Via FilterEngine first |
