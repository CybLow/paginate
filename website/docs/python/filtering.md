---
sidebar_position: 3
title: Filtering
---

# Filtering

`filter(items, where)` returns a new list of the items matching `where`, **in their
original order**. The matching runs in the native engine. For the full operator table
and semantics, see the [shared reference](../general/filtering).

## A single condition

A `FilterSpec` has a `field`, an `operator` (a plain string), and a `value`:

```python
from pypaginate import filter, FilterSpec

users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 17},
    {"name": "Carol", "age": 25},
]

adults = filter(users, FilterSpec(field="age", operator="gte", value=18))
# -> [{"name": "Alice", ...}, {"name": "Carol", ...}]
```

## A list of conditions

Pass a **list of specs** to combine several conditions. Each spec carries its own
`logic` (`"and"` — the default — or `"or"`): every `and` spec must match, and if any
spec uses `or`, at least one `or` spec must also match. An **empty** list matches
everything.

```python
# age >= 18 AND name contains "a"
filter(users, [
    FilterSpec(field="age", operator="gte", value=18),
    FilterSpec(field="name", operator="contains", value="a"),
])

# active AND (role == "admin" OR role == "owner")
filter(users, [
    FilterSpec(field="active", operator="eq", value=True),
    FilterSpec(field="role", operator="eq", value="admin", logic="or"),
    FilterSpec(field="role", operator="eq", value="owner", logic="or"),
])
```

## Nested boolean groups

For clearer nested logic, use the `And()` / `Or()` builders. Each condition is a
`FilterSpec` or another group, so they nest arbitrarily (up to
[5 levels](../general/filtering#nesting-depth-limit)):

```python
from pypaginate import filter, FilterSpec, And, Or

# active AND (role == "admin" OR role == "owner")
where = And(
    FilterSpec(field="active", operator="eq", value=True),
    Or(
        FilterSpec(field="role", operator="eq", value="admin"),
        FilterSpec(field="role", operator="eq", value="owner"),
    ),
)
filter(users, where)
```

## Common operators

```python
# membership
filter(users, FilterSpec(field="role", operator="in", value=["admin", "owner"]))
# inclusive range
filter(users, FilterSpec(field="age", operator="between", value=[18, 65]))
# null check (nullary operators ignore value — pass None)
filter(users, FilterSpec(field="email", operator="is_not_null", value=None))
# SQL LIKE (% = any run, _ = one char); ilike is case-insensitive
filter(users, FilterSpec(field="name", operator="like", value="A%"))
# regex (≤ 200 chars)
filter(users, FilterSpec(field="name", operator="regex", value="^[AEIOU]"))
```

See the [full operator table](../general/filtering#the-20-operators) for all 20.

## Dotted field paths

`field` is resolved through nested maps. Filtering is **strict**: each path must
resolve on every item, and segments may not start with `_`.

```python
filter(users, FilterSpec(field="address.city", operator="eq", value="Paris"))
```

## Errors

`filter()` raises **`FilterError`** (a subclass of `PaginateError`) when a spec can't
be evaluated — an unknown operator, an unresolved field path, a `_`-prefixed segment,
or incomparable operands. Building an over-deep group raises **`FilterValidationError`**
at construction time:

```python
from pypaginate import filter, FilterSpec, FilterError

try:
    filter(users, FilterSpec(field="age", operator="nope", value=1))
except FilterError as exc:
    print(exc)  # "unknown operator: nope"
```

## Next

- [Filtering & operators reference](../general/filtering) — all 20 operators, group depth.
- [Sorting](./sorting) · [Search](./search) · [Pagination](./pagination)
