---
sidebar_position: 2
title: Operators
---

# Operators

There are **20 filter operators**. They are plain strings, defined once in the Rust
core and shared by every language, so they behave identically in Python and
TypeScript — see [cross-language parity](/concepts/parity).

| Operator | Meaning | Example `value` |
|---|---|---|
| `eq` | Equal (`==`) | `18` |
| `ne` | Not equal (`!=`) | `18` |
| `gt` | Greater than (`>`) | `18` |
| `gte` | Greater than or equal (`>=`) | `18` |
| `lt` | Less than (`<`) | `65` |
| `lte` | Less than or equal (`<=`) | `65` |
| `in` | Membership in a list | `["admin", "owner"]` |
| `not_in` | Non-membership in a list | `["banned", "spam"]` |
| `contains` | Substring containment | `"ali"` |
| `starts_with` | String prefix | `"Al"` |
| `ends_with` | String suffix | `"son"` |
| `like` | SQL-style `LIKE`, case-sensitive | `"%ell%"` |
| `ilike` | SQL-style `LIKE`, case-insensitive | `"%ELL%"` |
| `between` | Inclusive range `[lo, hi]` | `[18, 30]` |
| `is_null` | Value is null / absent | `None` (ignored) |
| `is_not_null` | Value is present | `None` (ignored) |
| `regex` | Regular-expression match | `"^A.*e$"` |
| `empty` | Empty string / list (or null) | `None` (ignored) |
| `not_empty` | Non-empty string / list | `None` (ignored) |
| `exists` | Field / key exists | `None` (ignored) |

:::note value for nullary operators
`is_null`, `is_not_null`, `empty`, `not_empty`, and `exists` ignore `value`. In
Python `FilterSpec` requires the field, so pass `value=None`; in TypeScript `value`
is optional and may be omitted.
:::

## Membership: `in` / `not_in`

`value` is a list; the item value must be one of (or none of) its elements.

```python
from pypaginate import filter, FilterSpec

admins = filter(users, FilterSpec(field="role", operator="in", value=["admin", "owner"]))
others = filter(users, FilterSpec(field="role", operator="not_in", value=["admin", "owner"]))
```

```ts
const admins = filter(users, { field: "role", operator: "in", value: ["admin", "owner"] });
const others = filter(users, { field: "role", operator: "not_in", value: ["admin", "owner"] });
```

## Range: `between`

`value` must be a **two-element** `[lo, hi]` list; the bounds are inclusive
(`lo <= field <= hi`).

```python
working_age = filter(users, FilterSpec(field="age", operator="between", value=[18, 65]))
```

```ts
const workingAge = filter(users, { field: "age", operator: "between", value: [18, 65] });
```

## Null checks: `is_null` / `is_not_null`

```python
no_email = filter(users, FilterSpec(field="email", operator="is_null", value=None))
has_email = filter(users, FilterSpec(field="email", operator="is_not_null", value=None))
```

```ts
const noEmail = filter(users, { field: "email", operator: "is_null" });
const hasEmail = filter(users, { field: "email", operator: "is_not_null" });
```

## Substring: `contains`

```python
with_a = filter(users, FilterSpec(field="name", operator="contains", value="a"))
```

```ts
const withA = filter(users, { field: "name", operator: "contains", value: "a" });
```

## Pattern: `like` / `ilike`

SQL `LIKE` wildcards: `%` matches any run of characters and `_` matches exactly one.
`ilike` is the case-insensitive variant.

```python
filter(users, FilterSpec(field="name", operator="like", value="A%"))    # starts with "A"
filter(users, FilterSpec(field="name", operator="ilike", value="%son")) # ends with "son", any case
```

```ts
filter(users, { field: "name", operator: "like", value: "A%" });
filter(users, { field: "name", operator: "ilike", value: "%son" });
```

## Regular expression: `regex`

`value` is a regular-expression pattern (capped at 200 characters).

```python
starts_with_vowel = filter(users, FilterSpec(field="name", operator="regex", value="^[AEIOU]"))
```

```ts
const startsWithVowel = filter(users, { field: "name", operator: "regex", value: "^[AEIOU]" });
```

## Emptiness & presence: `empty` / `not_empty` / `exists`

`empty` matches an empty string, empty list, or null; `not_empty` is its negation.
`exists` matches when the field path resolves on the item.

```python
filter(users, FilterSpec(field="tags", operator="empty", value=None))
filter(users, FilterSpec(field="tags", operator="not_empty", value=None))
filter(users, FilterSpec(field="nickname", operator="exists", value=None))
```

```ts
filter(users, { field: "tags", operator: "empty" });
filter(users, { field: "tags", operator: "not_empty" });
filter(users, { field: "nickname", operator: "exists" });
```

## Next

- [Basic filtering](./basic) — single specs and flat lists.
- [Boolean groups](./groups) — combine operators with `And()` / `Or()`.
