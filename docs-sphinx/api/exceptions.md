# Exceptions Module

The exceptions module provides error classes for pagination-related errors.

## Exception Hierarchy

```
PaginatorException (base)
├── PaginationConfigurationError
├── FilterException
│   └── FilterValidationError
├── SearchException
│   ├── SearchQueryError
│   └── SearchNormalizationError
├── SortException
└── ValidationException
```

## Base Exception

```{eval-rst}
.. autoexception:: pypaginate.exceptions.PaginatorException
   :members:
   :show-inheritance:
```

## Configuration Errors

Raised when pagination is misconfigured.

```{eval-rst}
.. autoexception:: pypaginate.exceptions.PaginationConfigurationError
   :members:
   :show-inheritance:
```

## Filter Errors

Raised during filter building or validation.

```{eval-rst}
.. autoexception:: pypaginate.exceptions.FilterException
   :members:
   :show-inheritance:
```

```{eval-rst}
.. autoexception:: pypaginate.exceptions.FilterValidationError
   :members:
   :show-inheritance:
```

## Search Errors

Raised during search operations.

```{eval-rst}
.. autoexception:: pypaginate.exceptions.SearchException
   :members:
   :show-inheritance:
```

```{eval-rst}
.. autoexception:: pypaginate.exceptions.SearchQueryError
   :members:
   :show-inheritance:
```

```{eval-rst}
.. autoexception:: pypaginate.exceptions.SearchNormalizationError
   :members:
   :show-inheritance:
```

## Sort Errors

Raised during sorting operations.

```{eval-rst}
.. autoexception:: pypaginate.exceptions.SortException
   :members:
   :show-inheritance:
```

## Validation Errors

Raised when input validation fails.

```{eval-rst}
.. autoexception:: pypaginate.exceptions.ValidationException
   :members:
   :show-inheritance:
```

## Usage Examples

### Catching Pagination Errors

```python
from pypaginate.exceptions import (
    PaginatorException,
    PaginationConfigurationError,
)

try:
    page = await paginate_entities_to_page(session, stmt, params)
except PaginationConfigurationError as e:
    # Handle configuration issues
    print(f"Config error: {e}")
    if e.details:
        print(f"Details: {e.details}")
except PaginatorException as e:
    # Catch all pagination errors
    print(f"Pagination error: {e}")
```

### FastAPI Error Handlers

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pypaginate.exceptions import (
    PaginatorException,
    PaginationConfigurationError,
    ValidationException,
)

app = FastAPI()

@app.exception_handler(ValidationException)
async def validation_error_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=400,
        content={
            "error": "validation_error",
            "field": exc.field,
            "message": str(exc),
        },
    )

@app.exception_handler(PaginationConfigurationError)
async def config_error_handler(request: Request, exc: PaginationConfigurationError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "configuration_error",
            "message": str(exc),
        },
    )

@app.exception_handler(PaginatorException)
async def pagination_error_handler(request: Request, exc: PaginatorException):
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
from pypaginate.exceptions import (
    FilterException,
    FilterValidationError,
)

try:
    conditions = engine.build_conditions(User, filters)
except FilterValidationError as e:
    print(f"Invalid filter: {e}")
    if e.details:
        print(f"Details: {e.details}")
except FilterException as e:
    print(f"Filter error: {e}")
```

### Search Error Handling

```python
from pypaginate.exceptions import (
    SearchException,
    SearchQueryError,
    SearchNormalizationError,
)

try:
    results = search_service.search(items, query)
except SearchQueryError as e:
    print(f"Invalid query: {e}")
except SearchNormalizationError as e:
    print(f"Normalization failed: {e}")
except SearchException as e:
    print(f"Search error: {e}")
```

### Custom Exception Details

```python
from pypaginate.exceptions import PaginationConfigurationError

# Exceptions may include additional details
try:
    strategy = get_pagination_strategy("unknown")
except PaginationConfigurationError as e:
    print(f"Error: {e}")
    print(f"Field: {e.field}")
    print(f"Value: {e.value}")
    print(f"Reason: {e.reason}")
    print(f"Details: {e.details}")
```

## Best Practices

1. **Catch specific exceptions** before general ones
2. **Log errors** for debugging
3. **Return appropriate HTTP status codes** in APIs
4. **Include helpful error messages** for API consumers
5. **Don't expose internal details** in production error responses
6. **Access exception attributes** (field, value, details) for richer error handling
