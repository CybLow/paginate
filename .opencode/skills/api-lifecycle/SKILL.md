---
name: api-lifecycle
description: >
  API lifecycle management. Covers deprecation strategies, versioning changes,
  migration guides, HATEOAS principles, and JSON:API format.
related:
  - api-rest
  - api-gateway
  - arch-principles
---

## API LIFECYCLE MANAGEMENT

Manage API evolution over time.

---

### Deprecation Strategy

```python
from fastapi import APIRouter, Header
from datetime import date
import warnings


def deprecated(
    sunset_date: date,
    replacement: str | None = None,
    message: str | None = None,
):
    """Mark endpoint as deprecated."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, response: Response, **kwargs):
            # Add deprecation headers
            response.headers["Deprecation"] = "true"
            response.headers["Sunset"] = sunset_date.isoformat()
            
            if replacement:
                response.headers["Link"] = f'<{replacement}>; rel="successor-version"'
            
            # Log usage of deprecated endpoint
            logger.warning(
                "deprecated_endpoint_called",
                endpoint=func.__name__,
                sunset=sunset_date.isoformat(),
            )
            
            return await func(*args, response=response, **kwargs)
        return wrapper
    return decorator


router_v1 = APIRouter(prefix="/api/v1")


@router_v1.get("/users")
@deprecated(
    sunset_date=date(2024, 6, 1),
    replacement="/api/v2/users",
    message="Use v2 API for improved pagination",
)
async def get_users_v1(response: Response):
    """DEPRECATED: Use /api/v2/users instead."""
    return await user_service.list_v1()


router_v2 = APIRouter(prefix="/api/v2")


@router_v2.get("/users")
async def get_users_v2():
    """Current version with cursor pagination."""
    return await user_service.list_v2()
```

### Breaking vs Non-Breaking Changes

| Non-Breaking (Safe) | Breaking (Major Version) |
|---------------------|-------------------------|
| Add new endpoints | Remove endpoints |
| Add optional fields | Remove fields |
| Add new enum values | Change field types |
| Relax validation | Tighten validation |
| Add optional parameters | Remove parameters |
| Extend response | Change response structure |

### Version Migration Guide

```python
# docs/migration/v1-to-v2.md
"""
# Migration Guide: v1 to v2

## Timeline
- v2 Released: 2024-01-01
- v1 Deprecated: 2024-03-01
- v1 Sunset: 2024-06-01

## Breaking Changes

### 1. Pagination
v1: Offset pagination
```json
{"page": 1, "per_page": 20}
```

v2: Cursor pagination
```json
{"cursor": "abc123", "limit": 20}
```

### 2. User Response
v1:
```json
{"id": 1, "name": "John", "email": "john@example.com"}
```

v2:
```json
{
  "data": {"id": 1, "name": "John", "email": "john@example.com"},
  "meta": {"version": "2.0"}
}
```

## Migration Steps
1. Update client library to v2
2. Change pagination logic to use cursors
3. Update response parsing for wrapped format
4. Test thoroughly before v1 sunset
"""
```

---

## HATEOAS (Hypermedia)

Self-documenting APIs with navigation links.

---

### Link Structure

```python
from pydantic import BaseModel


class Link(BaseModel):
    href: str
    rel: str
    method: str = "GET"


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    _links: dict[str, Link]


def build_user_response(user: User, request: Request) -> UserResponse:
    base_url = str(request.base_url)
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        _links={
            "self": Link(
                href=f"{base_url}users/{user.id}",
                rel="self",
            ),
            "orders": Link(
                href=f"{base_url}users/{user.id}/orders",
                rel="orders",
            ),
            "update": Link(
                href=f"{base_url}users/{user.id}",
                rel="update",
                method="PUT",
            ),
            "delete": Link(
                href=f"{base_url}users/{user.id}",
                rel="delete",
                method="DELETE",
            ),
        },
    )


class PaginatedResponse(BaseModel):
    data: list[UserResponse]
    _links: dict[str, Link]


def build_paginated_response(
    users: list[User],
    request: Request,
    page: int,
    total_pages: int,
) -> PaginatedResponse:
    base_url = str(request.url).split("?")[0]
    links = {
        "self": Link(href=f"{base_url}?page={page}", rel="self"),
    }
    
    if page > 1:
        links["prev"] = Link(href=f"{base_url}?page={page-1}", rel="prev")
        links["first"] = Link(href=f"{base_url}?page=1", rel="first")
    
    if page < total_pages:
        links["next"] = Link(href=f"{base_url}?page={page+1}", rel="next")
        links["last"] = Link(href=f"{base_url}?page={total_pages}", rel="last")
    
    return PaginatedResponse(
        data=[build_user_response(u, request) for u in users],
        _links=links,
    )
```

### JSON:API Format

```python
class JsonApiResponse(BaseModel):
    """JSON:API compliant response format."""
    
    data: dict | list[dict]
    included: list[dict] | None = None
    links: dict[str, str] | None = None
    meta: dict | None = None


def to_json_api(user: User, include_orders: bool = False) -> JsonApiResponse:
    data = {
        "type": "users",
        "id": str(user.id),
        "attributes": {
            "name": user.name,
            "email": user.email,
        },
        "relationships": {
            "orders": {
                "links": {
                    "related": f"/users/{user.id}/orders",
                },
            },
        },
        "links": {
            "self": f"/users/{user.id}",
        },
    }
    
    included = []
    if include_orders:
        for order in user.orders:
            included.append({
                "type": "orders",
                "id": str(order.id),
                "attributes": {
                    "total": float(order.total),
                    "status": order.status,
                },
            })
    
    return JsonApiResponse(
        data=data,
        included=included if included else None,
    )
```

---

## VERSIONING STRATEGIES

### Comparison

| Strategy | Pros | Cons |
|----------|------|------|
| URL path (`/v1/`) | Clear, cacheable | URL pollution |
| Query param (`?v=1`) | Easy to implement | Less visible |
| Header (`Accept-Version`) | Clean URLs | Hidden, harder to debug |
| Content-Type | Standards-based | Complex |

### Implementation Pattern

```python
from fastapi import APIRouter, Request
from enum import Enum


class APIVersion(str, Enum):
    V1 = "v1"
    V2 = "v2"


def create_versioned_router(version: APIVersion) -> APIRouter:
    return APIRouter(prefix=f"/api/{version.value}")


# Version-specific implementations
router_v1 = create_versioned_router(APIVersion.V1)
router_v2 = create_versioned_router(APIVersion.V2)


# Shared logic with version dispatch
async def get_users(version: APIVersion, **kwargs):
    if version == APIVersion.V1:
        return await user_service.list_v1(**kwargs)
    return await user_service.list_v2(**kwargs)
```

---

## QUICK REFERENCE

### API Lifecycle Stages

| Stage | Duration | Actions |
|-------|----------|---------|
| Active | Ongoing | Full support |
| Deprecated | 3-6 months | Add headers, log usage |
| Sunset | 1-3 months | Return warnings |
| Removed | - | Return 410 Gone |

### Deprecation Headers

| Header | Purpose | Example |
|--------|---------|---------|
| `Deprecation` | Mark as deprecated | `true` |
| `Sunset` | Removal date | `2024-06-01` |
| `Link` | Successor version | `</v2/users>; rel="successor-version"` |

### Design Checklist

```
Planning:
[ ] Version strategy defined
[ ] Deprecation policy documented
[ ] Migration guide template ready

Implementation:
[ ] Deprecation decorator/middleware
[ ] Usage logging for deprecated endpoints
[ ] Sunset date tracking

Communication:
[ ] Changelog maintained
[ ] Breaking changes announced
[ ] Migration guides published
```
