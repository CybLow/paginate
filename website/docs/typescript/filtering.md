---
sidebar_position: 3
title: Filtering
---

# Filtering

`filter(items, where)` returns a new array of the items matching `where`, **in their
original order**. The matching runs in the native engine. For the full operator table
and semantics, see the [shared reference](../general/filtering).

## A single condition

A filter spec is a plain object with a `field`, an `operator` (a plain string), and a
`value`:

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

## A list of conditions

Pass an **array of specs** to combine several conditions. Each spec carries its own
`logic` (`"and"` — the default — or `"or"`): every `and` spec must match, and if any
spec uses `or`, at least one `or` spec must also match. An **empty** array matches
everything.

```ts
// age >= 18 AND name contains "a"
filter(users, [
  { field: "age", operator: "gte", value: 18 },
  { field: "name", operator: "contains", value: "a" },
]);

// active AND (role == "admin" OR role == "owner")
filter(users, [
  { field: "active", operator: "eq", value: true },
  { field: "role", operator: "eq", value: "admin", logic: "or" },
  { field: "role", operator: "eq", value: "owner", logic: "or" },
]);
```

## Nested boolean groups

For clearer nested logic, use the `And()` / `Or()` builders. Each condition is a spec
or another group, so they nest arbitrarily (up to
[5 levels](../general/filtering#nesting-depth-limit)):

```ts
import { filter, And, Or } from "@cyblow/paginate";

const where = And(
  { field: "active", operator: "eq", value: true },
  Or(
    { field: "role", operator: "eq", value: "admin" },
    { field: "role", operator: "eq", value: "owner" },
  ),
);
filter(users, where);
```

## Common operators

```ts
// membership
filter(users, { field: "role", operator: "in", value: ["admin", "owner"] });
// inclusive range
filter(users, { field: "age", operator: "between", value: [18, 65] });
// null check (value optional for nullary operators)
filter(users, { field: "email", operator: "is_not_null" });
// SQL LIKE (% = any run, _ = one char); ilike is case-insensitive
filter(users, { field: "name", operator: "like", value: "A%" });
// regex (≤ 200 chars)
filter(users, { field: "name", operator: "regex", value: "^[AEIOU]" });
```

See the [full operator table](../general/filtering#the-20-operators) for all 20.

## Filtering by indices

`filter` returns items; if you only need the matching **indices** (e.g. to apply them
elsewhere), use the engine helpers `filterIndices` / `filterGroupIndices`:

```ts
import { filterIndices, filterGroupIndices, And } from "@cyblow/paginate";

filterIndices(users, [{ field: "age", operator: "gte", value: 18 }]); // number[]
filterGroupIndices(users, And(/* ... */));
```

## Errors

The same conditions that fail in Python throw here too — an unknown operator, an
unresolved field path, or incomparable operands — each carrying the core's message:

```ts
try {
  filter(users, { field: "age", operator: "nope" as any, value: 1 });
} catch (err) {
  console.error((err as Error).message); // "unknown operator: nope"
}
```

The error classes (`FilterError`, `FilterValidationError`, …) are exported for
`instanceof` checks.

## Next

- [Filtering & operators reference](../general/filtering) — all 20 operators, group depth.
- [Sorting](./sorting) · [Search](./search) · [Pagination](./pagination)
