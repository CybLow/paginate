---
orphan: true
---

# ADR: A shared Rust core (`paginate-core`)

> **Status:** in progress · **Date:** 2026-06-01

## Context

pypaginate's pure-Python implementation is already heavily optimized (38
optimizations across 7 rounds; #1 in most in-memory benchmarks) and has reached
a local optimum for pure Python. The [optimization audit](OPTIMIZATION_AUDIT.md)
explicitly rejected mypyc/Cython for "build complexity, C extension
distribution issues." A **JS/TS port** is on the roadmap.

A **Rust core** resolves both: native speed *and* one implementation reusable
across runtimes. The same domain crate compiles to a CPython extension (PyO3)
and a Node addon (napi-rs); a Python-only native extension would not be
reusable.

## Decision

A separate, polyglot repository — [`paginate-core`](https://github.com/CybLow/paginate)
(renamed from `pypaginate-core`; it is not Python-only). Canonical layout:

```
paginate-core/
  crates/
    core/        # pure Rust domain engine — NO bindings, NO ORM, NO DB
    py/          # PyO3 adapter  -> Python module `paginate_core`
    node/        # napi-rs adapter -> Node/TS addon
  packages/
    python/      # consumed by pypaginate (SQLAlchemy / FastAPI ...)
    ts/          # future npm package (Prisma / Drizzle / TypeORM ...)
```

**Native-first, not WASM-first.** Use PyO3 for Python and napi-rs for Node/TS —
native addons are simpler and faster at the I/O boundary, and each language's
ORM stays in its own adapter. WASM (`wasm-bindgen`) is kept as an *optional*
future target for browser/edge runtimes only, never the foundation. (The core
still compiles to `wasm32` at no cost, so that door stays open.)

## Ports & adapters — the strict rule

```
ORM            -> language adapter (SQLAlchemy, Prisma, ...)
business rules -> Rust core
serialization  -> adapter
DB transaction -> adapter
```

The Rust core never talks to an ORM, a DB, or HTTP. It receives **plain DTOs**
(a small JSON-like `Value` model) and returns plain results. In pypaginate this
is already the design: the engines take/return plain data, and filter/sort/search
return **indices** so host ORM objects never round-trip through Rust — the
adapter selects from the originals by index.

## Integration (graceful, opt-in)

pypaginate auto-detects the native extension and falls back to pure Python — the
**same pattern** as `msgspec` / `google-re2`. No public API
change, no new required dependency. First integrated module: the cursor codec
([`engine/cursor_codec.py`](../src/pypaginate/engine/cursor_codec.py)):

```python
try:
    from paginate_core import encode_cursor as _native_encode, ...
    _HAS_NATIVE = True
except ImportError:
    _HAS_NATIVE = False
```

Enable native acceleration by installing the wheel (until published):

```bash
maturin build -r -m crates/py/Cargo.toml   # in the paginate-core repo
uv pip install path/to/paginate_core-*.whl
```

## The resident `Dataset` — one call, columnar speed

The headline optimization is a **resident** dataset: marshal rows into the core
**once**, then run filter → sort → paginate natively in a single call. Exposed as
the public `pypaginate.Dataset` (native one-call when available, pure-Python
fallback otherwise — an identical `OffsetPage` either way):

```python
from pypaginate import Dataset, FilterSpec, OffsetParams, SortSpec

ds = Dataset(rows)  # rows marshalled into the core once
page = ds.paginate(
    OffsetParams(page=1, limit=20),
    filters=[FilterSpec(field="age", operator="gte", value=18)],
    sorting=[SortSpec(field="age")],
)  # one native FFI crossing -> OffsetPage
```

Fields that hold the same scalar (`int`/`float`/`str`) in *every* row get a dense
typed column, so the filter and sort stages skip the per-row map lookup and
`Value` dispatch. On 10K rows the one-call pipeline is **~36× faster** than the
pure-Python pipeline (a single int filter ~28×, single-key sort ~9×) — all
**verified identical** to pure-Python (a column is built only when it can't
diverge from the row engine). The same `Dataset` exists for Node/TS; there V8
wins the single ops but the fused `page()` still wins ~6×. See
[BENCHMARKS.md](https://github.com/CybLow/paginate/blob/main/BENCHMARKS.md).
The columnar path also covers multi-key sort and multi-filter `AND`.

## Typed stubs & exceptions

The wheel ships PEP 561 type information (`paginate_core/__init__.pyi` + `py.typed`,
auto-detected by maturin), so consumers and mypy type-check against the native
module directly — pypaginate dropped its `ignore_missing_imports` override. Errors
surface as a typed hierarchy — `PaginateError` (a `ValueError`) with
`FilterError`/`SortError`/`SearchError`/`InvalidCursorError` — and the resident
`Dataset` is a `#[pyclass(frozen)]` with a `__repr__`.

## Verification

* Cursor wire format is **byte-identical** to the Python codec (golden vectors,
  incl. `ensure_ascii` + astral surrogate pairs) and round-trips both ways, so
  existing client cursors stay valid.
* Filter/sort/search outputs cross-checked vs the real Python engines: **22/22**.
* The cursor integration passes the existing suite on **both** paths
  (`tests/unit/adapters/sqlalchemy/test_cursor_codec.py`), ruff + mypy clean.

## Status & next steps

Done: pure core (65 cargo tests + 8 property), `abi3` wheel with PEP 561 stubs,
PyO3 + napi-rs bindings (typed exceptions), cursor codec + ranked search
integrated with fallback, `rapidfuzz` crate parity for fuzzy/token-sort search
(now the only implementation — the pure-Python search island was removed), and
the **resident `Dataset`** — filter/sort/paginate in one call with a columnar
fast path (int/float/str, multi-key sort, multi-filter `AND`) — exposed as the
public `pypaginate.Dataset` (native + pure-Python fallback, identical
`OffsetPage`) and as a Node/TS `Dataset`.

Next: publish the wheel + npm addon → optional grouped-filter / multi-key
columnar in the one-call path.
