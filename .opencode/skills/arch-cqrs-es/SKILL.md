---
name: arch-cqrs-es
description: >
  Event Sourcing and CQRS (Command Query Responsibility Segregation) patterns:
  event store implementation, projections, read models, commands, and queries.
version: "2.0"
source: mixed
related:
  - arch-ddd
  - arch-microservices
  - perf-database
  - guru-patterns-behavioral
---

## EVENT SOURCING

Store state as a sequence of events rather than current state.

---

### Event Store Implementation

```python
from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar
from uuid import UUID
import json


@dataclass
class StoredEvent:
    """Event as stored in the event store."""
    
    event_id: UUID
    aggregate_id: UUID
    aggregate_type: str
    event_type: str
    event_data: dict
    metadata: dict
    version: int
    occurred_at: datetime


class EventStore:
    """Append-only event store."""
    
    def __init__(self, session):
        self._session = session
    
    async def append(
        self,
        aggregate_id: UUID,
        aggregate_type: str,
        events: list[DomainEvent],
        expected_version: int,
    ) -> None:
        """Append events with optimistic concurrency."""
        # Check current version for optimistic locking
        current_version = await self._get_version(aggregate_id)
        if current_version != expected_version:
            raise ConcurrencyError(
                f"Expected version {expected_version}, got {current_version}"
            )
        
        # Append events
        for i, event in enumerate(events):
            stored = StoredEvent(
                event_id=event.event_id,
                aggregate_id=aggregate_id,
                aggregate_type=aggregate_type,
                event_type=event.__class__.__name__,
                event_data=self._serialize_event(event),
                metadata={"correlation_id": get_correlation_id()},
                version=expected_version + i + 1,
                occurred_at=event.occurred_at,
            )
            self._session.add(EventModel.from_stored(stored))
        
        await self._session.commit()
    
    async def get_events(
        self,
        aggregate_id: UUID,
        from_version: int = 0,
    ) -> list[DomainEvent]:
        """Get all events for an aggregate."""
        query = (
            select(EventModel)
            .where(EventModel.aggregate_id == aggregate_id)
            .where(EventModel.version > from_version)
            .order_by(EventModel.version)
        )
        result = await self._session.execute(query)
        return [self._deserialize_event(e) for e in result.scalars()]
    
    def _serialize_event(self, event: DomainEvent) -> dict:
        """Serialize event to JSON-compatible dict."""
        return {
            k: self._serialize_value(v)
            for k, v in event.__dict__.items()
            if not k.startswith("_")
        }
    
    def _deserialize_event(self, model: EventModel) -> DomainEvent:
        """Deserialize event from storage."""
        event_class = EVENT_REGISTRY[model.event_type]
        return event_class(**model.event_data)
```

---

### Event-Sourced Aggregate

```python
class OrderAggregate:
    """Order aggregate with event sourcing."""
    
    def __init__(self):
        self.id: UUID | None = None
        self.customer_id: UUID | None = None
        self.items: list[OrderItem] = []
        self.status: OrderStatus = OrderStatus.DRAFT
        self._version: int = 0
        self._pending_events: list[DomainEvent] = []
    
    @classmethod
    def create(cls, order_id: UUID, customer_id: UUID) -> "OrderAggregate":
        """Factory method to create new order."""
        order = cls()
        order._apply(OrderCreated(order_id=order_id, customer_id=customer_id))
        return order
    
    @classmethod
    def from_events(cls, events: list[DomainEvent]) -> "OrderAggregate":
        """Reconstitute aggregate from event history."""
        order = cls()
        for event in events:
            order._apply(event, is_new=False)
        return order
    
    def add_item(self, product_id: UUID, name: str, price: Money, quantity: int) -> None:
        """Command: Add item to order."""
        if self.status != OrderStatus.DRAFT:
            raise BusinessRuleViolation("Cannot modify submitted order")
        
        self._apply(OrderItemAdded(
            order_id=self.id,
            product_id=product_id,
            product_name=name,
            unit_price=price,
            quantity=quantity,
        ))
    
    def submit(self) -> None:
        """Command: Submit order."""
        if not self.items:
            raise BusinessRuleViolation("Cannot submit empty order")
        
        self._apply(OrderSubmitted(
            order_id=self.id,
            customer_id=self.customer_id,
            total_amount=self.total,
            item_count=len(self.items),
        ))
    
    def _apply(self, event: DomainEvent, is_new: bool = True) -> None:
        """Apply event to aggregate state."""
        # Update state based on event type
        handler = getattr(self, f"_on_{event.__class__.__name__}", None)
        if handler:
            handler(event)
        
        self._version += 1
        if is_new:
            self._pending_events.append(event)
    
    def _on_OrderCreated(self, event: OrderCreated) -> None:
        self.id = event.order_id
        self.customer_id = event.customer_id
        self.status = OrderStatus.DRAFT
    
    def _on_OrderItemAdded(self, event: OrderItemAdded) -> None:
        self.items.append(OrderItem(
            product_id=event.product_id,
            product_name=event.product_name,
            unit_price=event.unit_price,
            quantity=event.quantity,
        ))
    
    def _on_OrderSubmitted(self, event: OrderSubmitted) -> None:
        self.status = OrderStatus.SUBMITTED
    
    @property
    def pending_events(self) -> list[DomainEvent]:
        return self._pending_events.copy()
    
    def clear_events(self) -> None:
        self._pending_events.clear()
```

---

### Projections (Read Models)

```python
class OrderProjection:
    """Build read model from events."""
    
    def __init__(self, session):
        self._session = session
    
    async def project(self, event: DomainEvent) -> None:
        """Update read model based on event."""
        handler = getattr(self, f"on_{event.__class__.__name__}", None)
        if handler:
            await handler(event)
    
    async def on_OrderCreated(self, event: OrderCreated) -> None:
        """Create order in read model."""
        order_view = OrderView(
            id=event.order_id,
            customer_id=event.customer_id,
            status="draft",
            item_count=0,
            total=Decimal("0"),
            created_at=event.occurred_at,
        )
        self._session.add(order_view)
        await self._session.commit()
    
    async def on_OrderItemAdded(self, event: OrderItemAdded) -> None:
        """Update order view with new item."""
        order_view = await self._get_order(event.order_id)
        order_view.item_count += 1
        order_view.total += event.unit_price.amount * event.quantity
        await self._session.commit()
    
    async def on_OrderSubmitted(self, event: OrderSubmitted) -> None:
        """Update order status."""
        order_view = await self._get_order(event.order_id)
        order_view.status = "submitted"
        order_view.submitted_at = event.occurred_at
        await self._session.commit()


# Projection rebuilder
class ProjectionRebuilder:
    """Rebuild projections from event history."""
    
    async def rebuild(
        self,
        projection: OrderProjection,
        event_store: EventStore,
    ) -> None:
        """Rebuild projection from scratch."""
        # Clear existing read model
        await projection.truncate()
        
        # Replay all events
        async for event in event_store.stream_all():
            await projection.project(event)
```

---

## CQRS (Command Query Responsibility Segregation)

Separate read and write models for different optimization strategies.

---

### CQRS Implementation

```python
# Commands (write side)
@dataclass(frozen=True)
class CreateOrderCommand:
    customer_id: UUID
    items: list[OrderItemData]


@dataclass(frozen=True)
class SubmitOrderCommand:
    order_id: UUID


class OrderCommandHandler:
    """Handle order commands (write side)."""
    
    def __init__(
        self,
        repository: OrderRepository,
        event_publisher: EventPublisher,
    ):
        self._repository = repository
        self._event_publisher = event_publisher
    
    async def handle(self, command: CreateOrderCommand) -> UUID:
        """Handle CreateOrderCommand."""
        order = Order.create(
            customer_id=command.customer_id,
        )
        for item in command.items:
            order.add_item(
                product_id=item.product_id,
                name=item.name,
                price=item.price,
                quantity=item.quantity,
            )
        
        await self._repository.save(order)
        
        # Publish events for read side updates
        for event in order.collect_events():
            await self._event_publisher.publish(event)
        
        return order.id
    
    async def handle_submit(self, command: SubmitOrderCommand) -> None:
        """Handle SubmitOrderCommand."""
        order = await self._repository.get(command.order_id)
        if order is None:
            raise NotFoundError(f"Order {command.order_id} not found")
        
        order.submit()
        await self._repository.save(order)
        
        for event in order.collect_events():
            await self._event_publisher.publish(event)


# Queries (read side)
@dataclass(frozen=True)
class GetOrderQuery:
    order_id: UUID


@dataclass(frozen=True)
class SearchOrdersQuery:
    customer_id: UUID | None = None
    status: str | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None
    page: int = 1
    page_size: int = 20


class OrderQueryHandler:
    """Handle order queries (read side)."""
    
    def __init__(self, read_db: AsyncSession):
        self._db = read_db
    
    async def get_order(self, query: GetOrderQuery) -> OrderView | None:
        """Get single order from read model."""
        stmt = select(OrderViewModel).where(OrderViewModel.id == query.order_id)
        result = await self._db.execute(stmt)
        model = result.scalar_one_or_none()
        return OrderView.from_model(model) if model else None
    
    async def search_orders(self, query: SearchOrdersQuery) -> Page[OrderSummary]:
        """Search orders with filters."""
        stmt = select(OrderViewModel)
        
        # Apply filters
        if query.customer_id:
            stmt = stmt.where(OrderViewModel.customer_id == query.customer_id)
        if query.status:
            stmt = stmt.where(OrderViewModel.status == query.status)
        if query.from_date:
            stmt = stmt.where(OrderViewModel.created_at >= query.from_date)
        if query.to_date:
            stmt = stmt.where(OrderViewModel.created_at <= query.to_date)
        
        # Pagination
        total = await self._count(stmt)
        stmt = stmt.offset((query.page - 1) * query.page_size).limit(query.page_size)
        
        result = await self._db.execute(stmt)
        items = [OrderSummary.from_model(m) for m in result.scalars()]
        
        return Page(
            items=items,
            total=total,
            page=query.page,
            page_size=query.page_size,
        )
```

---

### CQRS Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                            API Layer                                 │
├────────────────────────────┬────────────────────────────────────────┤
│      Commands (POST/PUT)   │           Queries (GET)                │
│    CreateOrderCommand      │         GetOrderQuery                  │
│    SubmitOrderCommand      │         SearchOrdersQuery              │
├────────────────────────────┼────────────────────────────────────────┤
│     Command Handler        │          Query Handler                 │
│   (Domain Logic + Events)  │     (Simple Read from DB)              │
├────────────────────────────┼────────────────────────────────────────┤
│      Write Model           │          Read Model                    │
│   (Aggregates, Entities)   │    (Denormalized Views)                │
├────────────────────────────┴────────────────────────────────────────┤
│                    Event Bus / Message Queue                         │
│                    (Sync Read Model from Events)                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## QUICK REFERENCE

### Event Sourcing Benefits

| Benefit | Description |
|---------|-------------|
| Audit Trail | Complete history of all changes |
| Time Travel | Reconstruct state at any point |
| Event Replay | Rebuild projections from events |
| Debugging | See exactly what happened |
| Analytics | Rich data for analysis |

### Event Sourcing Challenges

| Challenge | Solution |
|-----------|----------|
| Event Evolution | Schema versioning, upcasters |
| Storage Size | Snapshotting, archiving |
| Eventual Consistency | Accept or use saga for strong |
| Complexity | Start with simple projections |

### CQRS Benefits

| Benefit | Description |
|---------|-------------|
| Optimized Models | Read/write models optimized separately |
| Scalability | Scale reads and writes independently |
| Flexibility | Different storage for read/write |
| Simplicity | Simple queries on denormalized data |

### When to Use

| Pattern | Use When |
|---------|----------|
| Event Sourcing | Need audit trail, undo, analytics |
| CQRS | Different read/write patterns |
| Both Together | Complex domain with reporting needs |
| Neither | Simple CRUD applications |

---

## Related Skills

- `arch-ddd` - Domain-Driven Design patterns
- `arch-principles` - Core architecture principles
- `arch-microservices` - Saga pattern for distributed transactions
