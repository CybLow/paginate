# Benchmarks — is native worth the FFI?

The cursor codec is a clear native win (tiny payload, no per-item marshalling).
The **in-memory engines** are the open question: each item's fields must cross
the FFI boundary, and pypaginate's pure-Python engines are already heavily
optimized (38 rounds). So before wiring anything, we measured.

## Method

- 10,000 dict items; median of 50–100 runs.
- **Native timing includes everything**: projecting each item's referenced
  fields → `Value`, the FFI call, and selecting results by returned index.
- **Pure-Python** is the existing optimized engine.
- Every case asserts native and pure-Python results are identical.

## Results (10K items, macOS arm64, Python 3.14)

| Engine | scenario | pure-Python | native (+marshalling) | speedup | winner |
|--------|----------|-------------|-----------------------|---------|--------|
| Filter | 1 op (gte)              | 1008 µs | 760 µs  | 1.33× | native (marginal) |
| Filter | 2 ops                   | 1426 µs | 1517 µs | 0.94× | **pure-Python** |
| Sort   | 1 key                   | 1362 µs | 1717 µs | 0.79× | **pure-Python** |
| Sort   | 2 keys                  | 3528 µs | 4053 µs | 0.87× | **pure-Python** |
| **Search (ranked, `SearchEngine`)** | 1 field            | 1986 µs | 1433 µs | 1.39× | **native** |
| **Search (ranked)** | 1 field (long text) | 4081 µs | 2511 µs | 1.63× | **native** |
| **Search (ranked)** | 2 fields            | 8402 µs | 4008 µs | **2.10×** | **native** |
| Match-filter (`MemorySearchBackend`, the pipeline path) | 1 field | 1235 µs | 2771 µs | 0.45× | **pure-Python** |
| Match-filter (pipeline) | 2 fields            | 4088 µs | 4039 µs | 1.01× | tie |

## Results — JS/Node (naive pure-JS vs native addon, 10K objects)

| Engine | naive pure-JS | native (+napi marshalling) | speedup | winner |
|--------|---------------|----------------------------|---------|--------|
| Filter (2 ops)    |  54 µs | 12,536 µs | 0.004× | **naive JS (~230×)** |
| Sort (1 key)      | 322 µs | 13,396 µs | 0.024× | **naive JS (~42×)** |
| Search (contains) | 154 µs | 12,826 µs | 0.012× | **naive JS (~83×)** |

V8's JIT runs `Array.filter`/`sort` on native objects in microseconds, while the
napi boundary must marshal **whole** 10K objects (JS → serde_json → `Value`),
costing ~12 ms. For JS the in-memory engines lose *catastrophically* — the
opposite of a win.

## Conclusion

The boundary cost is decided by **compute-per-item vs marshalling-per-item**,
and the data is unambiguous in *both* languages:

- **Crossing the FFI to filter/sort an in-memory list is not worth it.** The
  per-item work (accessor + compare) is tiny; marshalling 10K items dominates.
  Optimized Python is roughly even; JIT'd V8 beats native by **40–230×**.
- **Native wins only when marshalling is cheap or the host is slow:** the
  **cursor codec** (a few scalars, no per-item marshalling) and Python's
  **ranked `SearchEngine`** (heavy tokenize/score/rank per item; CPython is
  slower than V8).

> **This corrects an earlier assumption.** Native does *not* "win across the
> board for JS" — measured, the opposite is true: naive JS wins the in-memory
> engines decisively.

### So why a shared Rust core at all?

Its primary value is **cross-language behaviour consistency**, not raw in-memory
speed:

1. **One implementation** of the cursor codec, the 20 filter operators, the
   null-aware sort, and ranked search — Python and JS share *identical
   semantics*, with no drift from reimplementation.
2. **Cursor wire-compatibility** — a cursor minted by the Python service decodes
   byte-for-byte in the JS service and back (verified). This alone justifies the
   core for a polyglot system.
3. **Targeted speed** where it measurably helps: Python cursor + ranked search.

The filter/sort/search **bindings are kept for behaviour parity** (a caller who
needs pypaginate's *exact* semantics can use them), but for raw speed a host
should use its own array operations — and the README/ARCHITECTURE say so plainly.

## Making Rust actually win — the resident `Dataset`

The one-shot bindings re-marshal every item on every call, so the FFI tax is
paid per query. The fix is **marshal once, query many**: `pypaginate.Dataset`
holds the rows as `Value` in Rust, built once, then answers filter/sort/search
queries natively (returning indices) with **no re-marshalling**.

Once resident, Rust's compute advantage shows on **every** engine (10K rows,
per-query steady state):

| engine | pure-Python | native `Dataset` | speedup |
|--------|-------------|------------------|---------|
| filter (`age >= 500`)    | 1050 µs | **97 µs**  | **10.8×** |
| search (`name` contains) | 1457 µs | **712 µs** | **2.0×** |
| sort (`age` asc)         | 1426 µs | **972 µs** | **1.5×** |

Filter gains most (Python pays per-item interpreted predicate calls); sort gains
least (CPython's `list.sort` is C-level timsort, so Rust's `Value` comparison is
only modestly ahead). All three win.

Amortizing the one-time ~6 ms build over N **filter** queries gives a clean
crossover:

| queries | native (build + N) | pure-Python | winner |
|--------:|--------------------|-------------|--------|
| 1   | 6.2 ms  | 1.0 ms   | pure (build not amortized) |
| 10  | 7.2 ms  | 10.1 ms  | **native 1.4×** |
| 50  | 12.0 ms | 50.7 ms  | **native 4.2×** |
| 100 | 17.9 ms | 101.6 ms | **native 5.7×** (→ 10× as N grows) |

**So Rust *is* faster — the trick is not paying the FFI toll on every query.**
Use `Dataset` for a stable in-memory dataset served by many paginated/filtered
requests (an in-memory cache, a config table, a search index); one-shot calls on
data that lives in the host should stay in the host. And a **columnar** fast
path — a dense typed `Vec` for fields that hold the same scalar (`i64`/`f64`/
`String`) in *every* row — now backs the filter **and** sort stages, with
results identical to pure-Python:

| op (10K rows)               | pure-Python | native columnar | speedup |
|-----------------------------|-------------|-----------------|---------|
| filter int (`age >= n`)     | 1022 µs     | 36 µs           | **28×** |
| filter float (`price > x`)  |  527 µs     | 36 µs           | **14.5×** |
| filter str (`name == x`)    |  556 µs     | 20 µs           | **28×** |
| sort int (single key)       | 1068 µs     | 115 µs          | **9.3×** |
| sort int (2 keys)           | 2295 µs     | 297 µs          | **7.7×** |

A column is built only when the field is that exact scalar in every row, so the
typed scan (no map lookup, no `Value` dispatch) can't diverge from the row engine.

### One call, the whole pipeline

Better still, the core runs **filter → sort → paginate in a single call**
(`Dataset.page`), returning the page's indices + offset metadata. The host
passes specs once and maps the returned indices back to its own rows — no
orchestration in the host language. Because the pipeline routes its filter and
sort stages through the columnar path, on 10K rows (int filter + float sort +
page) that one call is **35.7× faster** than the pure-Python pipeline (30 µs vs
1069 µs) — up from 4.7× before columnar — and is a single FFI crossing per
request. This is the "powerful core, thin adapter" shape: the engine lives in
Rust; the host only marshals the dataset once and selects by index.

The columnar path also covers **multi-key sort** (all keys typed) and
**multi-filter `AND`** (every flat spec a typed comparison, intersected) — a
2-filter + 2-key-sort page on 10K rows is **23.7×** the pure-Python pipeline
(83 µs vs 1963 µs). `OR`, nested groups, or any non-columnar spec fall back to
the row engine, so results are always identical.

### The resident Dataset in JS, too

The same `Dataset` exists for Node/TS. JS is the harder case — V8's JIT runs
`Array.filter`/`sort` on native objects in microseconds — so the honest result
is split (10K objects, release addon):

| op | pure-JS | resident `Dataset` | winner |
|----|---------|--------------------|--------|
| filter int (`age >= 50`)        |  76 µs | 275 µs | **pure-JS 3.6×** |
| sort float (`price` desc)       | 283 µs | 416 µs | **pure-JS 1.5×** |
| **pipeline (filter+sort+page)** | 176 µs | **28 µs** | **resident 6.3×** |

Single ops lose: the napi index return + the JS index→row map cost more than the
tiny per-item saving. But the **one-call `page()` wins 6.3× even in JS** — it
fuses filter→sort→slice into a single native columnar pass and returns only the
20-row page, whereas pure-JS must materialize the full filtered array and sort
all of it. So in JS, reach for `Dataset.page` (the fused pipeline), not the
single-op helpers; behaviour parity + the cursor codec remain the cross-language
anchors.

## Update — resident-engine optimization pass (2026-06)

A profiling-led pass made the resident path far faster than the numbers above
(which it supersedes). Every win is bench-gated, keeps the cross-language parity
golden byte-identical, and was found/confirmed with a sampling profiler
(`samply`) rather than guesswork. Rejected along the way — each measured, not
assumed: an FxHash on the postings (below noise), a k-way merge of posting lists
(heap slower than `pdqsort`), and a decorate-subset sort (regressed the full
sort).

### Ranked fuzzy search — ~9× (memoize + bitset)

Fuzzy/trigram search over a resident `Dataset` re-trigrammed the whole corpus on
every query and built candidate sets by concatenate-then-sort. Memoizing the
per-field trigram sets and unioning candidates through a bitset cut it to the
irreducible scoring work:

| resident fuzzy search | 1K | 10K | 100K |
|-----------------------|----|-----|------|
| before | 45 µs | 511 µs | 6.06 ms |
| after  | **6.5 µs** | **63 µs** | **0.68 ms** |

### Columnar filter coverage — strings, ranges, membership

The columnar fast path (a typed dense `Vec` per field) previously handled only
the six comparison operators; everything else fell back to the row engine. It now
also serves the operators below — each removing the per-row accessor walk +
boxed-predicate dispatch, byte-identical to the row engine (100K rows, row →
columnar):

| filter operator | speedup |
|-----------------|---------|
| `contains` / `starts_with` / `ends_with` | ~**4.8×** |
| `between` (single inlined range check)   | ~**27×** |
| `in` / `not_in` (one HashSet vs per-row list scan) | ~**24×** |
| `like` / `ilike`                         | ~1.2× (and keeps a multi-`AND` filter fully columnar) |

### One-call `page()` — top-k, ~3×

The pipeline fully sorted the filtered set then sliced one page. It now pushes the
page window down as a **top-k** (`select_nth` instead of a full sort) over a
comparator **monomorphised per column type** (no per-comparison enum match):

| `Dataset.page` (100K, columnar) | time |
|---------------------------------|------|
| before this pass            | 554 µs |
| + top-k                     | 341 µs |
| + monomorphised comparator  | **183 µs** (3.0×) |

A re-profile confirms convergence: 94% of what remains is two irreducible O(n)
scans (the filter scan + the top-k partition), 6% allocation, no dispatch left.

### Node marshalling — move, don't clone (~1.7×)

The JSON→`Value` bridge cloned every row's strings and object keys. Consuming the
owned JSON and **moving** them cut the one-time build's marshalling ~1.7×
(1527 → 889 µs per 10K objects). PyO3 is unaffected (it marshals `PyAny`
directly).

### Where the time now goes — and why we stopped

Measured 100K resident-`Dataset` lifecycle:

| phase | cost | when paid |
|-------|------|-----------|
| marshalling (node) | ~9 ms | build (once) |
| `Columns::build` | 9.3 ms | build (once) |
| `TrigramIndex::build` | 27.6 ms | build (once) |
| `page` query | 0.18 ms | per query |
| `search` query | 0.06 ms | per query |

The per-query path is at its floor (Amdahl ceiling ~1.06×) and is well under 1%
of a typical `Dataset`'s lifetime cost — `build ≈ 46 ms` dominates until roughly
**N ≈ 255 queries**. The only sizeable remaining cost is the one-time index build
(`TrigramIndex::build`, 60% of it), but profiling shows it is bound by posting-list
**allocation**, not hashing: a faster `u64` hasher for the trigram keys was tried
and *regressed* it ~11% in a same-session A/B (28 → 31 ms). The trigram alphabet
is tiny — few distinct keys, huge posting lists — so a weaker hash only collides
more, and the real cost is the `Vec<u32>` growth that no hash change touches. That
lever is spent; the build is near its floor too. The engine is **converged** for
the intended use.

### Decision & status (Python package)

| Path | Native in Python? | Status |
|------|-------------------|--------|
| cursor codec | ✅ yes | integrated, both-path verified |
| ranked `SearchEngine` | ✅ yes (gated) | integrated — non-fuzzy, unweighted, ≥1000 items; pure-Python fallback; native==pure verified |
| resident `pypaginate.Dataset` (filter+sort+paginate) | ✅ yes (opt-in) | **new public API** — native one-call (columnar), pure-Python fallback, identical `OffsetPage` verified |
| `MemorySearchBackend` (pipeline search) | ❌ no | pure-Python (native loses) |
| one-shot filter, sort | ❌ no | pure-Python (marshalling-bound) |

### Caveat

The native search gate excludes **fuzzy** (native fuzzy is a fallback until the
`rapidfuzz` crate is wired) and **weighted** search, and applies only at
≥1000 items (FFI overhead floor) — so the native path is only ever taken where
it both wins and is byte-for-byte equivalent to pure-Python.
