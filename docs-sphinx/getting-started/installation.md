# Installation

This guide covers all installation options for pypaginate.

## Requirements

- **Python 3.11** or higher
- **pip** or **uv** package manager

## Basic Installation

### Using uv (Recommended)

[uv](https://docs.astral.sh/uv/) is a fast Python package manager:

```bash
uv add pypaginate
```

### Using pip

```bash
pip install pypaginate
```

## Installation with Optional Features

pypaginate uses optional dependencies to keep the core package lightweight. Install only what you need:

### SQLAlchemy Support

For database pagination with SQLAlchemy 2.0+:

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

This includes:

- `SQLAlchemy>=2.0.45` - ORM and database toolkit
- `sqlakeyset>=2.0` - Keyset pagination support

### Search Features

For full-text search with fuzzy matching:

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

This includes:

- `rapidfuzz>=3.14` - Fast fuzzy string matching
- `pyparsing>=3.3` - Query parsing

### Filtering Features

For advanced JSON Logic filtering:

::::{tab-set}

:::{tab-item} uv
```bash
uv add pypaginate[filters]
```
:::

:::{tab-item} pip
```bash
pip install pypaginate[filters]
```
:::

::::

This includes:

- `json-logic-qubit>=0.9` - JSON Logic evaluator
- `jmespath>=1.0` - Nested field access

### Text Processing

For text normalization (accent removal, etc.):

::::{tab-set}

:::{tab-item} uv
```bash
uv add pypaginate[text]
```
:::

:::{tab-item} pip
```bash
pip install pypaginate[text]
```
:::

::::

This includes:

- `text-unidecode>=1.3` - ASCII transliteration

### FastAPI Integration

For FastAPI dependency injection:

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

This includes:

- `fastapi>=0.127` - FastAPI framework

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
# Clone the repository
git clone https://github.com/CybLow/pypaginate.git
cd pypaginate

# Install with development dependencies
uv sync
```

This installs:

- All optional dependencies
- Testing tools (pytest, coverage)
- Linting tools (ruff, mypy)
- Documentation tools (Sphinx)

## Verifying Installation

After installation, verify everything works:

```python
>>> import pypaginate
>>> pypaginate.__version__
'0.1.0'

>>> from pypaginate import PageParams, Page
>>> params = PageParams(page=1, limit=20)
>>> params.offset
0
```

### Check Optional Dependencies

```python
# Check SQLAlchemy support
>>> from pypaginate import paginate_entities
>>> # No ImportError = SQLAlchemy is installed

# Check search support
>>> from pypaginate.filters.search import MemorySearchService
>>> # No ImportError = search features are installed

# Check filter support
>>> from pypaginate.filters.predicates import FilterEngine
>>> # No ImportError = filter features are installed
```

## Troubleshooting

### ImportError: SQLAlchemy Features

If you see:

```
ImportError: SQLAlchemy features require installation: uv add pypaginate[sqlalchemy]
```

Solution: Install the SQLAlchemy extra:

```bash
uv add pypaginate[sqlalchemy]
```

### ImportError: rapidfuzz

If you see errors about `rapidfuzz`:

```bash
uv add pypaginate[search]
```

### Version Conflicts

If you have version conflicts with existing packages:

```bash
# Create a fresh virtual environment with uv
uv venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install pypaginate
uv add pypaginate[all]
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Learn the basics in 5 minutes
- [First Steps Tutorial](first-steps.md) - Build your first paginated API
