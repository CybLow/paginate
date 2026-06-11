---
sidebar_position: 8
title: Sorting semantics
---

# Sorting semantics

Sorting is described by one or more **`SortSpec`** keys evaluated by the Rust core, so
the order is identical in every language. This page is the canonical reference; for
runnable code see the [Python](../python/sorting) and [TypeScript](../typescript/sorting)
sorting guides.

## The `SortSpec`

| Field | Type | Default | Meaning |
|---|---|---|---|
| `field` | string | — (required) | Dotted field path to sort by, e.g. `age` or `address.city`. |
| `direction` | `"asc"` \| `"desc"` | `"asc"` | Ascending or descending order. |
| `nulls` | `"first"` \| `"last"` | `"last"` | Where missing / null values go. |

In Python a `SortSpec` is a dataclass; in TypeScript a plain object — same field names,
same plain-string values.

## Stability

The sort is **stable**: items that compare equal on the sort key keep their original
relative order. Stability is what makes layering keys predictable, and it is the basis
for multi-key sorting.

## Multi-key (priority) ordering

Pass a **sequence of `SortSpec`** to sort by several keys at once. The keys apply in
**priority order** — the first spec is the primary sort, and each later spec only
breaks ties left by the ones before it. Any rows still tied after the last key keep
their original order (because the sort is stable).

Each key carries its **own** `direction` and `nulls`, so you can freely mix ascending
and descending keys in one order — e.g. *department ascending, then salary descending*.

An **empty** sequence of specs is a no-op: items are returned in their original order.

## Null placement

A value is treated as **null** when the field is missing on an item or is explicitly
`null` / `None`. Each key decides where its nulls go:

| `nulls` | Effect |
|---|---|
| `"last"` (default) | Null values sort **after** all non-null values. |
| `"first"` | Null values sort **before** all non-null values. |

Null placement is **independent of `direction`** — `nulls="first"` puts nulls first
whether the key is ascending or descending. Because nulls are placed per key, the next
key in the sequence still breaks ties among the null group, exactly as among non-null
values.

## Comparability

The core compares values the way Python does: numbers order against numbers and text
against text, but a number cannot be ordered against a string. When a field holds a mix
of those kinds across items, the sort **fails fast** with a sort error rather than
producing an arbitrary order.

## Next

- [Python sorting](../python/sorting) · [TypeScript sorting](../typescript/sorting)
- [Filtering & operators](./filtering) · [Search & ranking](./search)
