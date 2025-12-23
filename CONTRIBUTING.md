# Contributing to PyPaginator

Thank you for your interest in contributing to PyPaginator! We welcome contributions from the community.

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
   git clone https://github.com/yourusername/pypaginator.git
   cd pypaginator
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
uv run pypaginator qa

# Or with make
make qa
```

### Individual Checks

| Check | Command | Alias |
|-------|---------|-------|
| Linting | `uv run pypaginator lint` | `uv run ruff check src tests` |
| Formatting | `uv run pypaginator format` | `uv run ruff format src tests` |
| Type Checking | `uv run pypaginator typecheck` | `uv run mypy src` |
| Tests | `uv run pypaginator test` | `uv run pytest` |
| All Checks | `uv run pypaginator qas` | Includes mypy |

### Requirements

- ✅ Zero linting errors
- ✅ All tests pass
- ✅ Code is properly formatted
- ✅ New features include tests
- ✅ Type hints for all public APIs

## Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, typed Python code
   - Follow existing code style and patterns
   - Keep functions small and focused

3. **Run quality checks**
   ```bash
   uv run pypaginator qa
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: description of your feature"
   ```

5. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

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
- [ ] Quality checks pass (`uv run pypaginator qa`)
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

Thank you for contributing to PyPaginator! 🚀
