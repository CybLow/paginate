# Operators Reference

pypaginate ships 20 built-in filter operators. All are provided by the native core engine.

```python
from pypaginate import FilterSpec
```

## Comparison Operators

### eq -- Equal

```python
FilterSpec(field="status", operator="eq", value="active")
FilterSpec(field="status", value="active")  # "eq" is the default
```

Matches when the field value equals the spec value.

### ne -- Not Equal

```python
FilterSpec(field="status", operator="ne", value="banned")
```

Matches when the field value does not equal the spec value.

### gt -- Greater Than

```python
FilterSpec(field="age", operator="gt", value=18)
FilterSpec(field="created_at", operator="gt", value=datetime(2024, 1, 1))
```

Matches when the field value is strictly greater than the spec value.

### gte -- Greater Than or Equal

```python
FilterSpec(field="age", operator="gte", value=18)
```

Matches when the field value is greater than or equal to the spec value.

### lt -- Less Than

```python
FilterSpec(field="price", operator="lt", value=100.0)
```

Matches when the field value is strictly less than the spec value.

### lte -- Less Than or Equal

```python
FilterSpec(field="quantity", operator="lte", value=0)
```

Matches when the field value is less than or equal to the spec value.

## Membership Operators

### in -- In List

```python
FilterSpec(field="status", operator="in", value=["active", "pending"])
FilterSpec(field="priority", operator="in", value=[1, 2, 3])
```

Matches when the field value is contained in the provided sequence.

### not_in -- Not In List

```python
FilterSpec(field="role", operator="not_in", value=["banned", "suspended"])
```

Matches when the field value is not contained in the provided sequence.

## Text Operators

### contains -- Substring Match

```python
FilterSpec(field="name", operator="contains", value="alice")
FilterSpec(field="description", operator="contains", value="urgent")
```

Matches when the string spec value appears anywhere in the string field value. Both sides are cast to `str`.

### starts_with -- Prefix Match

```python
FilterSpec(field="email", operator="starts_with", value="admin@")
FilterSpec(field="code", operator="starts_with", value="PRJ-")
```

Matches when the field value starts with the spec value.

### ends_with -- Suffix Match

```python
FilterSpec(field="email", operator="ends_with", value="@example.com")
FilterSpec(field="filename", operator="ends_with", value=".pdf")
```

Matches when the field value ends with the spec value.

## Pattern Operators

### like -- SQL LIKE

```python
FilterSpec(field="name", operator="like", value="A%")       # starts with A
FilterSpec(field="email", operator="like", value="%@%.com")  # contains @ and ends with .com
```

SQL-style pattern matching. `%` matches any sequence of characters, `_` matches any single character. Case-sensitive.

In-memory: optimized to use `str.startswith()`, `str.endswith()`, or `in` when the pattern allows, falling back to `fnmatch` for complex patterns.

### ilike -- Case-Insensitive LIKE

```python
FilterSpec(field="name", operator="ilike", value="%alice%")
```

Same as `like` but case-insensitive. In SQLAlchemy, translates to `column.ilike(value)`.

### regex -- Regular Expression

```python
FilterSpec(field="phone", operator="regex", value=r"^\+\d{1,3}-\d+$")
FilterSpec(field="code", operator="regex", value=r"^[A-Z]{3}-\d{4}$")
```

Matches when the field value matches the regex pattern. The pattern is compiled once and reused.

Raises `FilterError` if the pattern is invalid.

## Range Operators

### between -- Inclusive Range

```python
FilterSpec(field="age", operator="between", value=(18, 65))
FilterSpec(field="price", operator="between", value=[10.0, 99.99])
```

Matches when `low <= field_value <= high`. The value must be a two-element sequence.

Raises `FilterValidationError` if the value is not a two-element sequence.

## Null Operators

### is_null -- Is None

```python
FilterSpec(field="deleted_at", operator="is_null")
```

Matches when the field value is `None`. The `value` field is ignored.

In SQLAlchemy: translates to `column.is_(None)`.

### is_not_null -- Is Not None

```python
FilterSpec(field="email", operator="is_not_null")
```

Matches when the field value is not `None`. The `value` field is ignored.

In SQLAlchemy: translates to `column.is_not(None)`.

## Emptiness Operators

### empty -- Is Empty

```python
FilterSpec(field="tags", operator="empty")
FilterSpec(field="bio", operator="empty")
```

Matches when the field value is `None`, `""` (empty string), or `[]` (empty list). The `value` field is ignored.

### not_empty -- Is Not Empty

```python
FilterSpec(field="tags", operator="not_empty")
```

Matches when the field value is not `None`, not `""`, and not `[]`. The `value` field is ignored.

## Existence Operators

### exists -- Field Exists

```python
FilterSpec(field="optional_field", operator="exists")
```

Always returns `True` if the field can be accessed. Useful for checking that a field exists on the item. The `value` field is ignored.

## Operator Summary Table

| Operator | Value | In-Memory | SQLAlchemy |
|----------|-------|-----------|------------|
| `eq` | same as field | `==` | `column == value` |
| `ne` | same as field | `!=` | `column != value` |
| `gt` | same as field | `>` | `column > value` |
| `gte` | same as field | `>=` | `column >= value` |
| `lt` | same as field | `<` | `column < value` |
| `lte` | same as field | `<=` | `column <= value` |
| `in` | sequence | `in` | `column.in_(value)` |
| `not_in` | sequence | `not in` | `column.not_in(value)` |
| `contains` | str | `value in str(field)` | `column.contains(value)` |
| `starts_with` | str | `str.startswith()` | `column.startswith(value)` |
| `ends_with` | str | `str.endswith()` | `column.endswith(value)` |
| `like` | str (with `%`/`_`) | fnmatch/string | `column.like(value)` |
| `ilike` | str (with `%`/`_`) | case-insensitive | `column.ilike(value)` |
| `regex` | str (regex) | `re.search()` | `column.regexp_match(value)` |
| `between` | `(low, high)` | `low <= x <= high` | `column.between(low, high)` |
| `is_null` | ignored | `is None` | `column.is_(None)` |
| `is_not_null` | ignored | `is not None` | `column.is_not(None)` |
| `empty` | ignored | `None / "" / []` | N/A |
| `not_empty` | ignored | not `None / "" / []` | N/A |
| `exists` | ignored | always True | N/A |

## Custom Operators

These 20 operators are implemented in the bundled native core engine and are not
Python-registrable: `FilterEngine()` takes no arguments and there is no public
operator registry. For logic not covered by a built-in operator, filter at the
application layer, or open an issue to request adding the operator to the core.
