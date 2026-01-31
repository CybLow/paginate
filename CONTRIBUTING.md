# Contributing to pypaginate

Thank you for your interest in contributing to pypaginate! We welcome contributions from the community.

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

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/CybLow/pypaginate.git
   cd pypaginate
   ```

2. **Install dependencies with UV**
   ```bash
   uv sync
   ```

3. **Install pre-commit hooks** (optional but recommended)
   ```bash
   uv run pre-commit install
   ```

## Code Quality Standards

All contributions must pass the following quality gates:

### Quick Quality Check
```bash
# Run essential checks (format, lint, test)
uv run pypaginate qa

# Or with make
make qa
```

### Individual Checks

| Check | Command | Alias |
|-------|---------|-------|
| Linting | `uv run pypaginate lint` | `uv run ruff check src tests` |
| Formatting | `uv run pypaginate format` | `uv run ruff format src tests` |
| Type Checking | `uv run pypaginate typecheck` | `uv run mypy src` |
| Tests | `uv run pypaginate test` | `uv run pytest` |
| All Checks | `uv run pypaginate qas` | Includes mypy |

### Requirements

- ✅ Zero linting errors
- ✅ All tests pass
- ✅ Code is properly formatted
- ✅ New features include tests
- ✅ Type hints for all public APIs

## Development Workflow

### Branch Naming Convention

We use a structured branching model. Always create branches from `develop`:

| Branch Pattern | Purpose | Example |
|----------------|---------|---------|
| `main` | Production-ready code | - |
| `develop` | Integration branch | - |
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
| **Tier 2** (Standard) | `develop`, Pull Requests | + Integration + Property Tests + Build |
| **Tier 3** (Full) | `main`, `release/*` | + Benchmarks |

### Workflow Steps

1. **Create a feature branch from develop**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, typed Python code
   - Follow existing code style and patterns
   - Keep functions small and focused

3. **Run quality checks**
   ```bash
   uv run pypaginate qa
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: description of your feature"
   ```

5. **Push and create a Pull Request to develop**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **After PR approval and merge to develop**
   - Create a release branch when ready: `release/v1.2.0`
   - Merge to `main` for production release

## Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Code style (formatting)
- `refactor:` Code refactor (no feature/fix)
- `test:` Adding/updating tests
- `chore:` Maintenance tasks

## Pull Request Guidelines

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Quality checks pass (`uv run pypaginate qa`)
- [ ] New code has tests
- [ ] Documentation is updated (if needed)
- [ ] CHANGELOG.md is updated

### Review Process

1. CI will automatically run all quality checks
2. A maintainer will review your PR
3. Address any feedback
4. Once approved, your PR will be merged

## Testing Guidelines

### Test Structure
```python
def test_feature_name() -> None:
    """Test description following Arrange-Act-Assert pattern."""
    # Arrange
    setup = create_test_data()

    # Act
    result = function_under_test(setup)

    # Assert
    assert result == expected
```

### Test Markers
- `@pytest.mark.unit`: Fast unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.sqlalchemy`: Tests requiring SQLAlchemy
- `@pytest.mark.search`: Tests requiring search features
- `@pytest.mark.filters`: Tests requiring filter features

## Code Style

### Type Hints
- Always use type hints for function signatures
- Use `from __future__ import annotations`
- Prefer `collections.abc` types over built-in generics

### Documentation
- Use docstrings for all public functions/classes
- Follow Google docstring style
- Include examples for complex functionality

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue with reproduction steps
- **Features**: Open a GitHub Issue with use case description

## Code of Conduct

Be respectful and inclusive. We follow the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).

---

Thank you for contributing to pypaginate! 🚀
