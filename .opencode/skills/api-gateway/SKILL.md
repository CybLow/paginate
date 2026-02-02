---
name: api-gateway
description: >
  API Gateway patterns and HTTP caching. Covers gateway responsibilities, Backend for Frontend (BFF),
  request aggregation, Cache-Control headers, ETags, conditional requests, and caching strategies.
related:
  - api-rest
  - api-auth
  - arch-microservices
  - perf-core
---

## API GATEWAY PATTERNS

Centralize cross-cutting concerns for microservices.

---

### Gateway Responsibilities

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway                               │
├─────────────────────────────────────────────────────────────────┤
│  - Authentication & Authorization                                │
│  - Rate Limiting                                                 │
│  - Request/Response Transformation                               │
│  - Load Balancing                                                │
│  - Circuit Breaking                                              │
│  - Caching                                                       │
│  - Logging & Monitoring                                          │
│  - API Versioning                                                │
└─────────────────────────────────────────────────────────────────┘
           │              │              │
           ▼              ▼              ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │  User    │   │  Order   │   │  Payment │
    │  Service │   │  Service │   │  Service │
    └──────────┘   └──────────┘   └──────────┘
```

### Backend for Frontend (BFF)

```python
# bff/mobile_api.py
"""BFF for mobile clients - aggregates and transforms data."""

from fastapi import APIRouter

router = APIRouter(prefix="/mobile/v1")


@router.get("/home")
async def get_home_screen(
    user_id: int,
    user_client: UserClient = Depends(),
    order_client: OrderClient = Depends(),
    recommendation_client: RecommendationClient = Depends(),
) -> MobileHomeResponse:
    """Aggregate data for mobile home screen in single request."""
    # Parallel requests to backend services
    user, recent_orders, recommendations = await asyncio.gather(
        user_client.get_user(user_id),
        order_client.get_recent(user_id, limit=3),
        recommendation_client.get_for_user(user_id, limit=5),
    )
    
    # Transform for mobile-specific needs
    return MobileHomeResponse(
        user=MobileUserSummary(
            name=user.name,
            avatar_url=user.avatar_url,
            loyalty_points=user.loyalty_points,
        ),
        recent_orders=[
            MobileOrderSummary(
                id=o.id,
                status_icon=get_status_icon(o.status),
                summary=f"{len(o.items)} items - ${o.total}",
            )
            for o in recent_orders
        ],
        recommendations=[
            MobileProductCard(
                id=r.id,
                image_url=r.thumbnail_url,
                name=r.name,
                price=format_price(r.price),
            )
            for r in recommendations
        ],
    )
```

### Request Aggregation

```python
async def aggregate_product_page(product_id: int) -> ProductPageResponse:
    """Aggregate data from multiple services for product page."""
    product, reviews, related, inventory = await asyncio.gather(
        product_service.get(product_id),
        review_service.get_for_product(product_id, limit=10),
        recommendation_service.get_related(product_id, limit=6),
        inventory_service.get_availability(product_id),
        return_exceptions=True,  # Don't fail if one service fails
    )
    
    # Handle partial failures gracefully
    return ProductPageResponse(
        product=product if not isinstance(product, Exception) else None,
        reviews=reviews if not isinstance(reviews, Exception) else [],
        related=related if not isinstance(related, Exception) else [],
        in_stock=inventory.available if not isinstance(inventory, Exception) else None,
    )
```

---

## HTTP CACHING

Reduce load and improve performance with proper caching headers.

---

### Cache-Control Headers

```python
from fastapi import Response
from datetime import datetime


@app.get("/products/{product_id}")
async def get_product(product_id: int, response: Response) -> Product:
    """Get product with caching headers."""
    product = await product_service.get(product_id)
    
    # Public caching for 5 minutes
    response.headers["Cache-Control"] = "public, max-age=300"
    
    return product


@app.get("/users/me")
async def get_current_user(
    response: Response,
    user: User = Depends(get_current_user),
) -> User:
    """User-specific data - private cache only."""
    response.headers["Cache-Control"] = "private, max-age=60"
    return user


@app.get("/config")
async def get_config(response: Response) -> Config:
    """Immutable config - cache forever."""
    response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return await config_service.get()


@app.post("/orders")
async def create_order(response: Response) -> Order:
    """Mutations should not be cached."""
    response.headers["Cache-Control"] = "no-store"
    return await order_service.create()
```

### ETags for Conditional Requests

```python
import hashlib
from fastapi import Header, HTTPException


def generate_etag(data: dict) -> str:
    """Generate ETag from response data."""
    content = json.dumps(data, sort_keys=True).encode()
    return f'"{hashlib.md5(content).hexdigest()}"'


@app.get("/products/{product_id}")
async def get_product(
    product_id: int,
    response: Response,
    if_none_match: str | None = Header(None),
) -> Product:
    product = await product_service.get(product_id)
    etag = generate_etag(product.model_dump())
    
    # Check if client has current version
    if if_none_match == etag:
        raise HTTPException(status_code=304)  # Not Modified
    
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "public, max-age=0, must-revalidate"
    return product


@app.put("/products/{product_id}")
async def update_product(
    product_id: int,
    data: ProductUpdate,
    if_match: str | None = Header(None),
) -> Product:
    """Optimistic concurrency with ETags."""
    product = await product_service.get(product_id)
    current_etag = generate_etag(product.model_dump())
    
    # Require ETag for updates (prevent lost updates)
    if if_match is None:
        raise HTTPException(428, "If-Match header required")
    
    if if_match != current_etag:
        raise HTTPException(412, "Precondition Failed - resource modified")
    
    return await product_service.update(product_id, data)
```

### Cache-Control Directives

| Directive | Meaning |
|-----------|---------|
| `public` | Can be cached by any cache |
| `private` | Only browser cache, not CDN |
| `no-cache` | Must revalidate before using |
| `no-store` | Don't cache at all |
| `max-age=N` | Cache for N seconds |
| `s-maxage=N` | CDN cache time (overrides max-age) |
| `must-revalidate` | Must check if stale |
| `immutable` | Never changes |

---

## CACHING STRATEGIES

### Cache Patterns

```python
# Cache-Aside (Lazy Loading)
async def get_user(user_id: int) -> User:
    # Check cache first
    cached = await cache.get(f"user:{user_id}")
    if cached:
        return cached
    
    # Load from database
    user = await db.get_user(user_id)
    
    # Store in cache
    await cache.set(f"user:{user_id}", user, ttl=300)
    return user


# Write-Through
async def update_user(user_id: int, data: UserUpdate) -> User:
    # Update database
    user = await db.update_user(user_id, data)
    
    # Update cache immediately
    await cache.set(f"user:{user_id}", user, ttl=300)
    return user


# Write-Behind (Async)
async def update_user(user_id: int, data: UserUpdate) -> User:
    # Update cache immediately
    user = User(**data.model_dump())
    await cache.set(f"user:{user_id}", user, ttl=300)
    
    # Queue database update
    await queue.publish("user.update", {"id": user_id, "data": data})
    return user
```

### Cache Invalidation

```python
class CacheInvalidator:
    """Invalidate related cache entries."""
    
    async def invalidate_user(self, user_id: int) -> None:
        await asyncio.gather(
            self.cache.delete(f"user:{user_id}"),
            self.cache.delete(f"user_orders:{user_id}"),
            self.cache.delete(f"user_profile:{user_id}"),
        )
    
    async def invalidate_order(self, order_id: int, user_id: int) -> None:
        await asyncio.gather(
            self.cache.delete(f"order:{order_id}"),
            self.cache.delete(f"user_orders:{user_id}"),
            self.cache.delete("recent_orders"),
        )
```

---

## QUICK REFERENCE

### Caching Decision Matrix

| Resource Type | Cache-Control | TTL |
|---------------|---------------|-----|
| Static assets | public, immutable | 1 year |
| API responses (public) | public, max-age | 5 min |
| User-specific data | private, max-age | 1 min |
| Mutations | no-store | N/A |
| Frequently changing | no-cache, must-revalidate | N/A |

### Gateway vs Direct Access

| Use Gateway | Use Direct Access |
|-------------|-------------------|
| Public APIs | Internal services |
| Need auth/rate limiting | Trusted clients |
| Multiple clients | Single consumer |
| Complex routing | Simple topology |
