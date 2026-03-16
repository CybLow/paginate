# Filter Expressions

pypaginate provides a type-safe filter system based on `FilterSpec` models,
`And`/`Or` group builders, and a compile-once predicate engine. The same filter
specs work for both in-memory and SQLAlchemy backends.

---

## FilterSpec

A `FilterSpec` is an immutable Pydantic model that describes a single filter condition:

```python
from pypaginate import FilterSpec

# Equality (default operator)
FilterSpec(field="status", value="active")

# Comparison
FilterSpec(field="age", operator="gte", value=18)

# Pattern matching
FilterSpec(field="name", operator="contains", value="john")

# Null check
FilterSpec(field="deleted_at", operator="is_null")
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `field` | `str` | required | Field name (supports nested: `"address.city"`) |
| `operator` | `FilterOperator` | `"eq"` | Operator name (Literal type, validated at definition) |
| `value` | `Any` | `None` | Comparison value |
| `logic` | `FilterLogic` | `FilterLogic.AND` | How to combine with other specs |

---

## Operators

pypaginate supports 20 operators, all type-checked as `Literal` values:

### Comparison

| Operator | SQL Equivalent | Example |
|----------|---------------|---------|
| `eq` | `=` | `FilterSpec(field="status", operator="eq", value="active")` |
| `ne` | `!=` | `FilterSpec(field="status", operator="ne", value="deleted")` |
| `gt` | `>` | `FilterSpec(field="age", operator="gt", value=18)` |
| `gte` | `>=` | `FilterSpec(field="age", operator="gte", value=18)` |
| `lt` | `<` | `FilterSpec(field="score", operator="lt", value=100)` |
| `lte` | `<=` | `FilterSpec(field="score", operator="lte", value=100)` |

### Membership

| Operator | SQL Equivalent | Example |
|----------|---------------|---------|
| `in` | `IN (...)` | `FilterSpec(field="role", operator="in", value=["admin", "mod"])` |
| `not_in` | `NOT IN (...)` | `FilterSpec(field="status", operator="not_in", value=["banned"])` |
| `between` | `BETWEEN ... AND ...` | `FilterSpec(field="age", operator="between", value=[18, 65])` |

### Text / Pattern

| Operator | SQL Equivalent | Example |
|----------|---------------|---------|
| `contains` | `LIKE '%...%'` | `FilterSpec(field="name", operator="contains", value="john")` |
| `starts_with` | `LIKE '...%'` | `FilterSpec(field="name", operator="starts_with", value="J")` |
| `ends_with` | `LIKE '%...'` | `FilterSpec(field="email", operator="ends_with", value=".com")` |
| `like` | `LIKE` | `FilterSpec(field="name", operator="like", value="%john%")` |
| `ilike` | `ILIKE` | `FilterSpec(field="name", operator="ilike", value="%JOHN%")` |
| `regex` | `~` / `REGEXP` | `FilterSpec(field="code", operator="regex", value=r"^[A-Z]{3}")` |

### Null / Existence

| Operator | SQL Equivalent | Example |
|----------|---------------|---------|
| `is_null` | `IS NULL` | `FilterSpec(field="deleted_at", operator="is_null")` |
| `is_not_null` | `IS NOT NULL` | `FilterSpec(field="email", operator="is_not_null")` |
| `empty` | `IS NULL OR = ''` | `FilterSpec(field="bio", operator="empty")` |
| `not_empty` | `IS NOT NULL AND != ''` | `FilterSpec(field="bio", operator="not_empty")` |
| `exists` | (always true) | `FilterSpec(field="id", operator="exists")` |

---

## And/Or Groups (FilterGroup)

For complex boolean logic, use the `And()` and `Or()` builder functions to create
nested `FilterGroup` trees:

```python
from pypaginate import FilterSpec, And, Or

# (status = "active") AND (age >= 18 OR role = "admin")
group = And(
    FilterSpec(field="status", value="active"),
    Or(
        FilterSpec(field="age", operator="gte", value=18),
        FilterSpec(field="role", value="admin"),
    ),
)
```

Groups can be nested up to 5 levels deep (validated by Pydantic):

```python
# Complex nested expression
group = And(
    Or(
        FilterSpec(field="a", value=1),
        FilterSpec(field="b", value=2),
    ),
    Or(
        FilterSpec(field="c", value=3),
        And(
            FilterSpec(field="d", operator="gte", value=10),
            FilterSpec(field="e", operator="lte", value=20),
        ),
    ),
)
# SQL: (a=1 OR b=2) AND (c=3 OR (d>=10 AND e<=20))
```

---

## How Filtering Works

### In-Memory (FilterEngine)

The `FilterEngine` compiles filter specs into **fast predicate closures** once,
then evaluates them per item with minimal overhead:

```{mermaid}
graph LR
    S["FilterSpec list or FilterGroup"] --> C["Compile predicates (once)"]
    C --> P["predicate closures"]
    P --> E["Evaluate per item"]
    E --> R["Filtered list"]
```

```python
from pypaginate.filtering.engine import FilterEngine
from pypaginate.filtering.registry import OperatorRegistry

engine = FilterEngine(OperatorRegistry.default())
filtered = engine.apply(items, [
    FilterSpec(field="age", operator="gte", value=18),
    FilterSpec(field="status", value="active"),
])
```

For flat `FilterSpec` lists, the engine partitions specs by `logic` (AND vs OR):
- All AND specs must match.
- At least one OR spec must match (if any exist).

For `FilterGroup` trees, the engine recursively compiles nested predicates.

### SQLAlchemy (SQLAlchemyFilterBackend)

The SQLAlchemy filter backend translates `FilterSpec` objects into SQLAlchemy
WHERE clauses:

```python
from pypaginate.adapters.sqlalchemy import SQLAlchemyFilterBackend

fb = SQLAlchemyFilterBackend()
modified_query = fb.apply_filters(
    select(User),
    [FilterSpec(field="age", operator="gte", value=18)],
)
# Generates: SELECT * FROM users WHERE users.age >= 18
```

### Pipeline Integration

Both backends integrate with the pipeline for filter + sort + search + paginate:

```python
from pypaginate.engine.pipeline import AsyncPipeline
from pypaginate.engine.paginator import AsyncPaginator
from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend, SQLAlchemyFilterBackend

pipeline = AsyncPipeline(
    AsyncPaginator(SQLAlchemyBackend(session)),
    filter_backend=SQLAlchemyFilterBackend(),
)

result = await pipeline.execute(
    select(User),
    OffsetParams(page=1, limit=20),
    filters=[FilterSpec(field="status", value="active")],
)
```

---

## Nested Field Access

The filter engine supports dotted paths for nested objects:

```python
# Access nested attribute: item.address.city
FilterSpec(field="address.city", operator="eq", value="Paris")
```

The `compile_accessor` function compiles a dotted path into a fast callable that
resolves the value from any object (dict or object with attributes).

---

## Operator Registry

The `OperatorRegistry` maps operator names to operator classes. The default registry
includes all 20 operators. You can create custom registries:

```python
from pypaginate.filtering.registry import OperatorRegistry
from pypaginate.filtering.operators import Eq

registry = OperatorRegistry()
registry.register("eq", Eq)
# Add custom operators the same way
```

Each operator implements the `Operator` protocol:

```python
class Operator(Protocol):
    @staticmethod
    def evaluate(field_value: object, spec_value: object) -> bool: ...
```

---

## Error Handling

Filter errors carry structured details:

```python
from pypaginate.domain.exceptions import FilterError, FilterValidationError

try:
    engine.apply(items, [FilterSpec(field="x", operator="regex", value="[invalid")])
except FilterError as e:
    print(e.details)  # {"pattern": "[invalid", "error": "..."}

try:
    FilterSpec(field="age", operator="between", value=[1, 2, 3])
except FilterValidationError as e:
    print(e.details)  # {"value": "[1, 2, 3]", "length": 3}
```
