---
sidebar_position: 1
title: Basic sorting
---

# Basic sorting

`sort` reorders an in-memory collection by a single key. You describe the key with a
**`SortSpec`** — a field path and a direction — and the Rust core returns the items in
that order. The Python and TypeScript packages produce **identical results** (see
[cross-language parity](../concepts/parity)).

## The SortSpec

| Field | Type | Default | Meaning |
|---|---|---|---|
| `field` | string | — (required) | Dotted field path to sort by, e.g. `age` or `address.city`. |
| `direction` | `"asc"` \| `"desc"` | `"asc"` | Ascending or descending order. |
| `nulls` | `"first"` \| `"last"` | `"last"` | Where missing / null values go (see [multi-key](./multi-key)). |

In Python a `SortSpec` is a dataclass; in TypeScript it is a plain object. Both use the
same `snake_case` field names and the same plain-string `direction` values.

## Sort by one key

```python
from pypaginate import sort, SortSpec

users = [
    {"name": "Bob", "age": 30},
    {"name": "Alice", "age": 25},
    {"name": "Carol", "age": 42},
]

by_age = sort(users, SortSpec(field="age"))               # ascending (default)
# -> Alice (25), Bob (30), Carol (42)

oldest_first = sort(users, SortSpec(field="age", direction="desc"))
# -> Carol (42), Bob (30), Alice (25)
```

```ts
import { sort } from "@cyblow/paginate";

const users = [
  { name: "Bob", age: 30 },
  { name: "Alice", age: 25 },
  { name: "Carol", age: 42 },
];

const byAge = sort(users, { field: "age" });              // ascending (default)
// -> Alice (25), Bob (30), Carol (42)

const oldestFirst = sort(users, { field: "age", direction: "desc" });
// -> Carol (42), Bob (30), Alice (25)
```

`sort` returns a **new list / array** of your original items in the new order — the
input is never mutated, and the items themselves are never copied through the core (the
engine returns indices and the package selects your objects). See
[architecture](../concepts/architecture).

## Stability

The sort is **stable**: items that compare equal on the sort key keep their original
relative order. This is what makes layering keys predictable — and it is the basis for
[multi-key sorting](./multi-key).

```python
from pypaginate import sort, SortSpec

rows = [
    {"name": "Bob", "age": 30},
    {"name": "Ann", "age": 30},
    {"name": "Cy", "age": 30},
]

sort(rows, SortSpec(field="age"))
# all ages equal -> original order preserved: Bob, Ann, Cy
```

```ts
import { sort } from "@cyblow/paginate";

const rows = [
  { name: "Bob", age: 30 },
  { name: "Ann", age: 30 },
  { name: "Cy", age: 30 },
];

sort(rows, { field: "age" });
// all ages equal -> original order preserved: Bob, Ann, Cy
```

## Dotted field paths

`field` may reach into nested objects with a dotted path:

```python
from pypaginate import sort, SortSpec

orders = [
    {"id": 1, "customer": {"name": "Zoe"}},
    {"id": 2, "customer": {"name": "Amy"}},
]

sort(orders, SortSpec(field="customer.name"))   # -> Amy, Zoe
```

```ts
import { sort } from "@cyblow/paginate";

const orders = [
  { id: 1, customer: { name: "Zoe" } },
  { id: 2, customer: { name: "Amy" } },
];

sort(orders, { field: "customer.name" });        // -> Amy, Zoe
```

A field that is missing on an item (or explicitly `null` / `None`) is treated as null
and placed according to `nulls` — see [null placement](./multi-key#null-placement).

## Incomparable values raise SortError

The core compares values the way Python does: numbers order against numbers and text
orders against text, but a number cannot be ordered against a string. When a field holds
a mix of those kinds across items, the sort fails fast with a **`SortError`**.

```python
from pypaginate import sort, SortSpec, SortError

mixed = [{"v": 1}, {"v": "two"}]   # number vs string on the same field

try:
    sort(mixed, SortSpec(field="v"))
except SortError as exc:
    print("cannot sort:", exc)     # "field values are not order-comparable"
```

```ts
import { sort, SortError } from "@cyblow/paginate";

const mixed = [{ v: 1 }, { v: "two" }];   // number vs string on the same field

try {
  sort(mixed, { field: "v" });
} catch (err) {
  if (err instanceof SortError) console.log("cannot sort:", err.message);
}
```

`SortError` is part of the shared error hierarchy (`SortError` → `PaginateError`),
mirrored byte-for-byte across both packages.

## Next

- [Multi-key sorting](./multi-key) — layer several keys with tie-breaking and per-key
  null placement.
