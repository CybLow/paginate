---
name: arch-ddd
description: >
  Domain-Driven Design tactical patterns: bounded contexts, context mapping,
  entities, value objects, aggregates, domain events, and domain services.
version: "2.0"
source: mixed
related:
  - arch-principles
  - arch-cqrs-es
  - arch-hexagonal
  - guru-patterns-behavioral
---

## DOMAIN-DRIVEN DESIGN (DDD)

DDD is a strategic and tactical approach to software development that focuses on the core domain and domain logic.

---

### Strategic DDD: Bounded Contexts

A bounded context is a boundary within which a domain model is defined and applicable.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        E-Commerce System                             │
├─────────────────┬─────────────────┬─────────────────────────────────┤
│   Sales Context │ Shipping Context│      Billing Context            │
├─────────────────┼─────────────────┼─────────────────────────────────┤
│ • Order         │ • Shipment      │ • Invoice                       │
│ • Customer      │ • Package       │ • Payment                       │
│ • Product       │ • Address       │ • Customer (billing info)       │
│ • Cart          │ • Carrier       │ • Receipt                       │
└─────────────────┴─────────────────┴─────────────────────────────────┘
```

**Context Mapping - Relationships between contexts:**

| Pattern | Description | Use When |
|---------|-------------|----------|
| **Shared Kernel** | Shared subset of domain model | Teams can coordinate closely |
| **Customer/Supplier** | Upstream provides, downstream consumes | Clear dependency direction |
| **Conformist** | Downstream adopts upstream's model | No influence over upstream |
| **Anti-Corruption Layer** | Translation layer between contexts | Protecting from external models |
| **Open Host Service** | Well-defined protocol for integration | Many consumers |
| **Published Language** | Shared documented language | Cross-context communication |

```python
# Anti-Corruption Layer example
# Protects our domain from external payment provider's model

class PaymentProviderACL:
    """Anti-Corruption Layer for external payment provider."""
    
    def __init__(self, stripe_client):
        self._stripe = stripe_client
    
    def charge(self, payment: Payment) -> PaymentResult:
        """Translate our domain model to Stripe's model and back."""
        # Translate to external model
        stripe_charge = self._stripe.Charge.create(
            amount=int(payment.amount.cents),
            currency=payment.amount.currency.lower(),
            source=payment.payment_method.token,
            metadata={"order_id": str(payment.order_id)},
        )
        
        # Translate back to our domain model
        return PaymentResult(
            success=stripe_charge.status == "succeeded",
            transaction_id=TransactionId(stripe_charge.id),
            charged_amount=Money(stripe_charge.amount, payment.amount.currency),
            error=self._translate_error(stripe_charge) if stripe_charge.failure_code else None,
        )
    
    def _translate_error(self, charge) -> PaymentError:
        """Translate external error codes to domain errors."""
        error_map = {
            "card_declined": PaymentErrorCode.DECLINED,
            "insufficient_funds": PaymentErrorCode.INSUFFICIENT_FUNDS,
            "expired_card": PaymentErrorCode.EXPIRED,
        }
        return PaymentError(
            code=error_map.get(charge.failure_code, PaymentErrorCode.UNKNOWN),
            message=charge.failure_message,
        )
```

---

### Tactical DDD: Building Blocks

#### Entities

Objects with identity that persists over time.

```python
from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Order:
    """Order entity - identified by its ID, not its attributes."""
    
    id: UUID = field(default_factory=uuid4)
    customer_id: UUID = field(default=None)
    items: list["OrderItem"] = field(default_factory=list)
    status: "OrderStatus" = field(default=OrderStatus.DRAFT)
    _events: list["DomainEvent"] = field(default_factory=list, repr=False)
    
    def __eq__(self, other: object) -> bool:
        """Entities are equal if they have the same identity."""
        if not isinstance(other, Order):
            return NotImplemented
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def add_item(self, product: "Product", quantity: int) -> None:
        """Add item to order - business logic lives in entity."""
        if self.status != OrderStatus.DRAFT:
            raise BusinessRuleViolation("Cannot modify submitted order")
        
        existing = next((i for i in self.items if i.product_id == product.id), None)
        if existing:
            existing.quantity += quantity
        else:
            self.items.append(OrderItem(
                product_id=product.id,
                product_name=product.name,
                unit_price=product.price,
                quantity=quantity,
            ))
        
        self._events.append(OrderItemAdded(self.id, product.id, quantity))
    
    def submit(self) -> None:
        """Submit order for processing."""
        if not self.items:
            raise BusinessRuleViolation("Cannot submit empty order")
        if self.status != OrderStatus.DRAFT:
            raise BusinessRuleViolation("Order already submitted")
        
        self.status = OrderStatus.SUBMITTED
        self._events.append(OrderSubmitted(self.id, self.total))
    
    @property
    def total(self) -> Money:
        return sum((item.subtotal for item in self.items), Money.zero())
    
    def collect_events(self) -> list["DomainEvent"]:
        """Collect and clear domain events."""
        events = self._events.copy()
        self._events.clear()
        return events
```

#### Value Objects

Immutable objects defined by their attributes, not identity.

```python
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    """Money value object - immutable, defined by value."""
    
    amount: Decimal
    currency: str = "USD"
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if len(self.currency) != 3:
            raise ValueError("Currency must be 3-letter code")
    
    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def __mul__(self, multiplier: int | Decimal) -> "Money":
        return Money(self.amount * Decimal(multiplier), self.currency)
    
    @classmethod
    def zero(cls, currency: str = "USD") -> "Money":
        return cls(Decimal("0"), currency)
    
    @property
    def cents(self) -> int:
        return int(self.amount * 100)


@dataclass(frozen=True)
class Address:
    """Address value object."""
    
    street: str
    city: str
    state: str
    postal_code: str
    country: str = "US"
    
    def __post_init__(self):
        if not self.street.strip():
            raise ValueError("Street is required")
        if not self.postal_code.strip():
            raise ValueError("Postal code is required")
    
    def format(self) -> str:
        return f"{self.street}\n{self.city}, {self.state} {self.postal_code}\n{self.country}"


@dataclass(frozen=True)
class EmailAddress:
    """Email address value object with validation."""
    
    value: str
    
    def __post_init__(self):
        if "@" not in self.value or "." not in self.value.split("@")[1]:
            raise ValueError(f"Invalid email: {self.value}")
    
    @property
    def domain(self) -> str:
        return self.value.split("@")[1]
    
    def __str__(self) -> str:
        return self.value
```

#### Aggregates

Cluster of entities and value objects with a single root entity.

```python
from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class Order:
    """Order aggregate root - all access goes through here."""
    
    id: UUID
    customer_id: UUID
    status: OrderStatus
    _items: list["OrderItem"] = field(default_factory=list)
    _events: list["DomainEvent"] = field(default_factory=list)
    
    # Invariant: Order must maintain consistency
    MAX_ITEMS = 100
    
    @property
    def items(self) -> tuple["OrderItem", ...]:
        """Expose items as immutable tuple."""
        return tuple(self._items)
    
    def add_item(self, product_id: UUID, name: str, price: Money, quantity: int) -> None:
        """Add item while enforcing aggregate invariants."""
        # Invariant: Cannot modify non-draft orders
        if self.status != OrderStatus.DRAFT:
            raise BusinessRuleViolation("Cannot modify submitted order")
        
        # Invariant: Maximum items limit
        if len(self._items) >= self.MAX_ITEMS:
            raise BusinessRuleViolation(f"Order cannot have more than {self.MAX_ITEMS} items")
        
        # Invariant: Quantity must be positive
        if quantity <= 0:
            raise BusinessRuleViolation("Quantity must be positive")
        
        # Business logic
        existing = self._find_item(product_id)
        if existing:
            existing.increase_quantity(quantity)
        else:
            self._items.append(OrderItem(
                id=uuid4(),
                product_id=product_id,
                product_name=name,
                unit_price=price,
                quantity=quantity,
            ))
        
        self._events.append(OrderItemAdded(self.id, product_id, quantity))
    
    def remove_item(self, item_id: UUID) -> None:
        """Remove item from order."""
        if self.status != OrderStatus.DRAFT:
            raise BusinessRuleViolation("Cannot modify submitted order")
        
        item = next((i for i in self._items if i.id == item_id), None)
        if item is None:
            raise NotFoundError(f"Item {item_id} not found in order")
        
        self._items.remove(item)
        self._events.append(OrderItemRemoved(self.id, item_id))
    
    def _find_item(self, product_id: UUID) -> "OrderItem | None":
        return next((i for i in self._items if i.product_id == product_id), None)


# Aggregate rules:
# 1. Only the root is referenced from outside
# 2. Root controls all access to internals
# 3. Transactions don't cross aggregate boundaries
# 4. Aggregates are loaded and saved as a whole
```

#### Domain Events

Events that represent something significant that happened in the domain.

```python
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DomainEvent:
    """Base class for domain events."""
    
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class OrderSubmitted(DomainEvent):
    """Event raised when an order is submitted."""
    
    order_id: UUID
    customer_id: UUID
    total_amount: Money
    item_count: int


@dataclass(frozen=True)
class OrderShipped(DomainEvent):
    """Event raised when an order is shipped."""
    
    order_id: UUID
    tracking_number: str
    carrier: str
    estimated_delivery: datetime


@dataclass(frozen=True)
class PaymentReceived(DomainEvent):
    """Event raised when payment is received."""
    
    order_id: UUID
    payment_id: UUID
    amount: Money
    payment_method: str


# Event handler
class OrderEventHandler:
    def __init__(
        self,
        email_service: EmailService,
        inventory_service: InventoryService,
    ):
        self._email = email_service
        self._inventory = inventory_service
    
    async def handle(self, event: DomainEvent) -> None:
        """Dispatch event to appropriate handler."""
        handler = getattr(self, f"on_{event.__class__.__name__}", None)
        if handler:
            await handler(event)
    
    async def on_OrderSubmitted(self, event: OrderSubmitted) -> None:
        """React to order submission."""
        await self._email.send_order_confirmation(event.order_id)
        await self._inventory.reserve(event.order_id)
    
    async def on_OrderShipped(self, event: OrderShipped) -> None:
        """React to order shipment."""
        await self._email.send_shipping_notification(
            event.order_id,
            event.tracking_number,
        )
```

#### Domain Services

Operations that don't naturally belong to an entity or value object.

```python
class PricingService:
    """Domain service for complex pricing logic."""
    
    def __init__(self, discount_repository: DiscountRepository):
        self._discounts = discount_repository
    
    def calculate_order_price(
        self,
        items: list[OrderItem],
        customer: Customer,
        promo_code: str | None = None,
    ) -> OrderPricing:
        """Calculate final order price with all discounts."""
        subtotal = sum(item.subtotal for item in items)
        
        discounts = []
        
        # Volume discount
        if subtotal > Money(Decimal("100"), "USD"):
            volume_discount = subtotal * Decimal("0.05")
            discounts.append(Discount("VOLUME_5%", volume_discount))
        
        # Customer loyalty discount
        if customer.tier == CustomerTier.GOLD:
            loyalty_discount = subtotal * Decimal("0.10")
            discounts.append(Discount("LOYALTY_GOLD", loyalty_discount))
        
        # Promo code
        if promo_code:
            promo = self._discounts.find_by_code(promo_code)
            if promo and promo.is_valid():
                promo_discount = promo.apply(subtotal)
                discounts.append(Discount(promo_code, promo_discount))
        
        total_discount = sum(d.amount for d in discounts)
        final_price = subtotal - total_discount
        
        return OrderPricing(
            subtotal=subtotal,
            discounts=discounts,
            total=max(final_price, Money.zero()),
        )
```

---

## QUICK REFERENCE

### DDD Building Blocks

| Block | Definition | Example |
|-------|------------|---------|
| Entity | Identity over time | Order, User |
| Value Object | Defined by attributes | Money, Address |
| Aggregate | Consistency boundary | Order + OrderItems |
| Domain Event | Something happened | OrderSubmitted |
| Domain Service | Cross-entity logic | PricingService |
| Repository | Aggregate persistence | OrderRepository |

### Entity vs Value Object

| Characteristic | Entity | Value Object |
|----------------|--------|--------------|
| Identity | Has unique ID | Defined by attributes |
| Mutability | Can change state | Immutable |
| Equality | Compare by ID | Compare by value |
| Example | User, Order | Money, Address, Email |

### Aggregate Rules

1. Only the root is referenced from outside
2. Root controls all access to internals
3. Transactions don't cross aggregate boundaries
4. Aggregates are loaded and saved as a whole
5. Prefer small aggregates

### Context Mapping Patterns

| Pattern | Relationship |
|---------|--------------|
| Shared Kernel | Shared code between teams |
| Customer/Supplier | Upstream serves downstream |
| Conformist | Accept upstream's model |
| Anti-Corruption Layer | Translate external models |
| Open Host Service | Published API |
| Published Language | Shared documentation |

---

## Related Skills

- `arch-principles` - Core architecture principles
- `arch-cqrs-es` - Event Sourcing and CQRS patterns
- `arch-hexagonal` - Hexagonal architecture
- `guru-patterns-creational` - Factory patterns for aggregates
