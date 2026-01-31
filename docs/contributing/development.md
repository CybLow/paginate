# Development Setup

This guide covers setting up your development environment for pypaginate.

## Prerequisites

- **Python 3.11+** (3.12 recommended)
- **[UV](https://docs.astral.sh/uv/)** - Fast Python package manager
- **Git**

## Installing UV

UV is a fast, modern Python package manager that we use for development.

=== "macOS/Linux"
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "Windows"
    ```powershell
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

=== "pip"
    ```bash
    pip install uv
    ```

## Setting Up the Project

### 1. Fork and Clone

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/pypaginate.git
cd pypaginate

# Add upstream remote
git remote add upstream https://github.com/CybLow/pypaginate.git
```

### 2. Install Dependencies

```bash
# Install all dependencies including dev tools
uv sync

# This installs:
# - Production dependencies
# - Development tools (pytest, mypy, ruff)
# - Documentation tools (mkdocs)
```

### 3. Install Pre-commit Hooks (Optional)

```bash
uv run pre-commit install
```

Pre-commit hooks run quality checks before each commit.

### 4. Verify Setup

```bash
# Run tests
uv run pytest

# Run quality checks
uv run pypaginate qa
```

## Project Structure

```
pypaginate/
├── src/
│   └── pypaginator/       # Main package
│       ├── core/          # Core types
│       ├── engines/       # Pagination engines
│       ├── filters/       # Filtering system
│       ├── sorting/       # Sorting utilities
│       ├── query/         # Query API
│       ├── integrations/  # Framework integrations
│       └── exceptions.py  # Custom exceptions
├── tests/                 # Test suite
├── docs/                  # Documentation
├── examples/              # Example scripts
├── pyproject.toml         # Project configuration
└── mkdocs.yml            # Documentation config
```

## Development Commands

### Using the CLI

pypaginate includes a CLI for common development tasks:

```bash
# Run all quality checks (lint, format, test)
uv run pypaginate qa

# Run quality checks + type checking
uv run pypaginate qas

# Individual commands
uv run pypaginate lint      # Check linting
uv run pypaginate format    # Format code
uv run pypaginate typecheck # Run mypy
uv run pypaginate test      # Run tests
```

### Using Make (Alternative)

```bash
make qa        # All quality checks
make test      # Run tests
make lint      # Lint code
make format    # Format code
```

### Direct Commands

```bash
# Linting
uv run ruff check src tests

# Formatting
uv run ruff format src tests

# Type checking
uv run mypy src

# Tests
uv run pytest
uv run pytest -v              # Verbose
uv run pytest -x              # Stop on first failure
uv run pytest --cov           # With coverage
```

## IDE Setup

### VS Code

1. Install Python extension
2. Open the project folder
3. Select Python interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter"
4. Choose the UV virtual environment

Recommended settings (`.vscode/settings.json`):

```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.analysis.typeCheckingMode": "strict",
    "editor.formatOnSave": true,
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff"
    }
}
```

### PyCharm

1. Open the project
2. Configure Python interpreter: Use existing UV environment
3. Enable Ruff for linting (install Ruff plugin)
4. Configure pytest as test runner

## Running Tests

### All Tests

```bash
uv run pytest
```

### Specific Tests

```bash
# Single file
uv run pytest tests/test_pages.py

# Single test
uv run pytest tests/test_pages.py::test_page_creation

# By marker
uv run pytest -m unit
uv run pytest -m integration
```

### With Coverage

```bash
# Terminal report
uv run pytest --cov=pypaginator --cov-report=term-missing

# HTML report
uv run pytest --cov=pypaginator --cov-report=html
# Open htmlcov/index.html
```

## Building Documentation

```bash
# Serve locally with hot reload
uv run mkdocs serve

# Build static site
uv run mkdocs build
```

Visit http://127.0.0.1:8000 to preview documentation.

## Keeping Up to Date

```bash
# Fetch upstream changes
git fetch upstream

# Merge into your main branch
git checkout main
git merge upstream/main

# Update your feature branch
git checkout feature/your-feature
git rebase main
```

## Troubleshooting

### Import Errors

```bash
# Reinstall in development mode
uv pip install -e .
```

### Dependency Issues

```bash
# Clear and reinstall
uv sync --reinstall
```

### Test Failures

```bash
# Clear pytest cache
uv run pytest --cache-clear
```

## Next Steps

- [Testing Guide](testing.md) - Learn about testing
- [Code Style](code-style.md) - Coding standards
- [Architecture](architecture.md) - Understand the codebase
