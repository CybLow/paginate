# Format Workflow

Format code using ruff.

## Commands

```bash
# Format all files
uv run ruff format .

# Check formatting without changing files
uv run ruff format --check .

# Format specific file
uv run ruff format src/pypaginate/paginator.py

# Format specific directory
uv run ruff format src/
```

## What It Does

- Applies consistent code style (Black-compatible)
- Fixes line length, quotes, indentation
- Organizes imports (when combined with ruff check)

## Configuration

Formatting is configured in `pyproject.toml`:
- Line length: 100
- Quote style: double
- Indent style: spaces
