---
sidebar_position: 1
---

# Installation

## Python

```bash
pip install pypaginate
```

Python 3.11+. The native engine ships **inside the wheel** — no Rust toolchain needed.
Pydantic is **not** a core dependency; install an extra only for the adapter you use:

```bash
pip install "pypaginate[fastapi]"      # FastAPI dependencies + Pydantic request models
pip install "pypaginate[sqlalchemy]"   # SQLAlchemy offset + keyset cursor
pip install "pypaginate[django]"       # Django Q-object builders
```

## TypeScript / Node

```bash
npm i @cyblow/paginate
# or
bun add @cyblow/paginate
```

The native addon (`paginate-core`) installs as a platform-specific dependency.

## Rust

```toml
[dependencies]
paginate-core = "0.1"
```

The pure engine — no host/binding dependencies. API reference on
[docs.rs](https://docs.rs/paginate-core).
