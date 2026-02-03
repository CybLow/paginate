# Integrations Module

The integrations module provides framework-specific utilities for FastAPI and other frameworks.

## FastAPI Integration

### PagedResponse

Pydantic model for paginated API responses. Generic over the item type.

```{eval-rst}
.. autoclass:: pypaginate.integrations.fastapi.PagedResponse
   :members:
   :show-inheritance:
```

### get_pagination_params

FastAPI dependency for extracting pagination parameters from query strings.

```{eval-rst}
.. autofunction:: pypaginate.integrations.fastapi.get_pagination_params
```

## Usage Examples

### Basic FastAPI Integration

```python
from fastapi import Depends, FastAPI
from pypaginate.integrations.fastapi import get_pagination_params, PagedResponse
from pypaginate.core import PageParams
from pypaginate.query import paginate_entities_to_page

app = FastAPI()

@app.get("/users", response_model=PagedResponse[UserSchema])
async def list_users(
    session: AsyncSession = Depends(get_session),
    params: PageParams = Depends(get_pagination_params),
):
    stmt = select(User).order_by(User.id)
    page = await paginate_entities_to_page(session, stmt, params)
    return PagedResponse.from_page(page)
```

### Custom Pagination Parameters

```python
from fastapi import Query
from pypaginate.core import PageParams

def get_custom_pagination(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=200, description="Items per page"),
) -> PageParams:
    return PageParams(page=page, limit=per_page)

@app.get("/products")
async def list_products(
    params: PageParams = Depends(get_custom_pagination),
):
    ...
```

### PagedResponse Fields

The `PagedResponse` model includes:

| Field | Type | Description |
|-------|------|-------------|
| `items` | list[T] | Items in current page |
| `total` | int | Total item count |
| `page` | int | Current page number |
| `limit` | int | Items per page |

### Converting from Page

```python
from pypaginate.integrations.fastapi import PagedResponse
from pypaginate.core import Page

# From a Page object
page: Page[User] = await paginate_entities_to_page(session, stmt, params)
response = PagedResponse.from_page(page)

# Response JSON:
# {
#     "items": [...],
#     "total": 100,
#     "page": 1,
#     "limit": 20
# }
```

### With Search and Filtering

```python
from pypaginate.filters.search import SqlSearchService
from pypaginate.sorting import SqlSortAdapter

@app.get("/products", response_model=PagedResponse[ProductSchema])
async def list_products(
    session: AsyncSession = Depends(get_session),
    params: PageParams = Depends(get_pagination_params),
    search: str | None = Query(None),
    category: str | None = Query(None),
    sort_by: str = Query("created_at"),
    order: str = Query("desc"),
):
    stmt = select(Product)
    
    # Apply search
    if search:
        search_service = SqlSearchService(Product, ["name", "description"])
        stmt = search_service.apply_search(stmt, search)
    
    # Apply filter
    if category:
        stmt = stmt.where(Product.category == category)
    
    # Apply sorting
    column = getattr(Product, sort_by)
    stmt = stmt.order_by(
        SqlSortAdapter.build_order_expression(column, order == "desc")
    )
    
    page = await paginate_entities_to_page(session, stmt, params)
    return PagedResponse.from_page(page)
```

### OpenAPI Schema

The integration automatically generates proper OpenAPI schemas:

```yaml
# Generated OpenAPI for PagedResponse[UserSchema]
PagedResponse_UserSchema_:
  type: object
  properties:
    items:
      type: array
      items:
        $ref: '#/components/schemas/UserSchema'
    total:
      type: integer
    page:
      type: integer
    limit:
      type: integer
```

## Installation

FastAPI integration requires additional dependencies:

::::{tab-set}

:::{tab-item} uv (recommended)
```bash
uv add pypaginate[fastapi]
```
:::

:::{tab-item} pip
```bash
pip install pypaginate[fastapi]
```
:::

::::

This installs:
- `fastapi`
- `pydantic`
