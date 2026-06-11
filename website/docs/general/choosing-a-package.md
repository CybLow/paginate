---
sidebar_position: 2
title: Choosing a package
---

# Choosing a package

All three packages wrap the **same** Rust core, so they share semantics and the
cursor wire format. Pick by the language you build in.

| You are building in… | Install | Package | Guide |
|---|---|---|---|
| **Python** (3.11+) | `pip install pypaginate` | [`pypaginate`](https://pypi.org/project/pypaginate/) | [Python](../python/installation) |
| **Node / TypeScript** (18+) | `npm i @cyblow/paginate` | [`@cyblow/paginate`](https://www.npmjs.com/package/@cyblow/paginate) | [TypeScript](../typescript/installation) |
| **Rust** | `cargo add paginate-core` | [`paginate-core`](https://crates.io/crates/paginate-core) | [Rust core](../rust/overview) |

:::tip Polyglot systems
You don't have to choose just one. A common shape is a **Python service** that mints
cursors and a **TypeScript client** that reads them — because the codec is shared,
the cursor round-trips byte-for-byte. See [parity](./parity).
:::

## Python — `pypaginate`

The native engine ships **inside the wheel** (built with PyO3 + maturin), so there's
no Rust toolchain to install. The core has **zero runtime dependencies**; Pydantic is
needed only for the FastAPI extra.

```bash
pip install pypaginate                  # in-memory + native engine
pip install "pypaginate[sqlalchemy]"    # SQLAlchemy 2.0 (sync + async)
pip install "pypaginate[fastapi]"       # FastAPI dependencies (+ Pydantic)
pip install "pypaginate[django]"        # Django Q-object builders
pip install "pypaginate[all]"           # everything
```

→ [Python installation](../python/installation)

## TypeScript / Node — `@cyblow/paginate`

An idiomatic TypeScript adapter over the native addon
[`@cyblow/paginate-core`](https://www.npmjs.com/package/@cyblow/paginate-core), which
installs as a platform-specific dependency (prebuilt binaries via napi-rs).

```bash
npm i @cyblow/paginate
# or: bun add @cyblow/paginate
```

→ [TypeScript installation](../typescript/installation)

## Rust — `paginate-core`

The pure engine itself, with no host/binding dependencies — embed it directly in a
Rust service, or read it to understand what the language packages delegate to.

```toml
[dependencies]
paginate-core = "0.1"
```

→ [Rust core](../rust/overview) · [docs.rs](https://docs.rs/paginate-core)

## What's the same everywhere

- The **20 filter operators**, the stable null-aware **sort**, and **search** ranking.
- The opaque, URL-safe **cursor** format.
- The **validation rules** and limits (e.g. `MAX_LIMIT`, filter nesting depth).
- The **error taxonomy** — each package maps the core's errors to host-native
  exceptions with the same hierarchy.

## What differs (by design)

- **Naming style.** Python uses `snake_case` (`has_next`); TypeScript uses
  `camelCase` (`hasNext`).
- **Spec shapes.** Python specs are dataclasses (`FilterSpec(field=…, operator=…)`);
  TypeScript specs are plain objects (`{ field, operator }`).
- **Integrations.** Python ships SQLAlchemy / Django / FastAPI; TypeScript ships
  Express / Prisma / Drizzle.
