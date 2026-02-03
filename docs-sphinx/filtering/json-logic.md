# JSON Logic Filtering

pypaginate uses JSON Logic for powerful, expressive filtering.

## What is JSON Logic?

JSON Logic is a way to write logical expressions in JSON format. It's:

- **Portable**: Works in any language (Python, JavaScript, etc.)
- **Safe**: Can be sent from untrusted sources
- **Expressive**: Supports complex nested logic

## Basic Structure

```text
{
  "operator": [arguments]
}
```

In pypaginate, we use a simplified syntax:

```python
# Field-based filter
{"field_name": {"operator": "value"}}

# Logical operators
{"and": [filter1, filter2]}
{"or": [filter1, filter2]}
{"not": filter}
```

## Field Filters

### Simple Comparison

```python
from pypaginate.filters.predicates import FilterEngine

engine = FilterEngine()

# Equality
{"name": {"eq": "Alice"}}

# Not equal
{"status": {"ne": "banned"}}

# Greater than / Less than
{"age": {"gt": 18}}
{"age": {"lt": 65}}

# Greater/less than or equal
{"age": {"gte": 18}}
{"age": {"lte": 65}}
```

### Range Filter

```python
# Between (inclusive)
{"age": {"between": [18, 65]}}

# Equivalent to:
{"and": [
    {"age": {"gte": 18}},
    {"age": {"lte": 65}}
]}
```

### String Operators

```python
# Pattern matching (SQL LIKE style)
{"email": {"like": "%@gmail.com"}}      # ends with @gmail.com
{"name": {"like": "A%"}}                 # starts with A
{"code": {"like": "AB_123"}}             # _ matches single char

# Case-insensitive
{"email": {"ilike": "%@GMAIL.COM"}}

# Prefix/suffix
{"name": {"startswith": "Alice"}}
{"email": {"endswith": ".com"}}

# Regular expression
{"code": {"regex": "^[A-Z]{2}[0-9]{3}$"}}
```

### Collection Operators

```python
# In list
{"status": {"in": ["active", "pending", "review"]}}

# Not in list
{"status": {"not_in": ["banned", "deleted"]}}

# Contains (for array fields)
{"tags": {"contains": "python"}}

# Has any of (array intersection)
{"tags": {"any": ["python", "javascript"]}}

# Has all of (array subset)
{"permissions": {"all": ["read", "write"]}}
```

## Logical Operators

### AND

All conditions must be true:

```python
{
    "and": [
        {"age": {"gte": 18}},
        {"status": {"eq": "active"}},
        {"verified": {"eq": True}}
    ]
}
```

### OR

At least one condition must be true:

```python
{
    "or": [
        {"role": {"eq": "admin"}},
        {"role": {"eq": "moderator"}},
        {"is_owner": {"eq": True}}
    ]
}
```

### NOT

Negate a condition:

```python
# Users who are NOT banned
{"not": {"status": {"eq": "banned"}}}

# Not in list
{"not": {"role": {"in": ["guest", "anonymous"]}}}
```

## Complex Expressions

### Nested Logic

```python
# (admin OR moderator) AND verified AND age >= 18
{
    "and": [
        {
            "or": [
                {"role": {"eq": "admin"}},
                {"role": {"eq": "moderator"}}
            ]
        },
        {"verified": {"eq": True}},
        {"age": {"gte": 18}}
    ]
}
```

### Multiple Conditions on Same Field

```python
# Age between 18 and 65 (inclusive)
{
    "and": [
        {"age": {"gte": 18}},
        {"age": {"lte": 65}}
    ]
}

# Or use between
{"age": {"between": [18, 65]}}
```

### Real-World Examples

#### E-commerce Product Filter

```python
product_filter = {
    "and": [
        {"category": {"in": ["electronics", "computers"]}},
        {"price": {"between": [100, 1000]}},
        {"in_stock": {"eq": True}},
        {
            "or": [
                {"rating": {"gte": 4}},
                {"reviews_count": {"gte": 100}}
            ]
        }
    ]
}

products = engine.filter(all_products, product_filter)
```

#### User Search Filter

```python
user_filter = {
    "and": [
        {"status": {"eq": "active"}},
        {"email_verified": {"eq": True}},
        {
            "or": [
                {"name": {"ilike": "%john%"}},
                {"email": {"ilike": "%john%"}}
            ]
        },
        {"not": {"role": {"eq": "bot"}}}
    ]
}

users = engine.filter(all_users, user_filter)
```

#### Order History Filter

```python
order_filter = {
    "and": [
        {"user_id": {"eq": current_user_id}},
        {"created_at": {"gte": "2024-01-01"}},
        {
            "or": [
                {"status": {"eq": "completed"}},
                {"status": {"eq": "shipped"}}
            ]
        },
        {"total": {"gte": 50}}
    ]
}

orders = engine.filter(all_orders, order_filter)
```

## Nested Field Access

Access nested objects with dot notation:

```python
data = [
    {
        "id": 1,
        "user": {
            "profile": {
                "name": "Alice",
                "settings": {"theme": "dark"}
            }
        }
    }
]

# Filter by nested field
result = engine.filter(data, {
    "user.profile.settings.theme": {"eq": "dark"}
})
```

## Arrays and Nested Objects

```python
data = [
    {
        "id": 1,
        "orders": [
            {"product": "A", "quantity": 2},
            {"product": "B", "quantity": 1}
        ]
    }
]

# Check if any order has quantity > 1
result = engine.filter(data, {
    "orders[*].quantity": {"gt": 1}
})
```

## Validation

pypaginate validates filter syntax:

```python
from pypaginate import FilterException, FilterValidationError

try:
    # Invalid operator
    engine.filter(users, {"age": {"invalid_op": 5}})
except FilterValidationError as e:
    print(f"Invalid filter: {e}")

try:
    # Invalid structure
    engine.filter(users, "not a dict")
except FilterException as e:
    print(f"Filter error: {e}")
```

## API Integration

Accept filters from API clients:

```python
from fastapi import FastAPI, Body
from pypaginate.filters.predicates import FilterEngine

app = FastAPI()
engine = FilterEngine()

@app.post("/users/search")
async def search_users(
    filters: dict = Body(default={}),
):
    """
    Search users with JSON Logic filters.
    
    Example request:
    ```json
    {
        "filters": {
            "and": [
                {"status": {"eq": "active"}},
                {"age": {"gte": 18}}
            ]
        }
    }
    ```
    """
    # Validate and apply filters
    try:
        result = engine.filter(all_users, filters)
        return {"users": result, "count": len(result)}
    except FilterException as e:
        raise HTTPException(400, f"Invalid filter: {e}")
```

## Next Steps

- [Operators Reference](operators.md) - Complete operator documentation
- [SQL Filtering](../integrations/sqlalchemy.md) - Database filtering
- [Basic Filtering](basic.md) - Simpler filter patterns
