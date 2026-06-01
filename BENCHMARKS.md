# Benchmarks — is native worth the FFI?

The cursor codec is a clear native win (tiny payload, no per-item marshalling).
The **in-memory engines** are the open question: each item's fields must cross
the FFI boundary, and pypaginate's pure-Python engines are already heavily
optimized (38 rounds). So before wiring them, we measured.

## Method

- 10,000 dict items; median of 50–100 runs.
- **Native timing includes everything**: projecting each item's referenced
  fields → `Value`, the FFI call, and selecting results by returned index.
- **Pure-Python** is the existing optimized engine (`FilterEngine` /
  `SortEngine` / `SearchEngine`).
- Every case asserts the native and pure-Python results are identical.

## Results (10K items, macOS arm64, Python 3.14)

| Engine | scenario | pure-Python | native (+marshalling) | speedup | winner |
|--------|----------|-------------|-----------------------|---------|--------|
| Filter | 1 op (gte)        | 1008 µs | 760 µs  | 1.33× | native (marginal) |
| Filter | 2 ops             | 1426 µs | 1517 µs | 0.94× | **pure-Python** |
| Sort   | 1 key             | 1362 µs | 1717 µs | 0.79× | **pure-Python** |
| Sort   | 2 keys            | 3528 µs | 4053 µs | 0.87× | **pure-Python** |
| Search | 1 field           | 1986 µs | 1433 µs | 1.39× | **native** |
| Search | 1 field (long text)| 4081 µs | 2511 µs | 1.63× | **native** |
| Search | 2 fields          | 8402 µs | 4008 µs | 2.10× | **native** |

## Conclusion

The boundary cost is decided by **compute-per-item vs marshalling-per-item**:

- **Filter / Sort are comparison-bound** — almost no work per item, so the
  marshalling cost cancels (or exceeds) the native speedup. **Keep pure-Python.**
- **Search is compute-bound** — normalize + match + score per field per item —
  so native wins clearly (up to **2.1×** on multi-field). **Worth wiring.**

### Decision (for the Python package, `pypaginate`)

| Path | Native in Python? |
|------|-------------------|
| cursor codec | ✅ yes (already integrated, with fallback) |
| search | ✅ yes — wire it (non-fuzzy first; see caveat) |
| filter, sort | ❌ no — the optimized pure-Python engines win |

> The filter/sort **bindings are still retained** in this repo: a *naive JS*
> engine has no 7-round optimization, so native likely wins there even where it
> doesn't for Python. The benchmark gate is per-language.

### Caveat for wiring search

Native fuzzy currently uses the no-rapidfuzz fallback, so until the `rapidfuzz`
crate is wired (parity with Python's rapidfuzz), route only **non-fuzzy**
search (exact / prefix / contains) to native and keep fuzzy on pure-Python.

## Reproduce

Build + install the wheel, then run the comparison scripts against `paginate_core`
and the `pypaginate` engines (see the commit that added this file).
