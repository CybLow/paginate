# paginate-core — Architecture

This repository is the **language-agnostic engine** behind
[pypaginate](https://github.com/CybLow/pypaginate). It exists so the
computational heart of the library lives once, in Rust, and is shared by every
host language through a thin **native adapter** — Python today, Node/TS next.

## Why this exists

pypaginate's pure-Python implementation is already heavily optimized (38
optimizations across 7 rounds; #1 in most in-memory benchmarks). It has reached
a local optimum for pure Python — the next step-change requires native code.
The audit explicitly **rejected mypyc/Cython** for "build complexity, C
extension distribution issues."

A **Rust core** changes that calculus: it captures the native speed *and* is
reusable across runtimes. A Python-only native extension would not be — but the
same Rust crate drives a CPython extension (PyO3) and a Node/TS addon
(napi-rs) without reimplementing a line of engine logic. One core, many
adapters; behaviour can never drift between languages.

## Native-first

The boundary between a host runtime and the core is native by design:

- **Python →** [PyO3](https://pyo3.rs) + [maturin](https://www.maturin.rs).
- **Node/TS →** [napi-rs](https://napi.rs).

Native addons are the *simplest* and *fastest* option at the I/O boundary: no
serialization tax across an interpreter sandbox, direct access to host objects,
and one core linked straight into the runtime. They are the foundation.

**WASM is an optional, future-only target.** [wasm-bindgen](https://github.com/rustwasm/wasm-bindgen)
exists for **browser / edge** runtimes where a native addon cannot be loaded —
never as the foundation for Python or Node. The core has zero binding
dependencies and already compiles to `wasm32-unknown-unknown` at no extra cost,
so that door stays open if and when a browser/edge consumer needs it.

## The founding decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Boundary** | Native-first | PyO3 for Python, napi-rs for Node/TS — native addons are simpler and faster at the I/O boundary than WASM. |
| **WASM** | Optional future target | wasm-bindgen for browser/edge **only**; the core compiles to `wasm32` at no cost so the door stays open. |
| **First scope** | All pure-compute | Port the whole compute surface (cursor, pagination, normalize, filter, sort, search) rather than spike one module. |
| **Repo layout** | Separate repo | The core is its own crate; adapters and consumers depend on it. Keeps the polyglot core decoupled from any one language package. |

### Decision table — what to build with what

| Target | Tool | Output |
|--------|------|--------|
| Domain engine | **Pure Rust** | `paginate-core` crate (no bindings/ORM/DB) |
| Python module | **PyO3 + maturin** | `paginate_core` extension module |
| Node/TS addon | **napi-rs** | native `.node` addon |
| Browser / edge | **WASM + wasm-bindgen** *(optional)* | `wasm32` module |

## Layout

```
paginate-core/
├── Cargo.toml                       # workspace
├── rust-toolchain.toml              # stable + clippy/rustfmt (wasm32 optional)
├── crates/
│   ├── core/                        # PURE engine — NO bindings/ORM/DB/HTTP
│   │   └── src/
│   │       ├── value.rs             # Value: the JSON-like FFI data model
│   │       ├── error.rs             # CoreError
│   │       ├── accessor.rs          # dotted-path resolve (shared)
│   │       ├── coerce.rs            # Python-semantics compare/eq/str(x)
│   │       ├── cursor.rs            # keyset cursor codec (wire-compatible)
│   │       ├── pagination.rs        # offset / pages / has_next math
│   │       ├── normalize.rs         # text normalization
│   │       ├── filter/              # 20 operators, groups, like, regex
│   │       ├── sort.rs              # stable multi-key sort, null placement
│   │       └── search/              # tokenizer + matching + ranking
│   ├── py/                          # PyO3 adapter -> `paginate_core` module
│   │   └── src/{lib.rs, conv.rs}
│   └── node/                        # napi-rs adapter -> Node/TS .node addon  (planned)
│       └── src/lib.rs
└── packages/
    ├── python/                      # consumed by the pypaginate package + its
    │                                #   ORMs (e.g. SQLAlchemy)               (planned)
    └── ts/                          # future npm package + its ORMs
                                     #   (e.g. Prisma / Drizzle / TypeORM)    (planned)
```

`crates/core` and `crates/py` exist today. `crates/node` and `packages/` are
the agreed target shape; the core engine is complete and the adapters layer on
top of it without engine changes.

## Ports & adapters — the strict boundary rule

The core is the **domain engine**: it has no knowledge of ORMs, databases,
HTTP, or any host runtime. Responsibilities split cleanly:

| Concern | Owner |
|---------|-------|
| ORM (SQLAlchemy / Prisma / Drizzle / TypeORM) | **language adapter** |
| Business rules (cursor, pagination, filter, sort, search) | **Rust core** |
| Serialization / object ↔ `Value` mapping | **adapter** |
| DB transaction / session lifecycle | **adapter** |

The core only ever sees plain DTOs — the `Value` model — and **never** talks to
an ORM, a database, or the network. Each adapter (`crates/py`, `crates/node`)
maps host objects to/from `Value` and hands the core nothing else.

## The boundary: `Value`

The core speaks only [`Value`](crates/core/src/value.rs) — a small enum:
`Null | Bool | Int | Float | Str | Bytes | List | Map`, plus typed scalars
`DateTime | Date | Decimal | Uuid` that carry their canonical string so cursors
round-trip with full fidelity. Nothing host-specific crosses the boundary; the
adapter layer converts host objects to/from `Value`.

### Marshalling strategy (the cost the boundary must respect)

The cursor codec and pagination math are **small-payload** — marshalling is
negligible. The in-memory engines are **large-payload** (every item), so:

- **Index-based returns.** `filter`, `sort`, and `search` return *indices* (a
  `Vec<usize>` / permutation), never cloned items. The adapter selects from the
  original host objects by index — host objects never round-trip through Rust,
  so an ORM model never crosses the FFI boundary as data.
- **Projected extraction (planned for the engine adapters).** Only the fields a
  spec references are extracted per item, not the whole record.

## Behaviour parity — how we know the port is correct

Each module mirrors the semantics of its Python counterpart, verified three ways:

1. **In-language unit tests** — 50 `cargo test` cases covering each module.
2. **Cross-language golden vectors** — the cursor wire format is asserted
   byte-identical to output generated by the *real* Python codec
   (`cursor::tests::golden_vectors_match_python_codec`), including non-ASCII
   (`ensure_ascii`) and astral surrogate pairs.
3. **Cross-language behavioural checks** — filter/sort/search outputs were
   compared against the real Python `FilterEngine`/`SortEngine`/`SearchEngine`
   on shared fixtures: **22/22 cases matched** (9 filter, 13 sort/search).

The cursor codec is also wire-compatible **in both directions**: a cursor
minted by Python decodes here and vice-versa, so switching implementations
never invalidates a client's existing cursors.

## Status

| Module | Core | Verified vs Python |
|--------|------|--------------------|
| `cursor` | ✅ | ✅ byte-identical (11 golden vectors) |
| `pagination` | ✅ | ✅ formula parity |
| `normalize` | ✅ | ✅ ASCII + accented Latin (casefold edges documented) |
| `coerce` | ✅ | ✅ used by filter/sort cross-checks |
| `filter` (20 ops, groups) | ✅ | ✅ 9/9 cases |
| `sort` (multi-key, nulls) | ✅ | ✅ 13/13 cases (with search) |
| `search` (rank, weights) | ✅ | ✅ (fuzzy uses fallback; rapidfuzz parity tracked) |
| **PyO3 adapter** (`crates/py`) | cursor, normalize, pagination ✅ | filter/sort/search bindings: planned |
| **napi-rs adapter** (`crates/node`) | planned | — |

## JS/TS adapter (native-first)

The Node/TS adapter is a **napi-rs** crate (`crates/node`) that wraps the *same*
core — no engine reimplementation, the same index-based returns and `Value`
boundary as the Python adapter. It produces a native `.node` addon consumed by
the future `packages/ts` npm package and its ORM integrations (Prisma, Drizzle,
TypeORM).

**WASM stays optional.** Because `crates/core` carries zero binding
dependencies and already builds for `wasm32-unknown-unknown` (CI runs this as a
portability check, not a release artifact), a `crates/wasm` (wasm-bindgen)
adapter can be added later for browser/edge runtimes without touching the core.
It is a future option, never the foundation.

## Known follow-ups

- Filter/sort/search PyO3 bindings (projected extraction over host items).
- napi-rs adapter (`crates/node`) + the `packages/ts` npm package.
- Wire the `rapidfuzz` Rust crate for fuzzy score parity with Python's rapidfuzz.
- Publish the `paginate-core` Python module so `pip install paginate-core`
  enables native acceleration for the `pypaginate` package.

## Develop

```bash
cargo test --workspace                      # unit + golden-vector tests
cargo clippy --workspace --all-targets -- -D warnings
maturin build -r -m crates/py/Cargo.toml    # Python module (paginate_core)

# Node/TS adapter (planned crate):
napi build --release --cargo-cwd crates/node

# Optional browser/edge portability check (not a release target):
cargo build -p paginate-core --target wasm32-unknown-unknown
```
