---
name: api-rest
description: >
  RESTful API design conventions. Covers resource-oriented URLs, HTTP methods, status codes,
  response formats, pagination (offset vs cursor), filtering, sorting, versioning strategies,
  and error response structure. Foundation for REST API development.
related:
  - api-graphql
  - api-grpc
  - api-auth
  - api-gateway
  - api-lifecycle
---

## REST API DESIGN

APIs are contracts. Design for clarity, consistency, and extensibility.

---

### RESTful Conventions

**Resource-oriented URLs:**
```
# Resources are nouns, not verbs
GET    /users              # List users
POST   /users              # Create user
GET    /users/{id}         # Get user
PUT    /users/{id}         # Replace user
PATCH  /users/{id}         # Partial update
DELETE /users/{id}         # Delete user

# Nested resources for relationships
GET    /users/{id}/orders  # List user's orders
POST   /users/{id}/orders  # Create order for user

# Actions as sub-resources (when needed)
POST   /orders/{id}/cancel     # Cancel order
POST   /orders/{id}/ship       # Ship order
```

**HTTP methods semantics:**

| Method | Purpose | Idempotent | Safe |
|--------|---------|------------|------|
| GET | Read | Yes | Yes |
| POST | Create | No | No |
| PUT | Replace | Yes | No |
| PATCH | Update | Yes | No |
| DELETE | Remove | Yes | No |

**HTTP status codes:**

| Code | Meaning | When to Use |
|------|---------|-------------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Missing/invalid auth |
| 403 | Forbidden | Authenticated but not allowed |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | State conflict (duplicate, etc.) |
| 422 | Unprocessable | Validation failed |
| 500 | Server Error | Unexpected failure |

---

### Response Format Standards

**Consistent structure:**
```json
// Success response
{
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  }
}

// Collection response
{
  "data": [
    {"id": 1, "name": "John"},
    {"id": 2, "name": "Jane"}
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5
  }
}

// Error response
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {"field": "email", "message": "Invalid email format"},
      {"field": "password", "message": "Must be at least 8 characters"}
    ]
  }
}
```

**Python implementation:**
```python
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")

@dataclass
class ApiResponse(Generic[T]):
    data: T
    meta: dict | None = None

@dataclass
class PaginatedResponse(Generic[T]):
    data: list[T]
    pagination: PaginationMeta

@dataclass
class PaginationMeta:
    page: int
    per_page: int
    total: int
    total_pages: int

@dataclass
class ErrorResponse:
    error: ErrorDetail

@dataclass
class ErrorDetail:
    code: str
    message: str
    details: list[FieldError] | None = None

@dataclass
class FieldError:
    field: str
    message: str
```

---

### Pagination Patterns

**Offset-based pagination (simple, familiar):**
```
GET /users?page=2&per_page=20
```

```python
@dataclass
class PageParams:
    page: int = 1
    per_page: int = 20

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("Page must be >= 1")
        if self.per_page < 1 or self.per_page > 100:
            raise ValueError("per_page must be 1-100")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page

    @property
    def limit(self) -> int:
        return self.per_page
```

**Cursor-based pagination (scalable, consistent):**
```
GET /users?cursor=eyJpZCI6MTAwfQ&limit=20
```

```python
import base64
import json

@dataclass
class CursorParams:
    cursor: str | None = None
    limit: int = 20

    def decode_cursor(self) -> dict | None:
        if self.cursor is None:
            return None
        try:
            decoded = base64.urlsafe_b64decode(self.cursor)
            return json.loads(decoded)
        except Exception:
            raise ValueError("Invalid cursor")

    @staticmethod
    def encode_cursor(data: dict) -> str:
        json_bytes = json.dumps(data).encode()
        return base64.urlsafe_b64encode(json_bytes).decode()
```

**When to use which:**

| Offset Pagination | Cursor Pagination |
|-------------------|-------------------|
| Small datasets | Large datasets |
| Need to jump to page | Sequential navigation |
| Total count needed | Consistency important |
| Infrequent updates | Frequent updates |

---

### Filtering & Sorting

**Filter parameters:**
```
GET /products?status=active&category=electronics&price_min=100&price_max=1000
GET /users?created_after=2024-01-01&role=admin
```

```python
@dataclass
class ProductFilters:
    status: str | None = None
    category: str | None = None
    price_min: float | None = None
    price_max: float | None = None

    def to_query_conditions(self) -> list[Condition]:
        conditions = []
        if self.status:
            conditions.append(Product.status == self.status)
        if self.category:
            conditions.append(Product.category == self.category)
        if self.price_min is not None:
            conditions.append(Product.price >= self.price_min)
        if self.price_max is not None:
            conditions.append(Product.price <= self.price_max)
        return conditions
```

**Sort parameters:**
```
GET /products?sort=price        # Ascending by price
GET /products?sort=-price       # Descending by price
GET /products?sort=category,-created_at  # Multiple fields
```

```python
@dataclass
class SortParam:
    field: str
    descending: bool = False

    @classmethod
    def parse(cls, value: str) -> SortParam:
        if value.startswith("-"):
            return cls(field=value[1:], descending=True)
        return cls(field=value, descending=False)

    @classmethod
    def parse_list(cls, value: str) -> list[SortParam]:
        return [cls.parse(v.strip()) for v in value.split(",")]
```

---

### Versioning Strategy

**URL versioning (recommended):**
```
/api/v1/users
/api/v2/users
```

```python
from fastapi import APIRouter

router_v1 = APIRouter(prefix="/api/v1")
router_v2 = APIRouter(prefix="/api/v2")

@router_v1.get("/users")
async def get_users_v1() -> list[UserV1]:
    ...

@router_v2.get("/users")
async def get_users_v2() -> list[UserV2]:
    ...
```

**Header versioning (alternative):**
```
GET /users
Accept: application/vnd.myapi.v2+json
```

**Versioning guidelines:**
1. Start with v1 from day one
2. Increment major version for breaking changes
3. Support at least 2 versions simultaneously
4. Provide migration path and timeline
5. Document breaking changes clearly

---

### Error Response Structure

**Consistent error format:**
```python
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

class ApiError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: list[dict] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


class ValidationError(ApiError):
    def __init__(self, details: list[dict]) -> None:
        super().__init__(
            code="VALIDATION_ERROR",
            message="Invalid input data",
            status_code=422,
            details=details,
        )


class NotFoundError(ApiError):
    def __init__(self, resource: str, id: Any) -> None:
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} with id '{id}' not found",
            status_code=404,
        )


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )
```

---

### API Documentation

**OpenAPI/Swagger with FastAPI:**
```python
from fastapi import FastAPI, Query, Path
from pydantic import BaseModel, Field

app = FastAPI(
    title="My API",
    description="API for managing users and orders",
    version="1.0.0",
)

class User(BaseModel):
    """User account information."""

    id: int = Field(description="Unique user identifier")
    name: str = Field(description="Full name", min_length=1, max_length=100)
    email: str = Field(description="Email address")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
            }
        }
    }


@app.get(
    "/users/{user_id}",
    response_model=User,
    summary="Get user by ID",
    description="Retrieve a single user by their unique identifier.",
    responses={
        404: {"description": "User not found"},
    },
)
async def get_user(
    user_id: int = Path(description="The unique user ID", ge=1),
) -> User:
    """
    Get a user by ID.

    - **user_id**: Unique identifier of the user
    """
    ...
```

---

### API Design Checklist

**Before releasing an API:**
- [ ] Consistent naming (plural nouns, kebab-case)
- [ ] Proper HTTP methods
- [ ] Meaningful status codes
- [ ] Consistent response format
- [ ] Pagination for lists
- [ ] Filtering and sorting
- [ ] Versioning strategy
- [ ] Error handling with codes
- [ ] Documentation (OpenAPI)
- [ ] Rate limiting
- [ ] Authentication
- [ ] CORS configuration

---

## QUICK REFERENCE

### HTTP Status Codes

| Code | Name | When to Use |
|------|------|-------------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST creating resource |
| 204 | No Content | Successful DELETE |
| 304 | Not Modified | Cache valid (ETag match) |
| 400 | Bad Request | Malformed request |
| 401 | Unauthorized | Missing/invalid authentication |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | State conflict |
| 412 | Precondition Failed | ETag mismatch |
| 422 | Unprocessable Entity | Validation failed |
| 428 | Precondition Required | Missing required header |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |
