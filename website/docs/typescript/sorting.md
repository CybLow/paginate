---
sidebar_position: 4
title: Sorting
---

# Sorting

`sort(items, by)` returns a new array of your items in the requested order. The input
is never mutated, and items are never copied through the core (the engine returns
indices and the package selects your objects). For the full semantics — stability, null
placement, comparability — see the [shared reference](../general/sorting).

## Sort by one key

A sort spec has a `field`, an optional `direction` (`"asc"` default / `"desc"`), and an
optional `nulls` (`"last"` default / `"first"`):

```ts
import { sort } from "@cyblow/paginate";

const users = [
  { name: "Bob", age: 30 },
  { name: "Alice", age: 25 },
  { name: "Carol", age: 42 },
];

sort(users, { field: "age" });                    // ascending (default)
// -> Alice (25), Bob (30), Carol (42)

sort(users, { field: "age", direction: "desc" }); // descending
// -> Carol (42), Bob (30), Alice (25)
```

The sort is **stable**: items equal on the key keep their original relative order.

## Multi-key sorting

Pass an **array of specs** to sort by several keys in priority order — the first is
primary, each later key only breaks ties left by the ones before it. Mix directions
freely:

```ts
const ordered = sort(employees, [
  { field: "dept" },                       // primary: dept asc
  { field: "salary", direction: "desc" },  // tie-break: salary desc
]);
```

Sorting by an empty array (`sort(items, [])`) is a no-op.

## Null placement

A missing field or an explicit `null` is treated as null. Each key places its nulls
with `nulls`, **independently of `direction`**:

```ts
const rows = [
  { name: "Ann", score: 10 },
  { name: "Bob", score: null },   // null
  { name: "Cy",  score: 5 },
  { name: "Di" },                  // missing -> null
];

sort(rows, { field: "score" });                  // nulls last (default)
// -> Cy (5), Ann (10), Bob (null), Di (missing)

sort(rows, { field: "score", nulls: "first" });  // nulls first
// -> Bob (null), Di (missing), Cy (5), Ann (10)
```

## Dotted field paths

```ts
sort(orders, { field: "customer.name" });
```

## Errors

If a key compares values that aren't order-comparable (e.g. a number against a string
on the same field), the sort throws **`SortError`**:

```ts
import { sort, SortError } from "@cyblow/paginate";

const mixed = [{ v: 1 }, { v: "two" }];
try {
  sort(mixed, { field: "v" });
} catch (err) {
  if (err instanceof SortError) console.log("cannot sort:", err.message);
}
```

## Next

- [Sorting semantics reference](../general/sorting) — stability, nulls, comparability.
- [Filtering](./filtering) · [Search](./search) · [Pagination](./pagination)
