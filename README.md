<div align="center">

# paginate

**Fast pagination, filtering, sorting & search — one Rust core, native Python & TypeScript packages, byte-for-byte parity.**

[![CI](https://github.com/CybLow/paginate/actions/workflows/ci.yml/badge.svg)](https://github.com/CybLow/paginate/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-cyblow.github.io%2Fpaginate-4f46e5)](https://cyblow.github.io/paginate/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[![PyPI](https://img.shields.io/pypi/v/pypaginate?label=pypi%20pypaginate)](https://pypi.org/project/pypaginate/)
[![npm](https://img.shields.io/npm/v/%40cyblow%2Fpaginate?label=npm%20%40cyblow%2Fpaginate)](https://www.npmjs.com/package/@cyblow/paginate)
[![crates.io](https://img.shields.io/crates/v/paginate-core?label=crates.io%20paginate-core)](https://crates.io/crates/paginate-core)

📖 **[Documentation](https://cyblow.github.io/paginate/)** ·
🐍 **[Python](https://cyblow.github.io/paginate/python/installation)** ·
🟦 **[TypeScript](https://cyblow.github.io/paginate/typescript/installation)** ·
🦀 **[Rust](https://cyblow.github.io/paginate/rust/overview)**

</div>

---

`paginate` implements pagination, filtering, sorting, and search **once**, in a Rust
core, and exposes it through thin native packages for each language. The headline
guarantee is **cross-language parity**: the Python and TypeScript packages return the
same filtered / sorted / ranked order and **byte-identical cursors**, so a cursor minted
by a Python service decodes byte-for-byte in a TypeScript client.

## Packages

| Language | Package | Install | Source |
|---|---|---|---|
| Python | [`pypaginate`](https://pypi.org/project/pypaginate/) | `pip install pypaginate` | [`py/`](py/) |
| TypeScript / Node | [`@cyblow/paginate`](https://www.npmjs.com/package/@cyblow/paginate) | `npm i @cyblow/paginate` | [`ts/`](ts/) |
| Rust | [`paginate-core`](https://crates.io/crates/paginate-core) | `cargo add paginate-core` | [`crates/core/`](crates/core/) |

The Python wheel and the npm package **bundle the native engine** (PyO3 / napi-rs prebuilt
binaries) — there is no Rust toolchain to install.

## Quick look

<table>
<tr><th>Python</th><th>TypeScript</th></tr>
<tr><td>

```python
from pypaginate import (
    paginate, filter, OffsetParams, FilterSpec,
)

page = paginate(users, OffsetParams(page=1, limit=20))
page.total      # 1000
page.has_next   # True

adults = filter(
    users,
    FilterSpec(field="age", operator="gte", value=18),
)
```

</td><td>

```ts
import { paginate, filter, OffsetParams } from "@cyblow/paginate";

const page = paginate(users, new OffsetParams({ page: 1, limit: 20 }));
page.total;     // 1000
page.hasNext;   // true

const adults = filter(users, {
  field: "age",
  operator: "gte",
  value: 18,
});
```

</td></tr>
</table>

## Features

- **One Rust core** — filtering (20 operators + nested `And`/`Or`), stable null-aware
  multi-key sorting, ranked + trigram-fuzzy search, the cursor codec, and pagination
  math all live once in [`paginate-core`](crates/core/).
- **Cross-language parity** — a frozen golden fixture is asserted by the Rust, Python,
  and TypeScript suites in CI; cursors are byte-identical across languages.
- **Two pagination models** — offset (page/limit) and keyset (cursor), with the cursor a
  typed, portable wire format.
- **Framework integrations** — SQLAlchemy, Django, FastAPI (Python); Express, Prisma,
  Drizzle (TypeScript).
- **Typed & dependency-light** — spec/param/page shapes are generated from one JSON
  Schema, so the languages can't drift; the core has zero runtime dependencies.

See the [docs](https://cyblow.github.io/paginate/) for guides and the API reference, and
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) / [`docs/BENCHMARKS.md`](docs/BENCHMARKS.md)
for the design and measured performance.

## Repository layout

```text
crates/
  core/     # paginate-core — the pure Rust engine (no bindings/ORM/DB)
  pyo3/     # PyO3 binding  -> the pypaginate._core extension module
  node/     # napi-rs binding -> the @cyblow/paginate-core native addon
py/         # pypaginate — the Python package (+ SQLAlchemy/Django/FastAPI adapters)
ts/         # @cyblow/paginate — the TypeScript package (+ Express/Prisma/Drizzle)
website/    # the Docusaurus documentation site
docs/       # ARCHITECTURE.md, BENCHMARKS.md
schemas/    # the cross-language JSON Schema (source of the generated types)
```

## Development

```bash
# Rust core + napi addon
cargo test --workspace
cargo clippy --workspace --all-targets -- -D warnings

# Python package (builds the native core via maturin)
cd py && uv sync && uv run pytest

# TypeScript package (builds the native addon, then tests)
cd ts && bun install && bun run test

# Documentation site
cd website && bun install && bun run build
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow and conventions.

## License

[MIT](LICENSE) © CybLow
