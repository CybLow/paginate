---
sidebar_position: 1
title: Installation
description: Install pypaginate with pip or uv. The native Rust engine ships inside the wheel — no toolchain needed. Optional extras for SQLAlchemy, FastAPI, and Django.
---

# Installation

```bash
pip install pypaginate
```

**Python 3.11+.** The native engine ships **inside the wheel** (built with PyO3 +
maturin), so there's **no Rust toolchain to install** and no separate native package
to manage. Prebuilt wheels cover Linux (manylinux + musllinux), macOS, and Windows on
x86-64 and arm64.

The core has **zero runtime dependencies**. Pydantic is **not** a core dependency —
install an extra only for the adapter you use.

## Extras

```bash
pip install "pypaginate[sqlalchemy]"   # SQLAlchemy 2.0 offset + keyset (sync + async)
pip install "pypaginate[fastapi]"      # FastAPI dependencies (+ Pydantic request models)
pip install "pypaginate[django]"       # Django Q-object builders
pip install "pypaginate[all]"          # everything above
```

| Extra | Pulls in | For |
|---|---|---|
| `sqlalchemy` | `SQLAlchemy[asyncio]>=2.0` | [SQLAlchemy integration](./integrations/sqlalchemy) |
| `fastapi` | `fastapi>=0.95`, `pydantic>=2.0` | [FastAPI integration](./integrations/fastapi) |
| `django` | `Django>=4.2` | [Django integration](./integrations/django) |

Ranked and fuzzy/trigram **search needs no extra** — it runs in the native engine.

## With uv

```bash
uv add pypaginate
uv add "pypaginate[all]"
```

## Verify

```python
import pypaginate
print(pypaginate.__version__)
```

## Next

- [Quickstart](./quickstart) — paginate, filter, sort, and search in a few lines.
