---
sidebar_position: 4
title: Sorting
---

# Sorting

`sort(items, by)` returns a new list of your items in the requested order. The input is
never mutated, and items are never copied through the core (the engine returns indices
and the package selects your objects). For the full semantics — stability, null
placement, comparability — see the [shared reference](../general/sorting).

## Sort by one key

A `SortSpec` has a `field`, an optional `direction` (`"asc"` default / `"desc"`), and
an optional `nulls` (`"last"` default / `"first"`):

```python
from pypaginate import sort, SortSpec

users = [
    {"name": "Bob", "age": 30},
    {"name": "Alice", "age": 25},
    {"name": "Carol", "age": 42},
]

sort(users, SortSpec(field="age"))                      # ascending (default)
# -> Alice (25), Bob (30), Carol (42)

sort(users, SortSpec(field="age", direction="desc"))    # descending
# -> Carol (42), Bob (30), Alice (25)
```

The sort is **stable**: items equal on the key keep their original relative order.

## Multi-key sorting

Pass a **sequence of `SortSpec`** to sort by several keys in priority order — the first
is primary, each later key only breaks ties left by the ones before it. Mix directions
freely:

```python
ordered = sort(employees, [
    SortSpec(field="dept"),                       # primary: dept asc
    SortSpec(field="salary", direction="desc"),   # tie-break: salary desc
])
```

Sorting by an empty sequence (`sort(items, [])`) is a no-op.

## Null placement

A missing field or an explicit `None` is treated as null. Each key places its nulls
with `nulls`, **independently of `direction`**:

```python
rows = [
    {"name": "Ann", "score": 10},
    {"name": "Bob", "score": None},   # null
    {"name": "Cy",  "score": 5},
    {"name": "Di"},                    # missing -> null
]

sort(rows, SortSpec(field="score"))                    # nulls last (default)
# -> Cy (5), Ann (10), Bob (None), Di (missing)

sort(rows, SortSpec(field="score", nulls="first"))     # nulls first
# -> Bob (None), Di (missing), Cy (5), Ann (10)
```

## Dotted field paths

```python
sort(orders, SortSpec(field="customer.name"))
```

## Errors

If a key compares values that aren't order-comparable (e.g. a number against a string
on the same field), the sort fails fast with **`SortError`**:

```python
from pypaginate import sort, SortSpec, SortError

mixed = [{"v": 1}, {"v": "two"}]
try:
    sort(mixed, SortSpec(field="v"))
except SortError as exc:
    print("cannot sort:", exc)   # "field values are not order-comparable"
```

## Next

- [Sorting semantics reference](../general/sorting) — stability, nulls, comparability.
- [Filtering](./filtering) · [Search](./search) · [Pagination](./pagination)
