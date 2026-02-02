---
name: api-graphql
description: >
  GraphQL API design with Strawberry. Covers when to use GraphQL vs REST, schema definition,
  queries, mutations, DataLoaders for N+1 prevention, input validation, and error handling.
related:
  - api-rest
  - api-grpc
  - api-auth
  - perf-database
---

## GRAPHQL

GraphQL provides a flexible query language for APIs. Use when clients have varying data needs.

---

### When to Use GraphQL vs REST

| Use GraphQL When | Use REST When |
|------------------|---------------|
| Clients have diverse data needs | Simple CRUD operations |
| Mobile apps need minimal data | Caching is critical (HTTP caching) |
| Avoiding over/under-fetching | Simple, well-defined resources |
| Rapid frontend iteration | Wide ecosystem/tooling needed |
| Single request for related data | Team unfamiliar with GraphQL |

### Basic GraphQL with Strawberry

```python
# schema.py
import strawberry
from strawberry.fastapi import GraphQLRouter
from typing import Optional


@strawberry.type
class User:
    id: int
    name: str
    email: str
    
    @strawberry.field
    async def orders(self, info) -> list["Order"]:
        """Resolve orders for user (avoid N+1 with dataloaders)."""
        return await info.context.order_loader.load(self.id)


@strawberry.type
class Order:
    id: int
    total: float
    status: str
    user_id: int


@strawberry.type
class Query:
    @strawberry.field
    async def user(self, id: int) -> Optional[User]:
        """Get user by ID."""
        return await user_service.get(id)
    
    @strawberry.field
    async def users(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> list[User]:
        """List users with pagination."""
        return await user_service.list(limit=limit, offset=offset)


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(self, name: str, email: str) -> User:
        """Create a new user."""
        return await user_service.create(name=name, email=email)
    
    @strawberry.mutation
    async def update_user(
        self,
        id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> User:
        """Update existing user."""
        return await user_service.update(id, name=name, email=email)


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

# Mount in FastAPI
app.include_router(graphql_app, prefix="/graphql")
```

### DataLoaders (N+1 Prevention)

```python
from strawberry.dataloader import DataLoader


async def load_orders_by_user(user_ids: list[int]) -> list[list[Order]]:
    """Batch load orders for multiple users."""
    orders = await order_repository.find_by_user_ids(user_ids)
    
    # Group by user_id
    orders_by_user = {uid: [] for uid in user_ids}
    for order in orders:
        orders_by_user[order.user_id].append(order)
    
    # Return in same order as input
    return [orders_by_user[uid] for uid in user_ids]


class GraphQLContext:
    def __init__(self, request):
        self.request = request
        self.order_loader = DataLoader(load_fn=load_orders_by_user)
        self.user_loader = DataLoader(load_fn=load_users)


async def get_context(request: Request) -> GraphQLContext:
    return GraphQLContext(request)


graphql_app = GraphQLRouter(schema, context_getter=get_context)
```

### GraphQL Input Validation

```python
import strawberry
from strawberry.types import Info


@strawberry.input
class CreateUserInput:
    name: str
    email: str
    password: str
    
    def validate(self) -> list[str]:
        errors = []
        if len(self.name) < 2:
            errors.append("Name must be at least 2 characters")
        if "@" not in self.email:
            errors.append("Invalid email format")
        if len(self.password) < 8:
            errors.append("Password must be at least 8 characters")
        return errors


@strawberry.type
class CreateUserResult:
    user: Optional[User] = None
    errors: list[str] = strawberry.field(default_factory=list)


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(self, input: CreateUserInput) -> CreateUserResult:
        errors = input.validate()
        if errors:
            return CreateUserResult(errors=errors)
        
        user = await user_service.create(
            name=input.name,
            email=input.email,
            password=input.password,
        )
        return CreateUserResult(user=user)
```

---

## BEST PRACTICES

### Schema Design

```python
# Use interfaces for shared fields
@strawberry.interface
class Node:
    id: strawberry.ID


@strawberry.type
class User(Node):
    name: str
    email: str


@strawberry.type
class Order(Node):
    total: float
    status: str
```

### Pagination with Connections

```python
@strawberry.type
class UserEdge:
    cursor: str
    node: User


@strawberry.type
class UserConnection:
    edges: list[UserEdge]
    page_info: PageInfo


@strawberry.type
class PageInfo:
    has_next_page: bool
    has_previous_page: bool
    start_cursor: str | None
    end_cursor: str | None


@strawberry.type
class Query:
    @strawberry.field
    async def users(
        self,
        first: int | None = None,
        after: str | None = None,
    ) -> UserConnection:
        """Cursor-based pagination for users."""
        return await user_service.list_connection(first=first, after=after)
```

### Error Handling

```python
@strawberry.type
class Error:
    message: str
    code: str


@strawberry.type
class CreateUserSuccess:
    user: User


CreateUserPayload = strawberry.union(
    "CreateUserPayload",
    [CreateUserSuccess, Error],
)


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(self, input: CreateUserInput) -> CreateUserPayload:
        try:
            user = await user_service.create(input)
            return CreateUserSuccess(user=user)
        except DuplicateEmailError:
            return Error(message="Email already exists", code="DUPLICATE_EMAIL")
```

---

## QUICK REFERENCE

### GraphQL vs REST Decision Matrix

| Scenario | Recommendation |
|----------|----------------|
| Public API | REST (better caching, tooling) |
| Mobile app | GraphQL (flexible queries) |
| Internal microservices | gRPC (performance) |
| Real-time updates | GraphQL subscriptions |
| File uploads | REST (multipart) |

### Common Patterns

```python
# Optional fields
@strawberry.type
class User:
    id: int
    name: str
    bio: str | None = None  # Optional

# Lists
@strawberry.type
class User:
    orders: list[Order] = strawberry.field(default_factory=list)

# Custom scalars
from datetime import datetime
from strawberry.scalars import JSON

@strawberry.type
class Event:
    created_at: datetime  # ISO 8601 string
    metadata: JSON        # Arbitrary JSON
```
