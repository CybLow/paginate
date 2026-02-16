# Basic Filtering

Learn the fundamentals of filtering data with pypaginate.

## The FilterEngine

The `FilterEngine` is your primary tool for in-memory filtering:

```python
from pypaginate.filters.predicates import FilterEngine

engine = FilterEngine()
```

## Simple Filters

### Equality

```python
users = [
    {"name": "Alice", "role": "admin"},
    {"name": "Bob", "role": "user"},
    {"name": "Charlie", "role": "user"},
]

# Find admins
admins = engine.filter(users, {"role": {"eq": "admin"}})
# [{"name": "Alice", "role": "admin"}]
```

### Comparison

```python
users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 35},
]

# Age greater than or equal to 30
result = engine.filter(users, {"age": {"gte": 30}})
# [Alice, Charlie]

# Age less than 30
result = engine.filter(users, {"age": {"lt": 30}})
# [Bob]
```

### Membership

```python
# Status in a list
result = engine.filter(users, {
    "status": {"in": ["active", "pending"]}
})

# Check if list contains value
result = engine.filter(users, {
    "roles": {"contains": "admin"}
})
```

### Pattern Matching

```python
# LIKE pattern (% is wildcard)
result = engine.filter(users, {
    "email": {"like": "%@gmail.com"}
})

# Starts with
result = engine.filter(users, {
    "name": {"startswith": "A"}
})

# Ends with
result = engine.filter(users, {
    "email": {"endswith": ".com"}
})
```

## Combining Conditions

### AND Logic

All conditions must be true:

```python
# Active users aged 30+
result = engine.filter(users, {
    "and": [
        {"age": {"gte": 30}},
        {"status": {"eq": "active"}}
    ]
})
```

### OR Logic

Any condition can be true:

```python
# Admins or moderators
result = engine.filter(users, {
    "or": [
        {"role": {"eq": "admin"}},
        {"role": {"eq": "moderator"}}
    ]
})
```

### NOT Logic

Negate a condition:

```python
# Non-banned users
result = engine.filter(users, {
    "not": {"status": {"eq": "banned"}}
})
```

### Nested Logic

Combine AND, OR, NOT:

```python
# (Active AND age >= 18) OR is_admin
result = engine.filter(users, {
    "or": [
        {
            "and": [
                {"status": {"eq": "active"}},
                {"age": {"gte": 18}}
            ]
        },
        {"is_admin": {"eq": True}}
    ]
})
```

## Filtering Nested Data

Access nested fields with dot notation:

```python
users = [
    {"id": 1, "profile": {"name": "Alice", "settings": {"theme": "dark"}}},
    {"id": 2, "profile": {"name": "Bob", "settings": {"theme": "light"}}},
]

# Filter by nested field
result = engine.filter(users, {
    "profile.settings.theme": {"eq": "dark"}
})
# [User 1]
```

## Filtering Lists

Filter items that contain list fields:

```python
users = [
    {"name": "Alice", "tags": ["python", "django"]},
    {"name": "Bob", "tags": ["javascript", "react"]},
    {"name": "Charlie", "tags": ["python", "fastapi"]},
]

# Users with "python" tag
result = engine.filter(users, {
    "tags": {"contains": "python"}
})
# [Alice, Charlie]
```

## Null and Empty Checks

```python
users = [
    {"name": "Alice", "bio": "Developer"},
    {"name": "Bob", "bio": None},
    {"name": "Charlie", "bio": ""},
]

# Check for null
result = engine.filter(users, {"bio": {"null": True}})
# [Bob]

# Check for non-null
result = engine.filter(users, {"bio": {"null": False}})
# [Alice, Charlie]

# Check for empty (null or "")
result = engine.filter(users, {"bio": {"empty": True}})
# [Bob, Charlie]
```

## Case Sensitivity

By default, string comparisons are case-sensitive:

```python
# Case-sensitive (default)
result = engine.filter(users, {"name": {"eq": "alice"}})
# [] - no match

result = engine.filter(users, {"name": {"eq": "Alice"}})
# [Alice]

# Case-insensitive LIKE
result = engine.filter(users, {"name": {"ilike": "alice"}})
# [Alice]
```

## Error Handling

```python
from pypaginate import FilterException

try:
    result = engine.filter(users, {"invalid": {"unknown_op": "value"}})
except FilterException as e:
    print(f"Filter error: {e}")
```

## Performance Tips

1. **Filter early**: Apply filters before other operations
2. **Use simple operators**: `eq` is faster than `regex`
3. **Index-friendly**: Structure data for efficient access

```python
# Good: Filter first, then paginate
filtered = engine.filter(users, {"status": {"eq": "active"}})
page = paginator.paginate(filtered, params).to_page()

# Less efficient: Paginate all, then check status
# (Don't do this - you'll paginate all data first)
```

## Next Steps

- [JSON Logic](json-logic.md) - Advanced filter expressions
- [Operators Reference](operators.md) - Complete operator list
- [SQL Filtering](../integrations/sqlalchemy.md) - Database filtering
