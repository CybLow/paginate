# Code Style

Standards enforced across pypaginate by tooling, architecture tests, and convention.

The canonical reference is [CLAUDE.md](https://github.com/CybLow/pypaginate/blob/main/CLAUDE.md) in the repository root.
This page summarizes the key rules.

---

## Tools

| Tool | Purpose | Command |
|---|---|---|
| [Ruff](https://docs.astral.sh/ruff/) | Lint + format | `uv run ruff check src/ && uv run ruff format .` |
| [mypy](https://mypy.readthedocs.io/) | Type checking (strict) | `uv run mypy src/` |
| [pytest](https://docs.pytest.org/) | Testing | `uv run pytest tests/ --ignore=tests/perf -q` |
| [bandit](https://bandit.readthedocs.io/) | Security scan | `uv run bandit -r src/ -c pyproject.toml` |

### Run All Checks

```bash
uv run ruff format . && uv run ruff check --fix . && uv run mypy src/ && uv run pytest tests/ --ignore=tests/perf -q
```

---

## Hard Limits

Enforced by `tests/architecture/test_file_limits.py`:

| Metric | Hard Limit | Preferred |
|---|---|---|
| Lines per file (code, excl. comments/docstrings) | **250** | 180 |
| Lines per function (body, excl. docstring) | **15** | 10 |
| Lines per class | **250** | 150 |
| Parameters per function | **4** | 3 |
| Indentation levels | **2** | 1 |
| Public methods per class | 10 | 5-7 |
| Instance attributes | 5 | 3-4 |
| Cyclomatic complexity | 10 | 5 |

---

## Python Version

**Python 3.11+** required. Use modern syntax:

```python
from __future__ import annotations  # Required in all files

X | None          # Not Optional[X]
list[str]         # Not List[str]
dict[str, int]    # Not Dict[str, int]
tuple[int, str]   # Not Tuple[int, str]
```

---

## Type Hints

### Required for All Public APIs

```python
def apply_filters(
    self,
    query: object,
    filters: Sequence[FilterSpec],
) -> object: ...
```

### Use Protocols, Not Base Classes

```python
# GOOD -- structural typing
class PaginationBackend(Protocol[T]):
    async def count(self, query: object) -> int: ...

# BAD -- inheritance coupling
class BasePaginationBackend(ABC):
    @abstractmethod
    async def count(self, query: object) -> int: ...
```

### TYPE_CHECKING for Import-Only Types

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
```

---

## Class Conventions

### `__slots__` on Every Class

Every class with instance attributes **must** have `__slots__`:

```python
class SQLAlchemyBackend(Generic[ItemT]):
    __slots__ = ("_count_query", "_session", "_unique")

    def __init__(self, session: AsyncSession, ...) -> None:
        self._session = session
```

Stateless classes use empty slots:

```python
class SQLAlchemySearchBackend:
    __slots__ = ()
```

### No Boolean Parameters

Use enums or separate methods:

```python
# BAD
def paginate(source, params, clamp: bool = False): ...

# GOOD
class OverflowStrategy(Enum):
    CLAMP = auto()
    EMPTY = auto()

def paginate(source, params, *, overflow: OverflowStrategy = OverflowStrategy.EMPTY): ...
```

---

## Function Conventions

### Guard Clauses (No Deep Nesting)

```python
# BAD -- deep nesting
def process(data):
    if data:
        if data.get("valid"):
            if data.get("type") == "order":
                return Result(...)
    return None

# GOOD -- guard clauses
def process(data):
    if not data:
        return None
    if not data.get("valid"):
        return None
    if data.get("type") != "order":
        return None
    return Result(...)
```

### Verb Prefixes

| Prefix | Returns | Example |
|---|---|---|
| `get_*` | Value or raises | `get_user(id)` |
| `find_*` | Value or None | `find_user_by_email(email)` |
| `create_*` | New object | `create_default_registry()` |
| `compile_*` | Reusable callable | `compile_accessor("user.name")` |
| `apply_*` | Transformed input | `apply_filters(query, specs)` |
| `build_*` | Constructed object | `build_sort_key(field, dir, nulls)` |
| `is_*` / `has_*` | bool | `is_active()`, `has_items()` |

---

## Naming

| Element | Convention | Example |
|---|---|---|
| Files | `snake_case.py` | `filter_engine.py` |
| Classes | `PascalCase` | `SQLAlchemyBackend` |
| Functions | `snake_case` + verb | `apply_filters()` |
| Constants | `UPPER_SNAKE` | `MAX_LIMIT` |
| Private | `_leading_underscore` | `self._session` |
| Type vars | Single uppercase or `*T` | `T`, `ItemT` |

---

## Imports

### Order

```python
from __future__ import annotations          # 1. Future annotations

import functools                            # 2. Stdlib
from collections.abc import Callable

from pypaginate.domain.enums import FilterLogic  # 3. Local
```

### No Circular Imports

Use `TYPE_CHECKING` guard for type-only imports:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pypaginate.domain.specs import FilterSpec
```

---

## Docstrings (Google Style)

```python
def apply_filters(
    self,
    query: object,
    filters: Sequence[FilterSpec],
) -> object:
    """Apply filter specs to a SQLAlchemy Select.

    Args:
        query: A SQLAlchemy Select statement.
        filters: Filter specifications to apply.

    Returns:
        Modified Select with WHERE clauses.

    Raises:
        FilterError: If the operator is unsupported.
    """
```

---

## Performance Patterns

### Compile-Once, Apply-N

```python
# BAD -- per-item work
for item in items:
    segments = field_path.split(".")
    for seg in segments: ...

# GOOD -- compile once
accessor = compile_accessor(field_path)
for item in items:
    value = accessor(item)
```

### LRU Cache for Pure Functions

```python
@functools.lru_cache(maxsize=8192)
def normalize_text(value: str) -> str: ...
```

### Optional Dependencies

```python
try:
    from rapidfuzz import fuzz as _fuzz
    _HAS_RAPIDFUZZ = True
except ImportError:  # pragma: no cover
    _HAS_RAPIDFUZZ = False  # pragma: no cover
```

### String Methods Over Regex

For simple patterns, use string methods (2-10x faster than regex/fnmatch).
