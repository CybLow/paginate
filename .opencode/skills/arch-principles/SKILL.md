---
name: arch-principles
description: >
  Core software architecture principles: layered architecture, dependency inversion,
  separation of concerns, dependency injection, error handling, async patterns,
  configuration management, observability (logging, health checks), and feature flags.
version: "2.0"
source: mixed
related:
  - arch-ddd
  - arch-hexagonal
  - arch-microservices
  - guru-patterns-creational
---

## SOFTWARE ARCHITECTURE PRINCIPLES

Architecture is about making decisions that are hard to change. Good architecture enables change where change is likely while protecting core business logic.

---

### Core Architectural Principles

#### 1. Layered Architecture

Organize code into distinct layers with clear responsibilities. Each layer has a specific purpose and dependency direction.

```
┌─────────────────────────────────────────────────┐
│           Presentation / Interface Layer        │  ← API, CLI, Web
│  (How users interact with the system)          │
├─────────────────────────────────────────────────┤
│              Application Layer                  │  ← Use cases, orchestration
│  (What the system does - workflows)            │
├─────────────────────────────────────────────────┤
│                Domain Layer                     │  ← Business logic, entities
│  (Core business rules - framework agnostic)    │
├─────────────────────────────────────────────────┤
│             Infrastructure Layer                │  ← Database, external APIs
│  (How the system connects to the outside)      │
└─────────────────────────────────────────────────┘
```

**Layer Responsibilities:**

| Layer | Responsibility | Changes When |
|-------|---------------|--------------|
| Presentation | Request/response handling, validation, serialization | UI/API requirements change |
| Application | Use case orchestration, transactions, authorization | Workflows change |
| Domain | Business rules, entities, domain events | Business rules change |
| Infrastructure | Persistence, external services, messaging | Technical details change |

**Layer Rules:**
1. Each layer only depends on layers **below** it
2. Domain layer has **no external dependencies**
3. Never import from upper layers
4. Use dependency injection to invert infrastructure dependencies

---

#### 2. Dependency Rule

> Source code dependencies must point **inward** toward higher-level policies.

The Dependency Rule ensures that changes in outer layers (infrastructure, presentation) don't affect inner layers (domain, application).

```python
# BAD: Domain depends on infrastructure
# domain/order.py
from sqlalchemy import Column, Integer  # Infrastructure leak!

class Order(Base):
    id = Column(Integer, primary_key=True)

# GOOD: Domain is pure, infrastructure adapts
# domain/order.py
@dataclass
class Order:
    id: int | None
    items: list[OrderItem]
    status: OrderStatus

# infrastructure/persistence/order_model.py
class OrderModel(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)

    def to_entity(self) -> Order:
        return Order(id=self.id, ...)

    @classmethod
    def from_entity(cls, order: Order) -> OrderModel:
        return cls(id=order.id, ...)
```

**Key insight**: Domain entities should be plain Python objects (dataclasses, attrs) that know nothing about how they're stored.

---

#### 3. Separation of Concerns

Each module should have a **single reason to change**. When concerns are mixed, changes ripple through the codebase unexpectedly.

**Signs of poor separation:**
- A file imports both HTTP frameworks and database libraries
- Business logic is mixed with persistence code
- Validation is scattered across multiple layers
- Tests require complex setup due to entangled dependencies

**Achieving separation:**
```python
# BAD: Mixed concerns
class OrderController:
    def create_order(self, request):
        # Validation (presentation concern)
        if not request.items:
            raise HTTPException(400, "Items required")
        
        # Business logic (domain concern)
        total = sum(item.price * item.quantity for item in request.items)
        if total > self.user.credit_limit:
            raise HTTPException(400, "Exceeds credit limit")
        
        # Persistence (infrastructure concern)
        db.session.add(Order(items=request.items, total=total))
        db.session.commit()

# GOOD: Separated concerns
class OrderController:  # Presentation
    def create_order(self, request: CreateOrderRequest) -> OrderResponse:
        order = self._order_service.create(request.to_command())
        return OrderResponse.from_entity(order)

class OrderService:  # Application
    def create(self, command: CreateOrderCommand) -> Order:
        order = Order.create(command.items)  # Domain
        self._repository.save(order)  # Infrastructure via abstraction
        return order

class Order:  # Domain
    @classmethod
    def create(cls, items: list[OrderItem]) -> Order:
        if not items:
            raise ValidationError("Items required")
        total = sum(item.price * item.quantity for item in items)
        return cls(items=items, total=total)
```

---

#### 4. Dependency Inversion Principle

> High-level modules should not depend on low-level modules. Both should depend on abstractions.

This principle allows you to swap implementations without changing business logic.

```python
from typing import Protocol

# Define abstraction in domain/application layer
class OrderRepository(Protocol):
    def get(self, order_id: int) -> Order | None: ...
    def save(self, order: Order) -> Order: ...
    def find_by_user(self, user_id: int) -> list[Order]: ...

# Application depends on abstraction
class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

# Infrastructure implements abstraction
class SqlOrderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, order_id: int) -> Order | None:
        model = self._session.query(OrderModel).get(order_id)
        return model.to_entity() if model else None

class InMemoryOrderRepository:
    def __init__(self) -> None:
        self._orders: dict[int, Order] = {}

    def get(self, order_id: int) -> Order | None:
        return self._orders.get(order_id)
```

---

### Dependency Injection

Dependency injection makes dependencies explicit and enables testing.

**Constructor injection (preferred):**
```python
class OrderService:
    def __init__(
        self,
        repository: OrderRepository,
        payment_gateway: PaymentGateway,
        email_sender: EmailSender,
    ) -> None:
        self._repository = repository
        self._payment_gateway = payment_gateway
        self._email_sender = email_sender

    def process_order(self, order_id: int) -> None:
        order = self._repository.get(order_id)
        self._payment_gateway.charge(order.total)
        self._email_sender.send_confirmation(order)
```

**Avoid service locators (hidden dependencies):**
```python
# BAD: Hidden dependency - hard to test, unclear requirements
class OrderService:
    def process_order(self, order_id: int) -> None:
        repository = ServiceLocator.get(OrderRepository)  # Hidden!
        order = repository.get(order_id)

# GOOD: Explicit dependency - easy to test, clear requirements
class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository
```

**Composition root (wire dependencies at startup):**
```python
# main.py or dependencies.py
def create_order_service(settings: Settings) -> OrderService:
    """Composition root - wire all dependencies."""
    db_session = create_db_session(settings.database_url)
    repository = SqlOrderRepository(db_session)
    payment_gateway = StripePaymentGateway(settings.stripe_key)
    email_sender = SendgridEmailSender(settings.sendgrid_key)

    return OrderService(
        repository=repository,
        payment_gateway=payment_gateway,
        email_sender=email_sender,
    )
```

**Factory functions for complex setup:**
```python
class OrderServiceFactory:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def create(self) -> OrderService:
        return OrderService(
            repository=self._create_repository(),
            payment_gateway=self._create_payment_gateway(),
            email_sender=self._create_email_sender(),
        )

    def _create_repository(self) -> OrderRepository:
        session = create_db_session(self._settings.database_url)
        return SqlOrderRepository(session)
```

---

### Module Organization Guidelines

#### When to Create a New Module

Create a new module when:

| Criterion | Indicator |
|-----------|-----------|
| **Single Responsibility** | Current module has multiple reasons to change |
| **Size Limit** | Current module exceeds size limits (e.g., 200 lines) |
| **Cohesion** | Group of functions/classes are tightly related but separate from others |
| **Reusability** | Code could be used independently |
| **Testability** | Code needs different test fixtures |

#### When to Create a New Package (directory)

Create a new package when:
1. Module has grown to need multiple files
2. Feature area is self-contained
3. Code represents a distinct bounded context
4. Integration with specific technology (adapters/integrations)

#### Naming Guidelines

| Type | Convention | Example |
|------|------------|---------|
| Entities | Singular noun | `user.py`, `order.py` |
| Services | Noun + "service" | `payment_service.py` |
| Repositories | Noun + "repository" | `user_repository.py` |
| Adapters | System + "adapter" | `stripe_adapter.py` |
| Use cases | Verb + noun | `create_order.py` |
| Utilities | Descriptive | `string_helpers.py` |

---

### Error Handling Architecture

#### Exception Hierarchy

Design a consistent exception hierarchy that reflects your domain:

```python
# exceptions.py
class AppError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self.code = code


# Domain errors - business rule violations
class DomainError(AppError):
    """Base for domain rule violations."""


class ValidationError(DomainError):
    """Invalid input data."""


class BusinessRuleViolation(DomainError):
    """Business rule not satisfied."""


# Application errors - use case failures
class ApplicationError(AppError):
    """Base for application-level errors."""


class NotFoundError(ApplicationError):
    """Requested resource not found."""


class ConflictError(ApplicationError):
    """Operation conflicts with current state."""


class AuthorizationError(ApplicationError):
    """User not authorized for operation."""


# Infrastructure errors - technical failures
class InfrastructureError(AppError):
    """Base for infrastructure failures."""


class DatabaseError(InfrastructureError):
    """Database operation failed."""


class ExternalServiceError(InfrastructureError):
    """External service call failed."""
```

#### Error Handling Guidelines

1. **Fail fast**: Validate early, raise immediately
2. **Specific exceptions**: Use specific types, not generic `Exception`
3. **Meaningful messages**: Include context for debugging
4. **Handle at boundaries**: Catch and translate at layer boundaries

```python
# Domain - raise specific errors
def get_user(user_id: int) -> User:
    user = self._repository.find(user_id)
    if user is None:
        raise NotFoundError(
            f"User with ID {user_id} not found",
            code="USER_NOT_FOUND",
        )
    return user

# Presentation - translate to HTTP
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> Response:
    return JSONResponse(
        status_code=404,
        content={"error": exc.code, "message": str(exc)},
    )

@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> Response:
    return JSONResponse(
        status_code=400,
        content={"error": exc.code, "message": str(exc)},
    )
```

---

### Async/Await Patterns

#### Consistency Principle

Be consistent with sync vs async throughout a call chain:

```python
# GOOD: Consistent async
async def get_user_with_orders(user_id: int) -> UserWithOrders:
    user = await self._user_repository.get(user_id)
    orders = await self._order_repository.find_by_user(user_id)
    return UserWithOrders(user=user, orders=orders)

# BAD: Mixing sync in async context blocks the event loop
async def get_user_with_orders(user_id: int) -> UserWithOrders:
    user = await self._user_repository.get(user_id)
    orders = self._order_repository.find_by_user(user_id)  # Blocking!
    return UserWithOrders(user=user, orders=orders)
```

#### Concurrent Operations

Use `asyncio.gather` for independent I/O operations:

```python
# GOOD: Concurrent I/O with gather
async def get_user_profile(user_id: int) -> UserProfile:
    user, orders, preferences = await asyncio.gather(
        self._user_repo.get(user_id),
        self._order_repo.find_by_user(user_id),
        self._preference_repo.get(user_id),
    )
    return UserProfile(user=user, orders=orders, preferences=preferences)

# Consider error handling
async def get_user_profile(user_id: int) -> UserProfile:
    results = await asyncio.gather(
        self._user_repo.get(user_id),
        self._order_repo.find_by_user(user_id),
        self._preference_repo.get(user_id),
        return_exceptions=True,  # Don't fail fast, collect all results
    )
    # Handle individual failures
```

#### Resource Cleanup

Always use async context managers for resources:

```python
# GOOD: Proper cleanup with async context manager
async def process_orders() -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            ...
```

---

### Configuration Management

#### Environment-Based Configuration

Use environment variables for configuration that varies between environments:

```python
# config.py
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class DatabaseConfig:
    url: str
    pool_size: int = 5
    echo: bool = False

    @classmethod
    def from_env(cls) -> DatabaseConfig:
        return cls(
            url=os.environ["DATABASE_URL"],
            pool_size=int(os.environ.get("DB_POOL_SIZE", "5")),
            echo=os.environ.get("DB_ECHO", "false").lower() == "true",
        )


@dataclass(frozen=True)
class AppConfig:
    database: DatabaseConfig
    debug: bool = False

    @classmethod
    def from_env(cls) -> AppConfig:
        return cls(
            database=DatabaseConfig.from_env(),
            debug=os.environ.get("DEBUG", "false").lower() == "true",
        )
```

#### Configuration Validation

Validate configuration at startup, fail fast on invalid config:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False
    max_connections: int = 10

    model_config = {
        "env_prefix": "APP_",
        "env_file": ".env",
    }


# Validates on startup - app won't start with invalid config
settings = Settings()
```

#### Configuration Guidelines

1. **Single source of truth**: One configuration class/file
2. **Immutable config**: Use frozen dataclasses or Pydantic
3. **Validate early**: Validate all config at startup
4. **Sensible defaults**: Provide defaults for optional settings
5. **No secrets in code**: Use environment variables or secret managers

---

### Public API Design

#### Export Strategy

Export only what users need from `__init__.py`:

```python
# __init__.py
"""MyPackage - A description of what it does.

Example:
    >>> from mypackage import Service, Config
    >>> service = Service(Config())
    >>> result = service.process(data)
"""
from mypackage.core.service import Service
from mypackage.core.config import Config
from mypackage.core.result import Result
from mypackage.exceptions import MyPackageError, ValidationError

__all__ = [
    # Core classes
    "Service",
    "Config",
    "Result",
    # Exceptions
    "MyPackageError",
    "ValidationError",
]

__version__ = "1.0.0"
```

#### API Design Guidelines

1. **Explicit exports**: Use `__all__` to be explicit about public API
2. **Convenience imports**: Re-export commonly used classes from `__init__.py`
3. **Internal modules**: Use `_prefix` convention for internal modules
4. **Stable interfaces**: Only export stable, documented APIs
5. **Backward compatibility**: Don't remove or change exported symbols without deprecation

---

### Anti-Patterns to Avoid

#### 1. God Class

A class that knows too much or does too much.

```python
# BAD: God class
class ApplicationManager:
    def create_user(self): ...
    def process_order(self): ...
    def send_email(self): ...
    def generate_report(self): ...
    def backup_database(self): ...
```

**Fix**: Split into focused classes with single responsibilities.

#### 2. Anemic Domain Model

Domain objects that are just data containers with no behavior.

```python
# BAD: Anemic domain model
@dataclass
class Order:
    items: list[OrderItem]
    total: Decimal
    status: str

class OrderService:
    def calculate_total(self, order: Order) -> Decimal:
        return sum(item.price * item.quantity for item in order.items)

    def can_ship(self, order: Order) -> bool:
        return order.status == "paid" and order.total > 0
```

```python
# GOOD: Rich domain model
@dataclass
class Order:
    items: list[OrderItem]
    status: OrderStatus

    @property
    def total(self) -> Decimal:
        return sum(item.price * item.quantity for item in self.items)

    def can_ship(self) -> bool:
        return self.status == OrderStatus.PAID and self.total > 0

    def mark_shipped(self) -> None:
        if not self.can_ship():
            raise BusinessRuleViolation("Order cannot be shipped")
        self.status = OrderStatus.SHIPPED
```

#### 3. Circular Dependencies

Modules that depend on each other directly or indirectly.

```python
# BAD: Circular dependency
# user.py
from order import Order  # Imports order
class User:
    orders: list[Order]

# order.py
from user import User  # Imports user - circular!
class Order:
    user: User
```

**Fix**: Use dependency inversion, introduce abstractions, or restructure modules.

#### 4. Leaky Abstractions

Implementation details leaking through abstractions.

```python
# BAD: SQL leaking through repository interface
class UserRepository(Protocol):
    def find_by_sql(self, sql: str) -> list[User]: ...  # Leaky!

# GOOD: Abstract interface
class UserRepository(Protocol):
    def find_by_criteria(self, criteria: UserCriteria) -> list[User]: ...
```

---

### Decision Framework

#### When to Add a Layer

| Question | If Yes |
|----------|--------|
| Does logic need to be reused across different entry points? | Add application layer |
| Is there complex business logic that needs isolation? | Add domain layer |
| Do you need to swap implementations (DB, external services)? | Add infrastructure abstractions |
| Is the codebase growing beyond single-file complexity? | Consider layered structure |

#### When to Keep It Simple

| Situation | Recommendation |
|-----------|----------------|
| Small script or utility | Single file is fine |
| CRUD-only application | Minimal layers needed |
| Prototype or spike | Simplicity over architecture |
| Small team, small codebase | Don't over-engineer |

---

## OBSERVABILITY

The three pillars: Logs, Metrics, Traces.

---

### Structured Logging

```python
import structlog
from contextvars import ContextVar

# Request context
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def add_request_context(logger, method_name, event_dict):
    """Add request context to all log entries."""
    event_dict["request_id"] = request_id_var.get()
    return event_dict


structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        add_request_context,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
)

logger = structlog.get_logger()


# Middleware to set request context
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    request_id_var.set(request_id)
    
    logger.info(
        "request_started",
        method=request.method,
        path=request.url.path,
    )
    
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    
    logger.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=duration * 1000,
    )
    
    response.headers["X-Request-ID"] = request_id
    return response
```

### Health Checks

```python
from dataclasses import dataclass
from enum import Enum


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    message: str | None = None
    latency_ms: float | None = None


class HealthChecker:
    def __init__(
        self,
        db_session,
        redis_client,
        external_services: list,
    ):
        self._db = db_session
        self._redis = redis_client
        self._services = external_services
    
    async def check_all(self) -> dict:
        checks = await asyncio.gather(
            self._check_database(),
            self._check_redis(),
            *[self._check_service(s) for s in self._services],
        )
        
        overall = HealthStatus.HEALTHY
        if any(c.status == HealthStatus.UNHEALTHY for c in checks):
            overall = HealthStatus.UNHEALTHY
        elif any(c.status == HealthStatus.DEGRADED for c in checks):
            overall = HealthStatus.DEGRADED
        
        return {
            "status": overall.value,
            "checks": {c.name: c.__dict__ for c in checks},
        }
    
    async def _check_database(self) -> HealthCheck:
        try:
            start = time.perf_counter()
            await self._db.execute(text("SELECT 1"))
            latency = (time.perf_counter() - start) * 1000
            return HealthCheck("database", HealthStatus.HEALTHY, latency_ms=latency)
        except Exception as e:
            return HealthCheck("database", HealthStatus.UNHEALTHY, str(e))


@app.get("/health")
async def health_check(checker: HealthChecker = Depends()):
    result = await checker.check_all()
    status_code = 200 if result["status"] == "healthy" else 503
    return JSONResponse(result, status_code=status_code)
```

---

## FEATURE FLAGS

Toggle features without deployments.

---

### Feature Flag Implementation

```python
from dataclasses import dataclass
from enum import Enum
from typing import Any


class RolloutStrategy(Enum):
    ALL = "all"
    NONE = "none"
    PERCENTAGE = "percentage"
    USER_LIST = "user_list"
    PROPERTY = "property"


@dataclass
class FeatureFlag:
    key: str
    enabled: bool
    strategy: RolloutStrategy
    percentage: int = 0
    user_list: list[str] = None
    property_rules: dict = None


class FeatureFlagService:
    def __init__(self, config_source: FeatureFlagSource):
        self._source = config_source
        self._cache: dict[str, FeatureFlag] = {}
    
    async def is_enabled(
        self,
        flag_key: str,
        user_id: str | None = None,
        properties: dict | None = None,
    ) -> bool:
        """Check if feature is enabled for user."""
        flag = await self._get_flag(flag_key)
        if flag is None:
            return False
        
        if not flag.enabled:
            return False
        
        match flag.strategy:
            case RolloutStrategy.ALL:
                return True
            case RolloutStrategy.NONE:
                return False
            case RolloutStrategy.PERCENTAGE:
                return self._check_percentage(user_id, flag.percentage)
            case RolloutStrategy.USER_LIST:
                return user_id in (flag.user_list or [])
            case RolloutStrategy.PROPERTY:
                return self._check_properties(properties, flag.property_rules)
        
        return False
    
    def _check_percentage(self, user_id: str | None, percentage: int) -> bool:
        if user_id is None:
            return False
        # Consistent hashing for sticky bucketing
        bucket = hash(user_id) % 100
        return bucket < percentage


# Context manager for feature flags
class FeatureContext:
    def __init__(self, service: FeatureFlagService, user_id: str):
        self._service = service
        self._user_id = user_id
    
    async def is_enabled(self, flag: str) -> bool:
        return await self._service.is_enabled(flag, self._user_id)


# Usage in application
async def create_order(
    request: CreateOrderRequest,
    features: FeatureContext = Depends(get_features),
):
    order = Order.create(request)
    
    if await features.is_enabled("new_discount_engine"):
        discount = await new_discount_service.calculate(order)
    else:
        discount = await legacy_discount_service.calculate(order)
    
    order.apply_discount(discount)
    return order
```

---

## QUICK REFERENCE

### Architecture Patterns

| Pattern | Use When | Trade-off |
|---------|----------|-----------|
| Layered | Clear separation needed | More indirection |
| Hexagonal | Multiple I/O adapters | More abstractions |
| CQRS | Different read/write needs | Complexity |
| Event Sourcing | Audit trail, time travel | Storage, rebuilding |
| Microservices | Independent scaling/teams | Network, consistency |

### Layer Dependencies

```
Presentation → Application → Domain ← Infrastructure
     │              │           │            │
     │              │           │            │
     └──────────────┴───────────┴────────────┘
                    (depends on)
```

### Configuration Checklist

- [ ] Environment variables for all env-specific config
- [ ] Validation at startup
- [ ] Immutable configuration objects
- [ ] Sensible defaults
- [ ] No secrets in code

---

## Related Skills

- `arch-ddd` - Domain-Driven Design tactical patterns
- `arch-hexagonal` - Hexagonal/Ports & Adapters architecture
- `arch-cqrs-es` - Event Sourcing and CQRS patterns
- `arch-microservices` - Distributed systems patterns
