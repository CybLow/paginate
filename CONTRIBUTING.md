# Contributing to pypaginate

Thank you for your interest in contributing to pypaginate! We welcome contributions from the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Prerequisites](#prerequisites)
- [Development Setup](#development-setup)
- [Code Quality Standards](#code-quality-standards)
- [Development Workflow](#development-workflow)
- [Commit Message Convention](#commit-message-convention)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Code Style](#code-style)
- [Getting Help](#getting-help)

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Be respectful and inclusive.

## Prerequisites

- **Python 3.11+**
- **[UV](https://docs.astral.sh/uv/)** - Fast Python package manager

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# or
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows
```

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/pypaginate.git
cd pypaginate
```

### 2. Install Dependencies

```bash
# Install all development dependencies
uv sync --frozen --all-extras --group dev
```

### 3. Install Pre-commit Hooks

```bash
uv run pre-commit install
```

### 4. Verify Setup

```bash
# Run all quality checks
uv run ruff format --check .
uv run ruff check .
uv run mypy src/
uv run pytest
```

## Code Quality Standards

All contributions must pass the following quality gates:

### Quick Quality Check

```bash
# Run all checks at once
uv run ruff format . && uv run ruff check . && uv run mypy src/ && uv run pytest
```

### Individual Checks

| Check | Command |
|-------|---------|
| Format | `uv run ruff format .` |
| Lint | `uv run ruff check .` |
| Type Check | `uv run mypy src/` |
| Tests | `uv run pytest` |
| Tests + Coverage | `uv run pytest --cov=pypaginate` |

### Requirements

- ✅ Zero linting errors
- ✅ All tests pass
- ✅ Code is properly formatted
- ✅ New features include tests
- ✅ Type hints for all public APIs

### Size Limits

Please follow these limits (see [CLAUDE.md](CLAUDE.md) for complete guidelines):

| Metric | Limit |
|--------|-------|
| Lines per function | ≤15 |
| Lines per file | ≤250 |
| Parameters per function | ≤4 |
| Nesting levels | ≤2 |

## Development Workflow

### Branch Naming Convention

Create branches from `main` using this pattern:

| Branch Pattern | Purpose | Example |
|----------------|---------|---------|
| `main` | Production-ready code | - |
| `release/v*` | Release candidates | `release/v1.2.0` |
| `feature/*` | New features | `feature/add-keyset-pagination` |
| `fix/*` | Bug fixes | `fix/memory-leak-in-paginator` |
| `hotfix/*` | Urgent production fixes | `hotfix/critical-security-issue` |
| `refactor/*` | Code improvements | `refactor/simplify-engine` |
| `docs/*` | Documentation only | `docs/update-api-reference` |
| `test/*` | Test improvements | `test/add-edge-cases` |
| `chore/*` | Maintenance tasks | `chore/update-dependencies` |

### CI Pipeline Tiers

The CI pipeline runs different test suites based on branch type:

| Tier | Branches | Tests Run |
|------|----------|-----------|
| **Tier 1** (Fast) | `feature/*`, `fix/*`, `refactor/*`, etc. | Quality + Unit Tests |
| **Tier 2** (Standard) | Pull Requests | + Integration + Property Tests + Build |
| **Tier 3** (Full) | `main`, `release/*` | + Benchmarks |

### Workflow Steps

1. **Create a feature branch from main**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, typed Python code
   - Follow existing code style and patterns
   - Keep functions small and focused

3. **Run quality checks**
   ```bash
   uv run ruff format .
   uv run ruff check .
   uv run mypy src/
   uv run pytest
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat(scope): description of your feature"
   ```

5. **Push and create a Pull Request to main**
   ```bash
   git push -u origin feature/your-feature-name
   ```

## Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Types

| Type | Purpose |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Code style (formatting) |
| `refactor` | Code refactor (no feature/fix) |
| `perf` | Performance improvement |
| `test` | Adding/updating tests |
| `chore` | Maintenance tasks |
| `ci` | CI/CD changes |

### Examples

```bash
git commit -m "feat(filters): add JSONLogic filter support"
git commit -m "fix(pagination): correct offset calculation for empty results"
git commit -m "docs: update installation instructions"
git commit -m "test(core): add edge case tests for pagination"
```

## Pull Request Guidelines

### Before Submitting

1. Ensure all checks pass
2. Update documentation if needed
3. Add/update tests for your changes
4. Fill out the PR template completely

### PR Checklist

- [ ] I have read the CONTRIBUTING guidelines
- [ ] Code follows project style guidelines ([CLAUDE.md](CLAUDE.md))
- [ ] All quality checks pass
- [ ] New code has tests
- [ ] Documentation is updated (if needed)

### Review Process

1. CI will automatically run all quality checks
2. A maintainer will review your PR
3. Address any feedback
4. Once approved, your PR will be merged

## Testing Guidelines

### Test Structure

```
tests/
├── unit/           # Fast, isolated tests
├── integration/    # Tests with external dependencies
├── property/       # Property-based tests (Hypothesis)
├── architecture/   # Code quality enforcement
├── perf/           # Performance benchmarks
└── e2e/            # End-to-end tests
```

### Writing Tests

Follow the AAA pattern (Arrange, Act, Assert):

```python
def test_paginate_returns_correct_page() -> None:
    """Test that pagination returns the correct page of items."""
    # Arrange
    items = [1, 2, 3, 4, 5]
    params = OffsetParams(page=1, limit=2)

    # Act
    result = paginate(items, params)

    # Assert
    assert result.items == [1, 2]
    assert result.total == 5
```

### Test Markers

| Marker | Purpose |
|--------|---------|
| `@pytest.mark.unit` | Fast unit tests |
| `@pytest.mark.integration` | Integration tests |
| `@pytest.mark.property` | Property-based tests |
| `@pytest.mark.slow` | Slow tests (skipped by default) |
| `@pytest.mark.benchmark` | Benchmark tests |

### Running Specific Tests

```bash
# Unit tests only
uv run pytest tests/unit

# With coverage
uv run pytest --cov=pypaginate --cov-report=term-missing

# Specific file
uv run pytest tests/unit/domain/test_pages.py

# By marker
uv run pytest -m "not slow"
```

## Code Style

### Type Hints

- Always use type hints for function signatures
- Use `from __future__ import annotations` at the top of all files
- Prefer `collections.abc` types for parameters, concrete types for returns

```python
from __future__ import annotations

from collections.abc import Sequence

def process_items(items: Sequence[int]) -> list[int]:
    """Process and return items."""
    return [x * 2 for x in items]
```

### Documentation

- Use docstrings for all public functions/classes
- Follow Google docstring style
- Include examples for complex functionality

```python
def paginate(items: list[T], params: OffsetParams) -> OffsetPage[T]:
    """Paginate a list of items.

    Args:
        items: The items to paginate.
        params: Pagination parameters.

    Returns:
        An OffsetPage containing the paginated items.

    Raises:
        ValidationError: If page or limit is less than 1.

    Example:
        >>> items = [1, 2, 3, 4, 5]
        >>> result = paginate(items, OffsetParams(page=1, limit=2))
        >>> result.items
        [1, 2]
    """
```

## Getting Help

- **Questions**: Open a [GitHub Discussion](https://github.com/CybLow/pypaginate/discussions)
- **Bugs**: Open a [GitHub Issue](https://github.com/CybLow/pypaginate/issues) with reproduction steps
- **Features**: Open a [GitHub Issue](https://github.com/CybLow/pypaginate/issues) with use case description
- **Security**: See [SECURITY.md](SECURITY.md) for reporting vulnerabilities

---

Thank you for contributing to pypaginate! 🚀
