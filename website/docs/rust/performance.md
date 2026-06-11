---
sidebar_position: 4
title: Performance
---

# Performance

A shared native core is an obvious win for the cursor codec, but the **in-memory
engines** are the real question: every item's fields must cross the FFI boundary, and a
JIT'd host (CPython, V8) is no slouch. So the project **measured** rather than assumed —
and the honest answer shapes how you should use the packages.

:::note
Figures below are representative (≈10K–100K rows, release builds); absolute numbers vary
by machine and runtime. The *shape* of the result is what matters.
:::

## The boundary cost decides everything

The trade-off is **compute-per-item vs. marshalling-per-item**:

- **Small-payload work wins natively.** The cursor codec and pagination math move a
  handful of scalars — marshalling is negligible, so Rust is the clear home.
- **One-shot, large-payload work often does *not* win.** Marshalling 10K items to call
  `filter`/`sort` once can dwarf the tiny per-item compare. In Python the optimized
  pure-Python engine is roughly even; in JS, V8's `Array.filter`/`sort` on native
  objects beats a single native call by **40–230×**, because the napi boundary must
  marshal whole objects.

So the one-shot `filter` / `sort` / `search` helpers exist for **behaviour parity** —
a caller who needs the *exact* shared semantics — not as a raw-speed play over data your
host already holds.

## Where native wins: the resident `Dataset`

The fix is **marshal once, query many**. A [`Dataset`](../python/pagination#the-resident-dataset)
holds the rows as `Value` in Rust, built once, then answers queries natively with no
re-marshalling. Once resident, Rust's compute advantage shows on every engine — and the
typed **columnar** path makes it dramatic:

| Operation (10K rows, resident) | vs. pure host |
|---|---|
| filter `age >= n` (int column) | ~**10–28×** |
| filter `between` / `in` (columnar) | ~**24–27×** |
| sort (single / multi-key, typed) | ~**8–9×** |
| ranked search (memoized trigram) | ~**2–9×** |

The standout is the **fused one-call `page()`** — filter → sort → paginate in a single
columnar pass that returns only the page's indices. On 10K rows that's roughly **35×**
the pure-Python pipeline, and even in **JS** — where single ops lose — the fused
`page()` wins (~**6×**), because it avoids materializing and fully sorting the whole
filtered array.

Amortizing the one-time build over `N` filter queries gives a clean crossover: native
pulls ahead after a handful of queries and grows from there.

## Guidance

| You're doing… | Use… |
|---|---|
| Cursor encode/decode, keyset pagination | the native codec — always a win |
| A **stable** in-memory dataset served by many paginated requests | a `Dataset` (`page()` especially) |
| One-shot filter/sort/search on data the host already holds | the helpers for parity; the host's own array ops for raw speed |
| Ranked / fuzzy search in Python | native (CPython is slower than the Rust ranker) |

Concretely: reach for `Dataset.page` for hot in-memory paths (an in-memory cache, a
config table, a search index); keep one-shot calls for convenience and parity.

## Why a shared core at all, then?

Its primary value is **cross-language behaviour consistency**, not raw single-op speed:

1. **One implementation** of the cursor codec, the 20 operators, the null-aware sort,
   and ranked search — identical semantics, no drift.
2. **Cursor wire-compatibility** — a cursor minted by a Python service decodes
   byte-for-byte in a TypeScript one and back. This alone justifies the core for a
   polyglot system.
3. **Targeted speed** where it measurably helps — the resident `Dataset` pipeline and
   the cursor codec.

For the full methodology and raw numbers, see
[`docs/BENCHMARKS.md`](https://github.com/CybLow/paginate/blob/main/docs/BENCHMARKS.md)
in the repository.
