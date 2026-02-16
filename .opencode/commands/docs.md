# Documentation Workflow

Build and serve documentation using Sphinx.

## Commands

```bash
# Build HTML docs
uv run sphinx-build -b html docs docs/_build/html

# Build with strict mode (warnings as errors)
uv run sphinx-build -W -b html docs docs/_build/html

# Serve docs locally (with auto-rebuild)
uv run sphinx-autobuild docs docs/_build/html

# Build multi-version docs
uv run sphinx-polyversion docs/poly.py

# Quick build (incremental, faster)
uv run sphinx-build -b html docs docs/_build/html

# Check for issues
uv run sphinx-build -W -n -b html docs docs/_build/html
```

## Project Structure

```
docs/
├── index.md              # Home page (MyST Markdown)
├── conf.py               # Sphinx configuration
├── poly.py               # Multi-version build config
├── getting-started/      # Quick start guides
├── concepts/             # Core concepts
├── filtering/            # Filter documentation
├── api/                  # API reference (autodoc)
├── examples/             # Code examples
├── _static/              # Static assets (CSS, images)
└── _templates/           # Custom Jinja templates
```

## Writing Documentation

### Docstrings (Google Style)

```python
def paginate(items: list[T], page: int = 1) -> Page[T]:
    """Paginate a list of items.

    Args:
        items: The items to paginate.
        page: Page number (1-indexed). Defaults to 1.

    Returns:
        A Page containing the requested items.

    Raises:
        ValueError: If page is less than 1.

    Example:
        >>> page = paginate(users, page=2)
        >>> print(page.items)
    """
```

### Cross-references (MyST Markdown)

```markdown
See {py:class}`pypaginate.Paginator` for details.
Check the {doc}`/api/index` reference.
```

### Admonitions

```markdown
:::{note}
This is a note.
:::

:::{warning}
This is a warning.
:::

:::{tip}
This is a tip.
:::
```

## Configuration

Documentation configured in `docs/conf.py`:
- Theme: Read the Docs (sphinx-rtd-theme)
- Markdown: MyST Parser
- API docs: sphinx-autodoc with typehints
- Extensions: sphinx-design, sphinx-copybutton, mermaid
