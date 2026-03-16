# Basic Filtering

This guide covers `FilterSpec` construction, operator selection, value types, and how to apply filters to both in-memory collections and SQLAlchemy queries.

## FilterSpec

Every filter is a `FilterSpec` -- an immutable Pydantic model with four fields:

```python
from pypaginate import FilterSpec

spec = FilterSpec(
    field="age",       # field name (supports dot notation: "address.city")
    operator="gte",    # one of 20 built-in operators
    value=18,          # comparison value (type depends on operator)
    # logic=FilterLogic.AND  (default)
)
```

### Defaults

- `operator` defaults to `"eq"` (equality)
- `value` defaults to `None`
- `logic` defaults to `FilterLogic.AND`

```python
# These are equivalent:
FilterSpec(field="name", operator="eq", value="Alice")
FilterSpec(field="name", value="Alice")
```

## Operator Categories

| Category | Operators | Value Type |
|----------|-----------|------------|
| Comparison | `eq`, `ne`, `gt`, `gte`, `lt`, `lte` | Same as field |
| Membership | `in`, `not_in` | Sequence |
| Text | `contains`, `starts_with`, `ends_with` | `str` |
| Pattern | `like`, `ilike`, `regex` | `str` |
| Range | `between` | Two-element sequence |
| Null | `is_null`, `is_not_null` | Ignored |
| Emptiness | `empty`, `not_empty` | Ignored |
| Existence | `exists` | Ignored |

See [Operators Reference](operators.md) for detailed examples of each.

## Value Types by Operator

```python
from pypaginate import FilterSpec

# Comparison: value matches the field type
FilterSpec(field="age", operator="gt", value=25)
FilterSpec(field="name", operator="eq", value="Alice")

# Membership: value is a list/tuple
FilterSpec(field="status", operator="in", value=["active", "pending"])

# Text: value is a string
FilterSpec(field="name", operator="contains", value="ali")

# Pattern: SQL-style wildcards for like/ilike
FilterSpec(field="email", operator="like", value="%@example.com")
FilterSpec(field="name", operator="ilike", value="%alice%")

# Regex: value is a regex pattern string
FilterSpec(field="code", operator="regex", value=r"^[A-Z]{3}-\d+$")

# Range: value is (low, high)
FilterSpec(field="age", operator="between", value=(18, 65))

# Null checks: value is ignored
FilterSpec(field="deleted_at", operator="is_null")

# Emptiness: value is ignored
FilterSpec(field="tags", operator="not_empty")
```

## Applying Filters

### In-Memory with FilterEngine

`FilterEngine` applies filters directly to Python sequences:

```python
from pypaginate import FilterSpec
from pypaginate.filtering.engine import FilterEngine
from pypaginate.filtering.registry import create_default_registry

engine = FilterEngine(registry=create_default_registry())

users = [
    {"name": "Alice", "age": 30, "status": "active"},
    {"name": "Bob", "age": 25, "status": "inactive"},
    {"name": "Charlie", "age": 35, "status": "active"},
]

# Single filter
active = engine.apply(users, [FilterSpec(field="status", value="active")])
# [Alice, Charlie]

# Multiple filters (AND)
result = engine.apply(users, [
    FilterSpec(field="status", value="active"),
    FilterSpec(field="age", operator="gte", value=30),
])
# [Alice, Charlie]
```

### In-Memory with MemoryFilterBackend

`MemoryFilterBackend` satisfies the `FilterBackend` protocol for use in pipelines:

```python
from pypaginate import FilterSpec
from pypaginate.adapters.memory import MemoryFilterBackend

backend = MemoryFilterBackend()

users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
]

filtered = backend.apply_filters(users, [
    FilterSpec(field="age", operator="gte", value=30),
])
# [{"name": "Alice", "age": 30}]
```

### SQLAlchemy

`SQLAlchemyFilterBackend` translates `FilterSpec` to WHERE clauses:

```python
from sqlalchemy import select
from pypaginate import FilterSpec
from pypaginate.adapters.sqlalchemy import SQLAlchemyFilterBackend

backend = SQLAlchemyFilterBackend()

stmt = select(User)
filtered_stmt = backend.apply_filters(stmt, [
    FilterSpec(field="status", operator="eq", value="active"),
    FilterSpec(field="age", operator="gte", value=18),
])
# SELECT * FROM user WHERE status = 'active' AND age >= 18
```

## AND/OR Logic

Each `FilterSpec` has a `logic` field controlling how it combines with others:

```python
from pypaginate import FilterSpec, FilterLogic

filters = [
    # AND filters (default): all must match
    FilterSpec(field="age", operator="gte", value=18),

    # OR filters: at least one must match
    FilterSpec(field="role", value="admin", logic=FilterLogic.OR),
    FilterSpec(field="role", value="moderator", logic=FilterLogic.OR),
]
# Result: age >= 18 AND (role = "admin" OR role = "moderator")
```

**Rule**: All AND filters must pass, then at least one OR filter must pass.

## Dot Notation for Nested Fields

Access nested attributes or dictionary keys with dot notation:

```python
from pypaginate import FilterSpec

# Works with dicts
FilterSpec(field="address.city", value="Paris")
# Accesses item["address"]["city"]

# Works with objects
FilterSpec(field="profile.email", operator="contains", value="@example.com")
# Accesses item.profile.email
```

## Pipeline Usage

Filters integrate naturally with the pagination pipeline:

```python
from pypaginate import FilterSpec, OffsetParams
from pypaginate.adapters.memory import MemoryBackend, MemoryFilterBackend
from pypaginate.engine.paginator import Paginator
from pypaginate.engine.pipeline import SyncPipeline

pipeline = SyncPipeline(
    Paginator(MemoryBackend()),
    filter_backend=MemoryFilterBackend(),
)

page = pipeline.execute(
    users,
    OffsetParams(page=1, limit=20),
    filters=[
        FilterSpec(field="status", value="active"),
        FilterSpec(field="age", operator="gte", value=18),
    ],
)
```

## Custom Operators

Register custom operators via the `OperatorRegistry`:

```python
from pypaginate.filtering.registry import OperatorRegistry, create_default_registry

class DivisibleBy:
    __slots__ = ()

    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool:
        return int(field_value) % int(spec_value) == 0  # type: ignore[arg-type]

registry = create_default_registry()
registry.register("divisible_by", DivisibleBy())

# Use with FilterEngine
from pypaginate.filtering.engine import FilterEngine

engine = FilterEngine(registry=registry)
```

## Error Handling

```python
from pypaginate import FilterError

try:
    result = engine.apply(users, [
        FilterSpec(field="age", operator="unknown_op", value=5),
    ])
except FilterError as e:
    print(f"Filter error: {e}")
```

## Next Steps

- [Operators Reference](operators.md) -- Detailed examples for all 20 operators
- [Nested Filter Groups](json-logic.md) -- Nested And/Or groups for complex expressions
