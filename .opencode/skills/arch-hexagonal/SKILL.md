---
name: arch-hexagonal
description: >
  Hexagonal Architecture (Ports & Adapters) pattern for isolating application 
  core from external concerns. Covers domain/application/adapter structure,
  port interfaces (protocols), inbound/outbound adapters, and dependency flow.
version: "2.0"
source: mixed
related:
  - arch-principles
  - arch-ddd
  - guru-patterns-structural
  - type-hints
---

## HEXAGONAL ARCHITECTURE (Ports & Adapters)

Isolate the application core from external concerns. The hexagonal architecture places the domain at the center, with ports defining how the outside world interacts with it, and adapters implementing those ports.

---

### Core Concepts

**Ports**: Interfaces (protocols) that define how the application interacts with the outside world.
- **Inbound ports**: How external actors trigger actions (use cases)
- **Outbound ports**: How the application accesses external resources (repositories, gateways)

**Adapters**: Implementations that connect ports to actual technologies.
- **Inbound adapters**: HTTP API, CLI, message consumers (driving adapters)
- **Outbound adapters**: Database repositories, external APIs, email services (driven adapters)

---

### Structure

```
src/
├── domain/                    # Core business logic (no dependencies)
│   ├── model/
│   │   ├── order.py
│   │   └── customer.py
│   ├── service/
│   │   └── pricing_service.py
│   └── ports/                 # Interfaces (ports)
│       ├── order_repository.py
│       └── payment_gateway.py
│
├── application/               # Use cases (orchestration)
│   ├── commands/
│   │   └── create_order.py
│   └── queries/
│       └── get_order.py
│
└── adapters/                  # Implementations (adapters)
    ├── inbound/               # Driving adapters (trigger actions)
    │   ├── api/
    │   │   └── order_routes.py
    │   ├── cli/
    │   │   └── order_commands.py
    │   └── messaging/
    │       └── order_consumer.py
    │
    └── outbound/              # Driven adapters (called by app)
        ├── persistence/
        │   └── sql_order_repository.py
        ├── payment/
        │   └── stripe_payment_gateway.py
        └── notification/
            └── sendgrid_email_sender.py
```

---

### Port (Interface in Domain)

Ports define contracts using Python's `Protocol`:

```python
# domain/ports/order_repository.py
from typing import Protocol


class OrderRepository(Protocol):
    """Port for order persistence."""
    
    async def get(self, order_id: UUID) -> Order | None:
        """Get order by ID."""
        ...
    
    async def save(self, order: Order) -> None:
        """Save order."""
        ...
    
    async def find_by_customer(self, customer_id: UUID) -> list[Order]:
        """Find orders by customer."""
        ...


class PaymentGateway(Protocol):
    """Port for payment processing."""
    
    async def charge(self, payment: Payment) -> PaymentResult:
        """Process payment."""
        ...
    
    async def refund(self, transaction_id: TransactionId) -> RefundResult:
        """Refund payment."""
        ...
```

---

### Adapter (Implementation)

Adapters implement ports for specific technologies:

```python
# adapters/outbound/persistence/sql_order_repository.py
from sqlalchemy.ext.asyncio import AsyncSession


class SqlOrderRepository:
    """SQL adapter for OrderRepository port."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get(self, order_id: UUID) -> Order | None:
        stmt = (
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.id == order_id)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None
    
    async def save(self, order: Order) -> None:
        model = OrderModel.from_domain(order)
        self._session.add(model)
        await self._session.commit()


# adapters/inbound/api/order_routes.py
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/orders")
async def create_order(
    request: CreateOrderRequest,
    use_case: CreateOrderUseCase = Depends(get_create_order_use_case),
) -> OrderResponse:
    """Inbound adapter: HTTP API."""
    order_id = await use_case.execute(request.to_command())
    return OrderResponse(order_id=order_id)
```

---

### Dependency Flow

```
                    ┌─────────────────────┐
                    │   Inbound Adapter   │
                    │   (HTTP, CLI, MQ)   │
                    └──────────┬──────────┘
                               │ calls
                               ▼
                    ┌─────────────────────┐
                    │    Application      │
                    │    (Use Cases)      │
                    └──────────┬──────────┘
                               │ depends on
                               ▼
                    ┌─────────────────────┐
                    │      Domain         │
                    │   (Ports + Model)   │
                    └──────────┬──────────┘
                               │ defines
                               ▼
                    ┌─────────────────────┐
                    │   Outbound Adapter  │
                    │  (DB, APIs, Email)  │
                    └─────────────────────┘
```

**Key Rules:**
1. Domain has NO external dependencies
2. Application depends only on Domain
3. Adapters depend on Domain (implement ports)
4. Dependency injection wires adapters at startup

---

### Testing Benefits

```python
# Test with in-memory adapter
class InMemoryOrderRepository:
    def __init__(self):
        self._orders: dict[UUID, Order] = {}
    
    async def get(self, order_id: UUID) -> Order | None:
        return self._orders.get(order_id)
    
    async def save(self, order: Order) -> None:
        self._orders[order.id] = order


# Test the use case without database
async def test_create_order():
    repository = InMemoryOrderRepository()
    use_case = CreateOrderUseCase(repository)
    
    order_id = await use_case.execute(CreateOrderCommand(...))
    
    saved_order = await repository.get(order_id)
    assert saved_order is not None
```

---

## Quick Reference

| Component | Purpose | Location |
|-----------|---------|----------|
| **Port** | Interface/contract | `domain/ports/` |
| **Inbound Adapter** | Triggers use cases | `adapters/inbound/` |
| **Outbound Adapter** | External resources | `adapters/outbound/` |
| **Use Case** | Orchestrates domain | `application/` |
| **Domain Model** | Business logic | `domain/model/` |

### When to Use Hexagonal

| Use When | Avoid When |
|----------|------------|
| Multiple entry points (API, CLI, MQ) | Simple CRUD app |
| Need to swap infrastructure | Single adapter per port |
| High testability required | Rapid prototyping |
| Complex domain logic | Small team, small codebase |

---

## Related Skills

- `arch-principles` - Core architectural principles and dependency inversion
- `arch-ddd` - Domain-Driven Design tactical patterns
- `arch-cqrs-es` - CQRS for separating read/write concerns
