---
sidebar_position: 7
title: Filtering & operators
---

# Filtering & operators

Filtering is described by **specs** that are evaluated by the Rust core, so the
operators and their semantics are identical in every language. This page is the
canonical reference for the vocabulary; for runnable, idiomatic code see the
[Python](../python/filtering) and [TypeScript](../typescript/filtering) filtering
guides.

## A single condition — `FilterSpec`

A condition has three parts (plus an optional `logic` for flat lists):

| Field | Meaning |
|---|---|
| `field` | Dotted path into each item (e.g. `"age"`, `"address.city"`). |
| `operator` | One of the [20 operators](#the-20-operators) (a plain string, e.g. `"gte"`). |
| `value` | The comparison value — its meaning depends on the operator. |

In Python a `FilterSpec` is a dataclass; in TypeScript it is a plain object — the same
field names and the same plain-string operator values.

```python
FilterSpec(field="age", operator="gte", value=18)   # Python
```

```ts
{ field: "age", operator: "gte", value: 18 }          // TypeScript
```

## The 20 operators

Operators are plain strings, defined once in the core. They behave identically across
languages — see [parity](./parity).

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
| `is_null` | Value is null / absent | *(ignored)* |
| `is_not_null` | Value is present | *(ignored)* |
| `regex` | Regular-expression match (≤ 200 chars) | `"^A.*e$"` |
| `empty` | Empty string / list (or null) | *(ignored)* |
| `not_empty` | Non-empty string / list | *(ignored)* |
| `exists` | Field / key resolves on the item | *(ignored)* |

:::note Nullary operators
`is_null`, `is_not_null`, `empty`, `not_empty`, and `exists` ignore `value`. In Python
`FilterSpec` requires the field, so pass `value=None`; in TypeScript `value` is
optional and may be omitted.
:::

`like` / `ilike` use SQL wildcards: `%` matches any run of characters, `_` matches
exactly one. `between` takes a two-element `[lo, hi]` list with **inclusive** bounds.

## Combining conditions

### Flat list (AND / OR)

A list of specs combines them; each spec carries its own `logic` (`"and"` — the
default — or `"or"`). The rule the core applies to a flat list is: **every `and` spec
must match, and — if any spec uses `or` — at least one `or` spec must also match.** An
**empty** filter list matches every item.

### Nested boolean groups

For anything beyond a flat list, build a tree with the `And()` / `Or()` builders.
`And(...)` matches when **all** of its conditions match; `Or(...)` when **any** do.
Each condition is either a `FilterSpec` or another group, so they nest arbitrarily —
for example `active AND (role == "admin" OR role == "owner")`.

#### Nesting depth limit

Groups may nest **at most 5 levels deep** (`MAX_FILTER_DEPTH = 5`). Depth is `1 + the
deepest nested group`; a group whose children are all leaf specs is depth 1. The limit
is checked **at construction time** — calling `And()` / `Or()` too deep raises a
validation error immediately, before any data is touched. Five levels is plenty for
real query trees; the cap guards against pathological, deeply recursive inputs.

## Dotted field paths and strictness

`field` is a dotted path resolved through nested maps (`"address.city"`). Filtering is
**strict**: the path must resolve on every item, and path segments may **not** start
with `_`. A path that doesn't resolve, an unknown operator, or operands that aren't
comparable, raise an error.

## Errors

The core raises a filter error (`FilterError` in Python, the same hierarchy in
TypeScript) for an unknown operator, an unresolved field path, or incomparable
operands; constructing an over-deep group raises a validation error
(`FilterValidationError`). See the language guides for handling them.

## Next

- [Python filtering](../python/filtering) · [TypeScript filtering](../typescript/filtering)
- [Sorting semantics](./sorting) · [Search & ranking](./search)
