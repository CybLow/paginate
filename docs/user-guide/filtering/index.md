# Filtering

pypaginate provides powerful filtering capabilities using JSON Logic.

## Overview

| Feature | Description |
|---------|-------------|
| [Basic Filtering](basic.md) | Simple filter expressions |
| [JSON Logic](json-logic.md) | Complex nested logic |
| [Operators Reference](operators.md) | All available operators |

## Quick Example

```python
from pypaginate.filters.predicates import FilterEngine

engine = FilterEngine()

users = [
    {"name": "Alice", "age": 30, "status": "active"},
    {"name": "Bob", "age": 25, "status": "inactive"},
    {"name": "Charlie", "age": 35, "status": "active"},
]

# Simple filter
active = engine.filter(users, {"status": {"eq": "active"}})
# [Alice, Charlie]

# Complex filter with AND
adults_active = engine.filter(users, {
    "and": [
        {"age": {"gte": 30}},
        {"status": {"eq": "active"}}
    ]
})
# [Alice, Charlie]
```

## Filter Specification

Filters are expressed as dictionaries:

```python
# Field + Operator + Value
{"field": {"operator": "value"}}

# Examples
{"name": {"eq": "Alice"}}           # name equals "Alice"
{"age": {"gte": 18}}                 # age >= 18
{"status": {"in": ["active", "pending"]}}  # status in list
```

## Combining Filters

Use `and`, `or`, and `not` for complex logic:

```python
# AND: All conditions must match
{"and": [
    {"age": {"gte": 18}},
    {"status": {"eq": "active"}}
]}

# OR: Any condition matches
{"or": [
    {"role": {"eq": "admin"}},
    {"role": {"eq": "moderator"}}
]}

# NOT: Negation
{"not": {"status": {"eq": "banned"}}}
```

## Filter Types

### In-Memory Filtering

Filter Python collections:

```python
from pypaginate.filters.predicates import FilterEngine

engine = FilterEngine()
result = engine.filter(items, filter_spec)
```

### SQL Filtering

Apply filters to SQLAlchemy queries:

```python
from pypaginate.filters.sql_adapter import SqlFilterAdapter

adapter = SqlFilterAdapter(User)
conditions = adapter.to_sql_conditions(filter_spec)

stmt = select(User).where(*conditions)
```

## Next Steps

- [Basic Filtering](basic.md) - Learn the fundamentals
- [JSON Logic](json-logic.md) - Complex expressions
- [Operators Reference](operators.md) - All operators
