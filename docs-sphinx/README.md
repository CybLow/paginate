# Sphinx Documentation (Experimental)

This directory contains an experimental Sphinx configuration for building pypaginate documentation. The primary documentation system is MkDocs (in `../docs/`).

## Purpose

This Sphinx setup allows comparing MkDocs vs Sphinx for the documentation. Both use the ReadTheDocs theme.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Link markdown files from the main docs:
   ```bash
   ./setup-links.sh
   ```

3. Build the documentation:
   ```bash
   sphinx-build -b html . _build/html
   ```

4. View the documentation:
   ```bash
   python -m http.server 8002 -d _build/html
   # Open http://localhost:8002
   ```

## Differences from MkDocs

| Feature | MkDocs | Sphinx |
|---------|--------|--------|
| Config | `mkdocs.yml` | `conf.py` |
| Index | `index.md` | `index.rst` |
| API Docs | mkdocstrings | autodoc |
| Admonitions | `!!! note` | `.. note::` |
| Mermaid | pymdownx.superfences | sphinxcontrib-mermaid |

## Notes

- The Markdown files are symlinked from `../docs/`
- Some MkDocs-specific syntax may not render correctly
- This is for comparison purposes only; MkDocs is the primary system
