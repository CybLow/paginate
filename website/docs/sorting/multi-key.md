---
sidebar_position: 2
title: Multi-key sorting
---

# Multi-key sorting

Pass a **sequence of `SortSpec`** to sort by several keys at once. The keys are applied
in **priority order** — the first spec is the primary sort, and each later spec only
breaks ties left by the ones before it. Because the underlying sort is
[stable](./basic#stability), any rows still tied after the last key keep their original
order. The Python and TypeScript packages give **identical results** (see
[cross-language parity](../concepts/parity)).

## Layering keys

Sort departments ascending, then within each department sort salary descending:

```python
from pypaginate import sort, SortSpec

employees = [
    {"name": "Bob", "dept": "eng", "salary": 120},
    {"name": "Ann", "dept": "eng", "salary": 150},
    {"name": "Cy",  "dept": "ops", "salary": 110},
    {"name": "Di",  "dept": "eng", "salary": 150},
]

ordered = sort(employees, [
    SortSpec(field="dept"),                          # primary: dept asc
    SortSpec(field="salary", direction="desc"),      # tie-break: salary desc
])
# eng/150 Ann, eng/150 Di, eng/120 Bob, ops/110 Cy
#   - Ann before Di: same dept AND same salary, so original order wins (stable)
```

```ts
import { sort } from "@cyblow/paginate";

const employees = [
  { name: "Bob", dept: "eng", salary: 120 },
  { name: "Ann", dept: "eng", salary: 150 },
  { name: "Cy",  dept: "ops", salary: 110 },
  { name: "Di",  dept: "eng", salary: 150 },
];

const ordered = sort(employees, [
  { field: "dept" },                          // primary: dept asc
  { field: "salary", direction: "desc" },     // tie-break: salary desc
]);
// eng/150 Ann, eng/150 Di, eng/120 Bob, ops/110 Cy
//   - Ann before Di: same dept AND same salary, so original order wins (stable)
```

Each spec carries its **own** `direction` (and `nulls`), so you can freely mix
ascending and descending keys in one order, as above.

## Null placement

A value is treated as **null** when the field is missing on an item or is explicitly
`null` / `None`. Each `SortSpec` decides where its nulls go with `nulls`:

| `nulls` | Effect |
|---|---|
| `"last"` (default) | Null values sort **after** all non-null values. |
| `"first"` | Null values sort **before** all non-null values. |

Null placement is **independent of `direction`** — setting `nulls="first"` puts nulls
first whether the key is ascending or descending.

```python
from pypaginate import sort, SortSpec

rows = [
    {"name": "Ann", "score": 10},
    {"name": "Bob", "score": None},     # null
    {"name": "Cy",  "score": 5},
    {"name": "Di"},                      # missing field -> null
]

sort(rows, SortSpec(field="score"))                       # nulls last (default)
# -> Cy (5), Ann (10), Bob (None), Di (missing)

sort(rows, SortSpec(field="score", nulls="first"))        # nulls first
# -> Bob (None), Di (missing), Cy (5), Ann (10)

sort(rows, SortSpec(field="score", direction="desc", nulls="first"))
# nulls still first, then values descending -> Bob, Di, Ann (10), Cy (5)
```

```ts
import { sort } from "@cyblow/paginate";

const rows = [
  { name: "Ann", score: 10 },
  { name: "Bob", score: null },     // null
  { name: "Cy",  score: 5 },
  { name: "Di" },                    // missing field -> null
];

sort(rows, { field: "score" });                       // nulls last (default)
// -> Cy (5), Ann (10), Bob (null), Di (missing)

sort(rows, { field: "score", nulls: "first" });       // nulls first
// -> Bob (null), Di (missing), Cy (5), Ann (10)

sort(rows, { field: "score", direction: "desc", nulls: "first" });
// nulls still first, then values descending -> Bob, Di, Ann (10), Cy (5)
```

Because nulls are placed per key, the next key in the sequence still breaks ties among
the null group, exactly as it does among non-null values.

## Empty sequence

Sorting by an empty sequence of specs is a no-op: the items are returned in their
original order.

```python
from pypaginate import sort

sort(items, [])     # -> items unchanged (original order)
```

```ts
import { sort } from "@cyblow/paginate";

sort(items, []);    // -> items unchanged (original order)
```

## Errors

If any key compares values that are not order-comparable (e.g. a number against a string
on the same field), the whole sort fails fast with a `SortError` — see
[incomparable values](./basic#incomparable-values-raise-sorterror).

## Next

- [Basic sorting](./basic) — the single-key form, stability, and dotted field paths.
