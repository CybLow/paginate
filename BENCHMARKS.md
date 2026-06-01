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
paid per query. The fix is **marshal once, query many**: `paginate_core.Dataset`
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
data that lives in the host should stay in the host. A *columnar* `Dataset`
(typed per-field arrays instead of `Value` maps) is the next lever for an even
larger per-query win.

### Decision & status (Python package)

| Path | Native in Python? | Status |
|------|-------------------|--------|
| cursor codec | ✅ yes | integrated, both-path verified |
| ranked `SearchEngine` | ✅ yes (gated) | integrated — non-fuzzy, unweighted, ≥1000 items; pure-Python fallback; native==pure verified |
| `MemorySearchBackend` (pipeline search) | ❌ no | pure-Python (native loses) |
| filter, sort | ❌ no | pure-Python (marshalling-bound) |

### Caveat

The native search gate excludes **fuzzy** (native fuzzy is a fallback until the
`rapidfuzz` crate is wired) and **weighted** search, and applies only at
≥1000 items (FFI overhead floor) — so the native path is only ever taken where
it both wins and is byte-for-byte equivalent to pure-Python.
