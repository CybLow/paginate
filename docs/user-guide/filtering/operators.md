# Operators Reference

Complete reference for all pypaginate filter operators.

## Comparison Operators

### `eq` - Equal

Exact equality comparison.

```python
{"name": {"eq": "Alice"}}
{"age": {"eq": 30}}
{"is_active": {"eq": True}}
{"data": {"eq": None}}
```

### `ne` - Not Equal

Inequality comparison.

```python
{"status": {"ne": "deleted"}}
{"role": {"ne": "guest"}}
```

### `gt` - Greater Than

Strictly greater than.

```python
{"age": {"gt": 18}}        # age > 18
{"price": {"gt": 99.99}}
{"date": {"gt": "2024-01-01"}}
```

### `gte` - Greater Than or Equal

Greater than or equal to.

```python
{"age": {"gte": 18}}       # age >= 18
{"score": {"gte": 0}}
```

### `lt` - Less Than

Strictly less than.

```python
{"age": {"lt": 65}}        # age < 65
{"attempts": {"lt": 3}}
```

### `lte` - Less Than or Equal

Less than or equal to.

```python
{"age": {"lte": 65}}       # age <= 65
{"priority": {"lte": 5}}
```

### `between` - Range (Inclusive)

Value is between two bounds (inclusive).

```python
{"age": {"between": [18, 65]}}      # 18 <= age <= 65
{"price": {"between": [10.0, 100.0]}}
{"date": {"between": ["2024-01-01", "2024-12-31"]}}
```

## String Operators

### `like` - Pattern Match

SQL LIKE-style pattern matching.

| Pattern | Matches |
|---------|---------|
| `%` | Any sequence of characters |
| `_` | Any single character |

```python
{"email": {"like": "%@gmail.com"}}    # Ends with @gmail.com
{"name": {"like": "A%"}}               # Starts with A
{"code": {"like": "AB_123"}}           # AB followed by any char, then 123
{"name": {"like": "%John%"}}           # Contains "John"
```

### `ilike` - Case-Insensitive Pattern

Same as `like` but case-insensitive.

```python
{"email": {"ilike": "%@GMAIL.COM"}}   # Matches alice@gmail.com
{"name": {"ilike": "alice"}}           # Matches "Alice", "ALICE"
```

### `startswith` - Starts With

String begins with value.

```python
{"name": {"startswith": "Dr."}}
{"email": {"startswith": "admin"}}
```

### `endswith` - Ends With

String ends with value.

```python
{"email": {"endswith": ".edu"}}
{"filename": {"endswith": ".pdf"}}
```

### `contains` - Contains Substring

String contains value (for string fields).

```python
{"bio": {"contains": "developer"}}
{"description": {"contains": "python"}}
```

### `regex` - Regular Expression

Match against regular expression pattern.

```python
{"phone": {"regex": "^\\+1[0-9]{10}$"}}     # US phone format
{"email": {"regex": ".*@company\\.com$"}}   # Company email
{"code": {"regex": "^[A-Z]{2}[0-9]{4}$"}}   # 2 letters + 4 digits
```

!!! warning "Regex Performance"
    Regular expressions can be slow. Use simpler operators when possible.

## Collection Operators

### `in` - In List

Value is in the given list.

```python
{"status": {"in": ["active", "pending"]}}
{"role": {"in": ["admin", "moderator", "user"]}}
{"country": {"in": ["US", "CA", "MX"]}}
```

### `not_in` - Not In List

Value is not in the given list.

```python
{"status": {"not_in": ["banned", "deleted"]}}
{"role": {"not_in": ["guest", "anonymous"]}}
```

### `contains` - Array Contains

Array field contains the value.

```python
{"tags": {"contains": "python"}}           # tags array contains "python"
{"permissions": {"contains": "admin"}}
```

### `any` - Any Match

Array field contains any of the given values.

```python
{"tags": {"any": ["python", "javascript", "go"]}}
# Matches if tags contains at least one of these
```

### `all` - All Match

Array field contains all of the given values.

```python
{"permissions": {"all": ["read", "write"]}}
# Matches only if both "read" AND "write" are in permissions
```

## Null/Empty Operators

### `null` - Null Check

Check if value is null.

```python
{"deleted_at": {"null": True}}     # Field is null
{"manager_id": {"null": False}}    # Field is not null
```

### `empty` - Empty Check

Check if value is empty (null, empty string, or empty array).

```python
{"bio": {"empty": True}}           # null, "", or []
{"tags": {"empty": False}}         # Has content
```

### `exists` - Field Exists

Check if field exists in the object.

```python
{"metadata.custom_field": {"exists": True}}
{"optional_field": {"exists": False}}
```

## Logical Operators

### `and` - Logical AND

All conditions must be true.

```python
{
    "and": [
        {"age": {"gte": 18}},
        {"status": {"eq": "active"}},
        {"verified": {"eq": True}}
    ]
}
```

### `or` - Logical OR

At least one condition must be true.

```python
{
    "or": [
        {"role": {"eq": "admin"}},
        {"role": {"eq": "moderator"}}
    ]
}
```

### `not` - Logical NOT

Negate a condition.

```python
{"not": {"status": {"eq": "banned"}}}

{"not": {
    "or": [
        {"role": {"eq": "guest"}},
        {"role": {"eq": "anonymous"}}
    ]
}}
```

## Type-Specific Behavior

### Numbers

```python
# Integer comparison
{"count": {"eq": 5}}
{"count": {"gte": 0}}

# Float comparison
{"price": {"lte": 99.99}}
{"rating": {"between": [4.0, 5.0]}}
```

### Strings

```python
# Exact match
{"name": {"eq": "Alice"}}

# Pattern matching
{"email": {"like": "%@example.com"}}

# Case-insensitive
{"name": {"ilike": "alice"}}
```

### Booleans

```python
{"is_active": {"eq": True}}
{"is_deleted": {"eq": False}}
{"verified": {"ne": False}}
```

### Dates/Datetimes

Dates can be compared as strings in ISO format:

```python
{"created_at": {"gte": "2024-01-01"}}
{"updated_at": {"between": ["2024-01-01T00:00:00", "2024-12-31T23:59:59"]}}
{"expires_at": {"lt": "2024-06-01"}}
```

### Null Values

```python
{"deleted_at": {"null": True}}    # Is null
{"manager": {"null": False}}      # Is not null
{"value": {"eq": None}}           # Also checks for null
```

## Operator Aliases

Some operators have aliases for convenience:

| Primary | Alias |
|---------|-------|
| `eq` | `==`, `equals` |
| `ne` | `!=`, `not_equals` |
| `gt` | `>` |
| `gte` | `>=` |
| `lt` | `<` |
| `lte` | `<=` |

## SQL Translation

When using `SqlFilterAdapter`, operators translate to SQL:

| pypaginate | SQL |
|------------|-----|
| `eq` | `= value` |
| `ne` | `!= value` |
| `gt` | `> value` |
| `gte` | `>= value` |
| `lt` | `< value` |
| `lte` | `<= value` |
| `in` | `IN (...)` |
| `like` | `LIKE pattern` |
| `ilike` | `ILIKE pattern` |
| `null: True` | `IS NULL` |
| `null: False` | `IS NOT NULL` |
| `between` | `BETWEEN a AND b` |

## Examples by Use Case

### User Status Filter

```python
{"and": [
    {"status": {"in": ["active", "pending"]}},
    {"email_verified": {"eq": True}},
    {"banned_at": {"null": True}}
]}
```

### Price Range

```python
{"and": [
    {"price": {"gte": 10}},
    {"price": {"lte": 100}},
    {"in_stock": {"eq": True}}
]}
# Or: {"price": {"between": [10, 100]}}
```

### Search by Name/Email

```python
{"or": [
    {"name": {"ilike": "%search_term%"}},
    {"email": {"ilike": "%search_term%"}}
]}
```

### Date Range

```python
{"created_at": {"between": ["2024-01-01", "2024-03-31"]}}
```

### Complex Permission Check

```python
{"or": [
    {"role": {"eq": "admin"}},
    {"and": [
        {"role": {"eq": "user"}},
        {"permissions": {"contains": "special_access"}}
    ]}
]}
```
