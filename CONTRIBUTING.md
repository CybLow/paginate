# Contributing to PyPaginator

Thank you for your interest in contributing to PyPaginator! We welcome contributions from the community.

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/pypaginator.git
   cd pypaginator
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev,all]"
   ```

## Code Quality Standards

All contributions must pass the following quality gates:

### 1. Type Checking (mypy)
```bash
mypy src/pypaginator
```
- Must pass with `--strict` mode
- 100% type coverage required

### 2. Linting (ruff)
```bash
ruff check src/pypaginator
```
- Zero linting issues allowed

### 3. Code Formatting (black)
```bash
black src/pypaginator tests
```
- All code must be formatted with Black

### 4. Tests (pytest)
```bash
pytest --cov=pypaginator --cov-report=term-missing
```
- All tests must pass
- Minimum 90% code coverage
- New features must include tests

### 5. Complexity (radon)
```bash
radon cc -s -n B src/pypaginator
```
- All functions must have cyclomatic complexity ≤ 8 (grade A or B)

## Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, typed Python code
   - Follow existing code style and patterns
   - Keep functions small and focused

3. **Add tests**
   - Write unit tests for new functionality
   - Ensure tests are isolated and repeatable
   - Use appropriate pytest markers (`@pytest.mark.unit`, etc.)

4. **Run quality checks**
   ```bash
   # Run all checks
   mypy src/pypaginator
   ruff check src/pypaginator
   black src/pypaginator tests
   pytest
   radon cc -s -n B src/pypaginator
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description of your feature"
   ```
   - Use clear, descriptive commit messages
   - Follow conventional commits format if possible

6. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Pull Request Guidelines

- **Title**: Clear and descriptive
- **Description**: Explain what changes you made and why
- **Tests**: Include test results showing all checks pass
- **Documentation**: Update README or docs if needed
- **Breaking Changes**: Clearly mark any breaking changes

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass (`pytest`)
- [ ] Type checking passes (`mypy --strict`)
- [ ] Linting passes (`ruff check`)
- [ ] Code is formatted (`black`)
- [ ] Complexity is low (`radon cc`)
- [ ] New code has tests
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated

## Code Style Guidelines

### Naming Conventions
- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: Prefix with `_`

### Type Hints
- Always use type hints for function signatures
- Use `from __future__ import annotations` for forward references
- Prefer `collections.abc` types over built-in generics

### Documentation
- Use docstrings for all public functions and classes
- Follow Google docstring style
- Include examples for complex functionality

### Error Handling
- Use custom exceptions from `pypaginator.exceptions`
- Provide clear error messages
- Don't catch exceptions silently

### File Organization
- Keep files under 200 lines when possible
- One class per file for large classes
- Group related functions together

## Testing Guidelines

### Test Structure
```python
def test_feature_name():
    """Test description following Arrange-Act-Assert pattern."""
    # Arrange
    setup = create_test_data()
    
    # Act
    result = function_under_test(setup)
    
    # Assert
    assert result == expected
```

### Test Markers
- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.sqlalchemy`: Tests requiring SQLAlchemy
- `@pytest.mark.search`: Tests requiring search features
- `@pytest.mark.filters`: Tests requiring filter features

### Fixtures
- Use fixtures for common test data
- Keep fixtures focused and reusable
- Document fixture purpose

## Adding New Features

### 1. Core Types
- Immutable dataclasses with `@dataclass(frozen=True)`
- Protocol definitions in `types.py`
- Concrete implementations in appropriate modules

### 2. Engines
- Inherit from base protocols
- Keep engine logic focused
- Support both sync and async where applicable

### 3. Filters/Search
- Add operators to appropriate operator modules
- Register in `operators/__init__.py`
- Include comprehensive tests

### 4. Integrations
- Keep framework-specific code in `integrations/`
- Make dependencies optional
- Provide helpful error messages when dependencies missing

## Documentation

### API Documentation
- Update docstrings for any changed functions
- Include examples in docstrings
- Keep documentation current with code

### User Documentation
- Update README.md for user-facing changes
- Add examples to `examples/` directory
- Update `docs/` for major features

### Architecture Documentation
- Update architecture docs for structural changes
- Document design decisions
- Keep architecture diagrams current

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with changes
3. Create a git tag: `git tag v0.x.x`
4. Push tag: `git push origin v0.x.x`
5. GitHub Actions will automatically publish to PyPI

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue with reproduction steps
- **Features**: Open a GitHub Issue with use case description

## Code of Conduct

Be respectful and inclusive. We follow the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).

---

Thank you for contributing to PyPaginator! 🚀

