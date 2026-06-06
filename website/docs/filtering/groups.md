---
sidebar_position: 3
title: Boolean groups
---

# Boolean groups

For anything beyond a flat list, build a **nested boolean tree** with the `And()`
and `Or()` builders. `And(...)` matches when **all** of its conditions match;
`Or(...)` matches when **any** of them match. Each condition is either a
[`FilterSpec`](./basic) or another group, so they nest arbitrarily.

The builders are identical across languages, and the resulting tree is evaluated by
the same Rust core — Python and TypeScript return identical results
([parity](/concepts/parity)).

## Nesting `And` / `Or`

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
result = filter(users, where)
```

```ts
import { filter, And, Or } from "@cyblow/paginate";

// active AND (role == "admin" OR role == "owner")
const where = And(
  { field: "active", operator: "eq", value: true },
  Or(
    { field: "role", operator: "eq", value: "admin" },
    { field: "role", operator: "eq", value: "owner" },
  ),
);
const result = filter(users, where);
```

A group built by `And()` / `Or()` is passed straight to `filter()` just like a
single spec or a flat list.

## Nesting depth limit

Groups may nest **at most 5 levels deep**. Depth is measured as `1 + the deepest
nested group` — a group whose children are all leaf specs is depth 1. The limit is
defined once in the core (`MAX_FILTER_DEPTH = 5`).

The depth is checked **at construction time**, the moment you call `And()` / `Or()`.
Exceeding it raises **`FilterValidationError`** (a subclass of `FilterError`) in
both languages, before you ever call `filter()`:

```python
from pypaginate import And, FilterSpec, FilterValidationError

leaf = FilterSpec(field="age", operator="gte", value=18)

try:
    # 6 nested groups -> depth 6 -> rejected
    And(And(And(And(And(And(leaf))))))
except FilterValidationError as exc:
    print(exc)  # "FilterGroup nesting must not exceed 5 levels"
```

```ts
import { And, FilterValidationError } from "@cyblow/paginate";

const leaf = { field: "age", operator: "gte" as const, value: 18 };

try {
  // 6 nested groups -> depth 6 -> rejected
  And(And(And(And(And(And(leaf))))));
} catch (err) {
  if (err instanceof FilterValidationError) {
    console.error(err.message); // "FilterGroup nesting must not exceed 5 levels"
  }
}
```

Five levels of nesting is plenty for real query trees; the cap is a guard against
pathological, deeply recursive inputs.

## Next

- [Basic filtering](./basic) — single specs and flat lists.
- [Operators](./operators) — the full table of 20 operators.
