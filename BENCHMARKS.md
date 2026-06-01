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

## Conclusion

The boundary cost is decided by **compute-per-item vs marshalling-per-item**:

- **Compute-heavy → native wins.** Ranked search (`SearchEngine`) tokenizes,
  scores, and ranks per field per item — native wins up to **2.1×**.
- **Lightweight → marshalling dominates, native loses or ties.** Filter, sort,
  and the pipeline's *match-filter* search are little more than an accessor +
  compare/substring per item; projecting 10K items to `Value` costs more than
  it saves. (Single-field match-filter is 2.2× *slower* native.)

So in **Python**, native helps exactly two paths: the **cursor codec** and the
**ranked `SearchEngine`**. Everything else stays pure-Python.

> **The bigger picture:** native barely moves pypaginate's already-optimized
> Python in-memory engines — the Rust core's primary value is the **polyglot
> story** (a *naive* JS/TS engine has no 7-round optimization, so native will
> win there across the board) plus the cursor codec. The bindings for filter /
> sort / match-filter are retained for exactly that reason.

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
