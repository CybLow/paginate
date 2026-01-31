# Testing Guide

This guide explains how to write and run tests for pypaginate.

## Running Tests

### All Tests

```bash
# Simple execution
uv run pytest

# Verbose output
uv run pytest -v

# Parallel execution (faster)
uv run pytest -n auto
```

### Specific Tests

```bash
# Single file
uv run pytest tests/test_pages.py

# Single class
uv run pytest tests/test_pages.py::TestPage

# Single test
uv run pytest tests/test_pages.py::TestPage::test_creation

# By marker
uv run pytest -m unit
uv run pytest -m integration
```

### Useful Options

```bash
# Stop on first failure
uv run pytest -x

# Show print statements
uv run pytest -s

# Re-run failed tests only
uv run pytest --lf

# Quiet mode
uv run pytest -q
```

## Test Coverage

### Generate Reports

```bash
# Terminal report
uv run pytest --cov=pypaginate --cov-report=term-missing

# HTML report (recommended)
uv run pytest --cov=pypaginate --cov-report=html
# Open htmlcov/index.html in browser

# Fail if below threshold
uv run pytest --cov=pypaginate --cov-fail-under=80
```

### Coverage for Specific Module

```bash
uv run pytest tests/test_filters.py \
    --cov=pypaginate.filters \
    --cov-report=term-missing
```

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures
├── test_core.py               # Core types tests
├── test_pages.py              # Pagination tests
├── test_filter_engine.py      # Filter tests
├── test_search.py             # Search tests
├── test_sorting.py            # Sorting tests
├── test_sql_filter_adapter.py # SQL adapter tests
├── test_fastapi_integration.py # FastAPI tests
└── ...
```

### Naming Conventions

- **Files:** `test_<module>.py`
- **Classes:** `Test<ClassName>`
- **Methods:** `test_<description_snake_case>`
- **Fixtures:** `<resource_name>` (no `test_` prefix)

## Writing Tests

### Basic Test Template

```python
"""Tests for module X."""
from __future__ import annotations

import pytest
from pypaginate.module import ClassToTest


class TestClassName:
    """Tests for ClassName."""

    def test_basic_functionality(self) -> None:
        """Test basic functionality works correctly."""
        # Arrange
        obj = ClassToTest()
        
        # Act
        result = obj.method()
        
        # Assert
        assert result == expected_value

    def test_edge_case(self) -> None:
        """Test edge case handling."""
        obj = ClassToTest()
        
        with pytest.raises(ValueError):
            obj.method_that_raises()
```

### Using Fixtures

```python
@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return [1, 2, 3, 4, 5]


class TestWithFixture:
    def test_using_fixture(self, sample_data):
        """Test using a fixture."""
        assert len(sample_data) == 5
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    """Test doubling values."""
    assert double(input) == expected
```

### Async Tests

```python
import pytest


@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await async_function()
    assert result == expected
```

### Database Tests

```python
@pytest.fixture
def db_session():
    """Create a database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


def test_with_database(db_session):
    """Test database operations."""
    user = User(name="Alice")
    db_session.add(user)
    db_session.commit()
    
    assert db_session.query(User).count() == 1
```

## Test Markers

Available markers:

| Marker | Description |
|--------|-------------|
| `@pytest.mark.unit` | Fast unit tests |
| `@pytest.mark.integration` | Integration tests |
| `@pytest.mark.asyncio` | Async tests |
| `@pytest.mark.sqlalchemy` | SQLAlchemy tests |
| `@pytest.mark.search` | Search feature tests |
| `@pytest.mark.filters` | Filter feature tests |

## Best Practices

### 1. Arrange-Act-Assert Pattern

```python
def test_user_creation():
    # Arrange
    name = "Alice"
    email = "alice@example.com"
    
    # Act
    user = User(name=name, email=email)
    
    # Assert
    assert user.name == name
    assert user.email == email
```

### 2. Test Edge Cases

```python
def test_edge_cases():
    # Empty input
    assert process([]) == []
    
    # Single item
    assert process([1]) == [1]
    
    # None input
    with pytest.raises(TypeError):
        process(None)
```

### 3. Isolated Tests

```python
# GOOD: Each test creates its own state
def test_addition():
    calculator = Calculator()
    assert calculator.add(2, 3) == 5

# BAD: Shared state between tests
calculator = Calculator()
def test_addition():
    assert calculator.add(2, 3) == 5
```

### 4. Descriptive Names

```python
# GOOD
def test_paginate_returns_empty_page_for_empty_list():
    ...

# BAD
def test_1():
    ...
```

### 5. Mock External Dependencies

```python
def test_api_call(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"status": "ok"}
    mocker.patch("requests.get", return_value=mock_response)
    
    result = fetch_data()
    assert result["status"] == "ok"
```

## Troubleshooting

### Tests Pass Locally But Fail in CI

1. Check dependency versions
2. Clear pytest cache: `pytest --cache-clear`
3. Reinstall dependencies: `uv sync --reinstall`

### Import Errors

```bash
# Ensure package is installed in editable mode
uv pip install -e .
```

### Slow Tests

```bash
# Parallel execution
pip install pytest-xdist
pytest -n auto

# Skip coverage during development
pytest  # Without --cov
```

## Contributing Tests

### Checklist

- [ ] Tests follow naming conventions
- [ ] Clear docstrings
- [ ] Isolated and independent
- [ ] Edge cases covered
- [ ] Error cases tested
- [ ] Type hints added
- [ ] Tests pass locally
- [ ] Coverage verified

### Submitting

1. Create branch: `git checkout -b test/module-name`
2. Write tests
3. Verify coverage: `pytest --cov`
4. Commit: `git commit -m "test: add tests for module X"`
5. Push and create PR
