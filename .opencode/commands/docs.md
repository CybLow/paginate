# Documentation Workflow

Build and serve documentation using MkDocs.

## Commands

```bash
# Serve docs locally (with hot reload)
uv run mkdocs serve

# Build static docs
uv run mkdocs build

# Build with strict mode (fail on warnings)
uv run mkdocs build --strict

# Deploy to GitHub Pages
uv run mkdocs gh-deploy

# Check for broken links
uv run mkdocs build --strict 2>&1 | grep -i "warning"
```

## Project Structure

```
docs/
├── index.md              # Home page
├── getting-started/      # Quick start guides
├── user-guide/           # Detailed usage
├── api/                  # API reference (auto-generated)
└── examples/             # Code examples
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

### Cross-references

```markdown
See [Paginator][pypaginate.Paginator] for details.
Check the [API Reference](../api/paginator.md).
```

## Configuration

Documentation configured in `mkdocs.yml`:
- Theme: Material for MkDocs
- API docs: mkdocstrings (auto-generated from docstrings)
- Code highlighting: Pygments
