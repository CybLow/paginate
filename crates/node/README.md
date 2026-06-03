# paginate-node

napi-rs (Node-API) adapter that exposes the pure-Rust [`paginate-core`](../core)
engine to Node.js / TypeScript. It mirrors the [PyO3 adapter](../py) surface so
both runtimes share one engine and one set of behaviours (the cursor wire format
is byte-identical across Python, Node, and the core itself).

## What it exposes

Rust function names are exported to JavaScript as camelCase (napi-rs convention):

| JS export | Signature | Description |
|-----------|-----------|-------------|
| `normalizeText` | `(value: string) => string` | NFKD accent-stripping text normalization. |
| `offset` | `(page: number, limit: number) => number` | Zero-based row offset. |
| `maxPages` | `(total: number, limit: number) => number` | Total page count (ceil). |
| `clampPage` | `(page, limit, total) => number` | Clamp page into `[1, maxPage]`. |
| `offsetMeta` | `(page, limit, total) => OffsetMeta` | `{ page, pages, hasNext, hasPrevious }`. |
| `encodeCursor` | `(values: unknown) => string` | Encode ordering values into a URL-safe cursor. |
| `decodeCursor` | `(cursor: string) => unknown[]` | Decode a cursor back into its ordering values. |
| `filterIndices` | `(items, specs) => number[]` | Indices matching flat filter specs `[{field,op,value,logic?}]`. |
| `sortIndices` | `(items, specs) => number[]` | Index permutation for sort specs `[{field,direction?,nulls?}]`. |
| `searchIndices` | `(items, query, fields, …) => number[]` | Ranked search indices over `fields`. |

### Cursor values

Ordering values cross the boundary as plain JSON (`serde_json::Value`):
`null` / `bool` / `number` (integral -> Int, otherwise Float) / `string` /
`array` / `object`. JavaScript has no native datetime / Decimal / UUID types, so
the typed-scalar variants the Python codec round-trips are not minted here —
pass their ISO/canonical strings instead. Cursors remain interoperable: a cursor
produced by Python or the Rust core decodes here and vice versa.

### Performance — prefer native Array methods for in-memory work

`filterIndices` / `sortIndices` / `searchIndices` exist for **behaviour parity**
with pypaginate's exact semantics — **not** for speed. Marshalling a large array
across the napi boundary costs far more than the per-item work, so V8's
`Array.filter` / `Array.sort` are **40–230× faster** (see
[../../BENCHMARKS.md](../../BENCHMARKS.md)). Reach for the native engines only
when you need pypaginate's precise operator / ranking behaviour; otherwise use
plain JS. The **cursor codec** and `normalizeText` are the consistency-critical
paths genuinely worth crossing the boundary for.

## Building

This crate compiles to a Node-API addon (`crate-type = ["cdylib"]`). The native
addon plus its generated `index.js` / `index.d.ts` glue are produced by
[`@napi-rs/cli`](https://www.npmjs.com/package/@napi-rs/cli):

```bash
npm install        # installs @napi-rs/cli
npm run build      # napi build --platform --release  -> *.node + index.{js,d.ts}
```

`build.rs` calls `napi_build::setup()` so the linker is configured for the host
Node-API toolchain.

A plain `cargo build -p paginate-node` / `cargo check -p paginate-node` compiles
the Rust object too, but only `@napi-rs/cli` emits the loadable addon and TS
type definitions.

## Status

Builds and is validated from Node — cursor wire-identical to Python/core, and
filter/sort/search return correct results. The generated artifacts (`index.js`,
`index.d.ts`, `*.node`) are build outputs and are not checked in. Consumed by
the `packages/ts` TypeScript package.
