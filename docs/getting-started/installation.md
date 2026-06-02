# Installation

This guide covers all installation options for pypaginate.

## Requirements

- **Python 3.11** or higher
- **pip** or **uv** package manager

## Basic Installation

::::{tab-set}

:::{tab-item} uv
```bash
uv add pypaginate
```
:::

:::{tab-item} pip
```bash
pip install pypaginate
```
:::

::::

The base package includes in-memory pagination, filtering specs, sorting specs, and search specs with no heavy dependencies beyond pydantic.

## Installation with Extras

### SQLAlchemy Support

For database pagination (offset and cursor/keyset) with SQLAlchemy 2.0+:

::::{tab-set}

:::{tab-item} uv
```bash
uv add pypaginate[sqlalchemy]
```
:::

:::{tab-item} pip
```bash
pip install pypaginate[sqlalchemy]
```
:::

::::

Includes:

- `SQLAlchemy[asyncio]>=2.0.0` -- ORM and async database toolkit (includes built-in cursor/keyset pagination)

### Search Features

Fuzzy text search is **built into the native engine** -- it always works with the base
install, no extra dependency required.

The `pypaginate[search]` extra is a no-op kept only for backward compatibility (it no
longer installs anything):

::::{tab-set}

:::{tab-item} uv
```bash
uv add pypaginate[search]
```
:::

:::{tab-item} pip
```bash
pip install pypaginate[search]
```
:::

::::

### FastAPI Integration

For FastAPI dependency injection (`OffsetDep`, `CursorDep`, `FilterDep`, etc.):

::::{tab-set}

:::{tab-item} uv
```bash
uv add pypaginate[fastapi]
```
:::

:::{tab-item} pip
```bash
pip install pypaginate[fastapi]
```
:::

::::

Includes:

- `fastapi>=0.95.0` -- FastAPI framework

### Fast Mode (msgspec)

For near-zero-overhead page construction using msgspec structs:

::::{tab-set}

:::{tab-item} uv
```bash
uv add pypaginate[fast]
```
:::

:::{tab-item} pip
```bash
pip install pypaginate[fast]
```
:::

::::

Includes:

- `msgspec>=0.18.0` -- Fast serialization

### All Features

Install everything at once:

::::{tab-set}

:::{tab-item} uv
```bash
uv add pypaginate[all]
```
:::

:::{tab-item} pip
```bash
pip install pypaginate[all]
```
:::

::::

## Development Installation

For contributing to pypaginate:

```bash
git clone https://github.com/CybLow/pypaginate.git
cd pypaginate
uv sync
```

This installs all optional dependencies plus testing, linting, and documentation tools.

## Verifying Installation

```python
>>> import pypaginate
>>> pypaginate.__version__
'0.2.0'

>>> from pypaginate import paginate, OffsetParams
>>> page = paginate([1, 2, 3, 4, 5], OffsetParams(page=1, limit=2))
>>> page.items
[1, 2]
>>> page.total
5
```

### Check Optional Dependencies

```python
# Check SQLAlchemy support
>>> from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend
>>> # No ImportError = SQLAlchemy is installed

# Check FastAPI support
>>> from pypaginate.adapters.fastapi import OffsetDep, FilterDep
>>> # No ImportError = FastAPI is installed

# Check fast mode
>>> from pypaginate.domain.fast_pages import FastOffsetPage
>>> # No ImportError = msgspec is installed
```

## Troubleshooting

### ImportError: FastAPI Features

If you see:

```
ImportError: FastAPI is required: pip install pypaginate[fastapi]
```

Solution:

```bash
pip install pypaginate[fastapi]
```

### ImportError: SQLAlchemy

If you get import errors for `pypaginate.adapters.sqlalchemy`:

```bash
pip install pypaginate[sqlalchemy]
```

### Version Conflicts

If you have version conflicts:

```bash
uv venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

pip install pypaginate[all]
```

## Next Steps

- [Quick Start Guide](quickstart.md) -- Learn the basics in 5 minutes
- [First Steps](first-steps.md) -- Filtering, sorting, and search
