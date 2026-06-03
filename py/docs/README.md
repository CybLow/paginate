---
orphan: true
---

# pypaginate Documentation

This directory contains the Sphinx documentation for pypaginate.

## Quick Start

1. Install dependencies:
   ```bash
   uv sync --group docs
   ```

2. Build the documentation:
   ```bash
   uv run sphinx-build -b html docs docs/_build/html
   ```

3. View locally:
   ```bash
   python -m http.server 8000 -d docs/_build/html
   # Open http://localhost:8000
   ```

## Development

For live preview with auto-rebuild:
```bash
uv run sphinx-autobuild docs docs/_build/html
```

Build with warnings as errors (CI mode):
```bash
uv run sphinx-build -W -b html docs docs/_build/html
```

## Multi-Version Builds

For building documentation across multiple versions/tags:
```bash
uv run sphinx-polyversion docs/poly.py
```

## Structure

| Directory | Purpose |
|-----------|---------|
| `api/` | Auto-generated API reference |
| `concepts/` | Core concepts and architecture |
| `examples/` | Code examples and tutorials |
| `filtering/` | Filter system documentation |
| `getting-started/` | Quick start guides |
| `_static/` | Static assets (CSS, images, logo) |
| `_templates/` | Jinja2 templates |

## Configuration

| File | Purpose |
|------|---------|
| `conf.py` | Sphinx configuration |
| `poly.py` | sphinx-polyversion config |
| `index.md` | Documentation home page |

## Writing Docs

- Use MyST Markdown (`.md` files)
- Follow Google-style docstrings for API docs
- Use `{py:class}`, `{py:func}`, etc. for cross-references
- Admonitions: `:::{note}`, `:::{warning}`, `:::{tip}`
