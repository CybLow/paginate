---
sidebar_position: 1
title: Basic filtering
---

# Basic filtering

`filter(items, where)` returns a new list of the items that match `where`, **in
their original order**. The matching is done by the Rust core, so Python and
TypeScript return identical results — see [cross-language parity](/concepts/parity).

A single condition is a **`FilterSpec`** with three parts:

| Field | Meaning |
|---|---|
| `field` | Dotted path into each item (e.g. `"age"`, `"address.city"`). |
| `operator` | One of the [20 operators](./operators) (plain string, e.g. `"gte"`). |
| `value` | The comparison value — its meaning depends on the operator. |

In Python a `FilterSpec` is a dataclass; in TypeScript it is a plain object.

## A single condition

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

```ts
import { filter } from "@cyblow/paginate";

const users = [
  { name: "Alice", age: 30 },
  { name: "Bob", age: 17 },
  { name: "Carol", age: 25 },
];

const adults = filter(users, { field: "age", operator: "gte", value: 18 });
// -> [{ name: "Alice", ... }, { name: "Carol", ... }]
```

Both calls return the same items in the same order ([parity](/concepts/parity)).

## A list of conditions

Pass a **list of specs** to combine several conditions. Each spec carries its own
`logic` (`"and"` — the default — or `"or"`). The rule the core applies to a flat
list is: **every `and` spec must match, and — if any spec uses `or` — at least one
`or` spec must also match.**

```python
from pypaginate import filter, FilterSpec

# age >= 18 AND name contains "a"
result = filter(users, [
    FilterSpec(field="age", operator="gte", value=18),
    FilterSpec(field="name", operator="contains", value="a"),
])

# active AND (role == "admin" OR role == "owner")
result = filter(users, [
    FilterSpec(field="active", operator="eq", value=True),
    FilterSpec(field="role", operator="eq", value="admin", logic="or"),
    FilterSpec(field="role", operator="eq", value="owner", logic="or"),
])
```

```ts
import { filter } from "@cyblow/paginate";

// age >= 18 AND name contains "a"
const result = filter(users, [
  { field: "age", operator: "gte", value: 18 },
  { field: "name", operator: "contains", value: "a" },
]);

// active AND (role == "admin" OR role == "owner")
const grouped = filter(users, [
  { field: "active", operator: "eq", value: true },
  { field: "role", operator: "eq", value: "admin", logic: "or" },
  { field: "role", operator: "eq", value: "owner", logic: "or" },
]);
```

For clearer nested boolean logic, prefer the `And()` / `Or()` builders — see
[boolean groups](./groups). An **empty** filter list matches every item.

## Dotted field paths

`field` is a dotted path resolved through nested maps. Filtering is **strict**:
each path must resolve on every item, and path segments may **not** start with `_`.

```python
filter(users, FilterSpec(field="address.city", operator="eq", value="Paris"))
```

```ts
filter(users, { field: "address.city", operator: "eq", value: "Paris" });
```

## Errors

The Python `filter()` raises **`FilterError`** (a subclass of `PaginateError`) when
a spec can't be evaluated — an unknown operator, a field path that doesn't resolve,
a segment starting with `_`, or operands that aren't comparable:

```python
from pypaginate import filter, FilterSpec, FilterError

try:
    filter(users, FilterSpec(field="age", operator="nope", value=1))
except FilterError as exc:
    print(exc)  # "unknown operator: nope"
```

In TypeScript the same conditions throw an error carrying the core's message:

```ts
import { filter } from "@cyblow/paginate";

try {
  filter(users, { field: "age", operator: "nope" as any, value: 1 });
} catch (err) {
  console.error((err as Error).message); // "unknown operator: nope"
}
```

## Next

- [Operators](./operators) — the full table of 20 operators with examples.
- [Boolean groups](./groups) — nest conditions with `And()` / `Or()`.
