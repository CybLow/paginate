# Exceptions Module

The exceptions module provides error classes for pagination-related errors.

## Base Exception

::: pypaginator.exceptions.PaginationError
    options:
      show_source: true

## Configuration Errors

::: pypaginator.exceptions.PaginationConfigurationError
    options:
      show_source: true

## Validation Errors

::: pypaginator.exceptions.InvalidPageError
    options:
      show_source: true

::: pypaginator.exceptions.InvalidLimitError
    options:
      show_source: true

## Filter Errors

::: pypaginator.exceptions.FilterError
    options:
      show_source: true

::: pypaginator.exceptions.InvalidOperatorError
    options:
      show_source: true

::: pypaginator.exceptions.InvalidFieldError
    options:
      show_source: true

## Search Errors

::: pypaginator.exceptions.SearchError
    options:
      show_source: true

## Usage Examples

### Catching Pagination Errors

```python
from pypaginator.exceptions import (
    PaginationError,
    PaginationConfigurationError,
    InvalidPageError,
)

try:
    page = await paginate_entities_to_page(session, stmt, params)
except InvalidPageError as e:
    # Handle invalid page number
    print(f"Invalid page: {e}")
except PaginationConfigurationError as e:
    # Handle configuration issues
    print(f"Config error: {e}")
except PaginationError as e:
    # Catch all pagination errors
    print(f"Pagination error: {e}")
```

### FastAPI Error Handlers

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pypaginator.exceptions import (
    PaginationError,
    InvalidPageError,
    InvalidLimitError,
)

app = FastAPI()

@app.exception_handler(InvalidPageError)
async def invalid_page_handler(request: Request, exc: InvalidPageError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "invalid_page",
            "message": str(exc),
        },
    )

@app.exception_handler(InvalidLimitError)
async def invalid_limit_handler(request: Request, exc: InvalidLimitError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "invalid_limit",
            "message": str(exc),
        },
    )

@app.exception_handler(PaginationError)
async def pagination_error_handler(request: Request, exc: PaginationError):
    return JSONResponse(
        status_code=500,
        content={
            "error": "pagination_error",
            "message": str(exc),
        },
    )
```

### Filter Error Handling

```python
from pypaginator.exceptions import (
    FilterError,
    InvalidOperatorError,
    InvalidFieldError,
)

try:
    conditions = engine.build_conditions(User, filters)
except InvalidOperatorError as e:
    print(f"Unknown operator: {e}")
except InvalidFieldError as e:
    print(f"Invalid field: {e}")
except FilterError as e:
    print(f"Filter error: {e}")
```

### Custom Exception Details

```python
from pypaginator.exceptions import PaginationConfigurationError

# Exceptions may include additional details
try:
    strategy = get_pagination_strategy("unknown")
except PaginationConfigurationError as e:
    print(f"Error: {e}")
    # Access error details if available
    if hasattr(e, 'details'):
        print(f"Details: {e.details}")
```

## Exception Hierarchy

```
PaginationError (base)
├── PaginationConfigurationError
├── InvalidPageError
├── InvalidLimitError
├── FilterError
│   ├── InvalidOperatorError
│   └── InvalidFieldError
└── SearchError
```

## Best Practices

1. **Catch specific exceptions** before general ones
2. **Log errors** for debugging
3. **Return appropriate HTTP status codes** in APIs
4. **Include helpful error messages** for API consumers
5. **Don't expose internal details** in production error responses
