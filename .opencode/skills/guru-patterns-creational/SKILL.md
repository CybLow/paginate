---
name: guru-patterns-creational
description: >
  Creational design patterns for object instantiation. Covers Factory Method (create objects via subclass),
  Abstract Factory (families of related objects), Builder (step-by-step complex object construction),
  Prototype (cloning existing objects), and Singleton (single instance with global access).
  Each pattern includes problem/solution, UML structure, Python implementation, applicability, and trade-offs.
related:
  - guru-patterns-structural
  - guru-patterns-behavioral
  - arch-principles
  - test-data
---

## CREATIONAL DESIGN PATTERNS

Creational patterns deal with object creation mechanisms, trying to create objects in a manner suitable to the situation. They help make a system independent of how its objects are created, composed, and represented.

> **Reference**: Full details at [refactoring.guru/design-patterns/creational-patterns](https://refactoring.guru/design-patterns/creational-patterns)

---

### Factory Method

> Defines an interface for creating objects, letting subclasses decide which class to instantiate.

**Problem:**
You have a class that needs to create objects, but you don't know ahead of time which exact class of object you'll need. Hardcoding the class leads to tight coupling and makes it impossible to extend.

**Solution:**
Replace direct constructor calls with calls to a factory method. Subclasses can override this method to change the class of objects being created.

**Structure:**
```
┌─────────────────────┐       ┌─────────────────────┐
│     Creator         │       │      Product        │
├─────────────────────┤       │     (Protocol)      │
│ + factory_method()  │──────▶├─────────────────────┤
│ + some_operation()  │       │ + operation()       │
└─────────────────────┘       └─────────────────────┘
         △                              △
         │                              │
┌─────────────────────┐       ┌─────────────────────┐
│  ConcreteCreator    │       │  ConcreteProduct    │
├─────────────────────┤       ├─────────────────────┤
│ + factory_method()  │──────▶│ + operation()       │
└─────────────────────┘       └─────────────────────┘
```

**Example:**
```python
from typing import Protocol

class Notification(Protocol):
    def send(self, message: str) -> None: ...

class EmailNotification:
    def __init__(self, recipient: str) -> None:
        self._recipient = recipient

    def send(self, message: str) -> None:
        print(f"Email to {self._recipient}: {message}")

class SMSNotification:
    def __init__(self, phone: str) -> None:
        self._phone = phone

    def send(self, message: str) -> None:
        print(f"SMS to {self._phone}: {message}")

class PushNotification:
    def __init__(self, device_token: str) -> None:
        self._token = device_token

    def send(self, message: str) -> None:
        print(f"Push to {self._token}: {message}")

class NotificationFactory:
    """Factory for creating notification instances."""

    @staticmethod
    def create(notification_type: str, **kwargs) -> Notification:
        factories: dict[str, type[Notification]] = {
            "email": EmailNotification,
            "sms": SMSNotification,
            "push": PushNotification,
        }
        if notification_type not in factories:
            raise ValueError(f"Unknown notification type: {notification_type}")
        return factories[notification_type](**kwargs)

# Usage
notification = NotificationFactory.create("email", recipient="user@example.com")
notification.send("Hello!")
```

**Applicability:**
- You don't know beforehand the exact types of objects needed
- You want to provide extension points for users
- You want to save resources by reusing existing objects

**Consequences:**

| Pros | Cons |
|------|------|
| Loose coupling between creator and products | Can lead to many subclasses |
| Single Responsibility: creation code in one place | Clients may need to subclass Creator |
| Open/Closed: easy to add new products | |

---

### Abstract Factory

> Creates families of related objects without specifying concrete classes.

**Problem:**
You need to create families of related objects (e.g., UI elements for different operating systems) that should be used together, but you don't want the code to depend on concrete classes.

**Solution:**
Define interfaces for each product in the family, then create factory classes that produce all products for a specific variant.

**Structure:**
```
┌─────────────────────────┐
│    AbstractFactory      │
├─────────────────────────┤
│ + create_product_a()    │
│ + create_product_b()    │
└─────────────────────────┘
            △
            │
     ┌──────┴──────┐
     │             │
┌────────────┐ ┌────────────┐
│ Factory1   │ │ Factory2   │
├────────────┤ ├────────────┤
│ (creates   │ │ (creates   │
│  A1, B1)   │ │  A2, B2)   │
└────────────┘ └────────────┘
```

**Example:**
```python
from typing import Protocol
from collections.abc import Callable

# Abstract Products
class Button(Protocol):
    def render(self) -> str: ...
    def on_click(self, handler: Callable[[], None]) -> None: ...

class Checkbox(Protocol):
    def render(self) -> str: ...
    def is_checked(self) -> bool: ...

# Concrete Products - Light Theme
class LightButton:
    def render(self) -> str:
        return "<button class='light'>Click</button>"

    def on_click(self, handler: Callable[[], None]) -> None:
        handler()

class LightCheckbox:
    def __init__(self) -> None:
        self._checked = False

    def render(self) -> str:
        return "<input type='checkbox' class='light'/>"

    def is_checked(self) -> bool:
        return self._checked

# Concrete Products - Dark Theme
class DarkButton:
    def render(self) -> str:
        return "<button class='dark'>Click</button>"

    def on_click(self, handler: Callable[[], None]) -> None:
        handler()

class DarkCheckbox:
    def __init__(self) -> None:
        self._checked = False

    def render(self) -> str:
        return "<input type='checkbox' class='dark'/>"

    def is_checked(self) -> bool:
        return self._checked

# Abstract Factory
class UIFactory(Protocol):
    def create_button(self) -> Button: ...
    def create_checkbox(self) -> Checkbox: ...

# Concrete Factories
class LightThemeFactory:
    def create_button(self) -> Button:
        return LightButton()

    def create_checkbox(self) -> Checkbox:
        return LightCheckbox()

class DarkThemeFactory:
    def create_button(self) -> Button:
        return DarkButton()

    def create_checkbox(self) -> Checkbox:
        return DarkCheckbox()

# Client code works with any factory
def render_ui(factory: UIFactory) -> str:
    button = factory.create_button()
    checkbox = factory.create_checkbox()
    return f"{button.render()}\n{checkbox.render()}"
```

**Applicability:**
- System should be independent of how products are created
- System should work with multiple families of products
- Products in a family must be used together
- You want to provide a library without exposing implementations

**Consequences:**

| Pros | Cons |
|------|------|
| Products from same factory are compatible | Adding new product types is difficult |
| Loose coupling | Adds complexity with many interfaces |
| Single Responsibility | |
| Open/Closed for new families | |

---

### Builder

> Constructs complex objects step by step, allowing different representations.

**Problem:**
You have a complex object that requires laborious step-by-step initialization with many optional parameters. The constructor becomes unwieldy or you have many constructor overloads.

**Solution:**
Extract the construction code into a separate builder class with methods for each configuration step. The director class can define the order of building steps.

**Structure:**
```
┌──────────────┐     uses      ┌──────────────┐
│   Director   │──────────────▶│   Builder    │
├──────────────┤               ├──────────────┤
│ + construct()│               │ + step_a()   │
└──────────────┘               │ + step_b()   │
                               │ + get_result()│
                               └──────────────┘
```

**Example:**
```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Self

@dataclass
class Query:
    """Represents a database query."""
    table: str
    columns: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    order_by: list[str] = field(default_factory=list)
    limit: int | None = None
    offset: int | None = None

class QueryBuilder:
    """Builds complex queries step by step."""

    def __init__(self, table: str) -> None:
        self._table = table
        self._columns: list[str] = []
        self._conditions: list[str] = []
        self._order_by: list[str] = []
        self._limit: int | None = None
        self._offset: int | None = None

    def select(self, *columns: str) -> Self:
        self._columns.extend(columns)
        return self

    def where(self, condition: str) -> Self:
        self._conditions.append(condition)
        return self

    def order_by(self, column: str, descending: bool = False) -> Self:
        direction = "DESC" if descending else "ASC"
        self._order_by.append(f"{column} {direction}")
        return self

    def limit(self, count: int) -> Self:
        self._limit = count
        return self

    def offset(self, count: int) -> Self:
        self._offset = count
        return self

    def build(self) -> Query:
        return Query(
            table=self._table,
            columns=self._columns or ["*"],
            conditions=self._conditions,
            order_by=self._order_by,
            limit=self._limit,
            offset=self._offset,
        )

# Usage - fluent interface
query = (
    QueryBuilder("users")
    .select("id", "name", "email")
    .where("status = 'active'")
    .where("created_at > '2024-01-01'")
    .order_by("created_at", descending=True)
    .limit(10)
    .build()
)
```

**Applicability:**
- Object creation involves many steps
- You want different representations of the same construction process
- You want to isolate complex construction code from business logic
- You need fluent interface for configuration

**Consequences:**

| Pros | Cons |
|------|------|
| Construct objects step-by-step | Increases code complexity |
| Reuse construction code | Requires creating builder for each product |
| Single Responsibility | |
| Fluent, readable construction | |

---

### Prototype

> Creates new objects by cloning existing ones.

**Problem:**
You need to copy an object, but:
- You don't know its concrete class
- The object has private fields
- You want to avoid subclass explosion

**Solution:**
Declare a common interface with a `clone` method. Objects that support cloning are called prototypes.

**Example:**
```python
from __future__ import annotations
import copy
from dataclasses import dataclass
from typing import Any, Self

@dataclass
class DocumentTemplate:
    """A document that can be cloned and customized."""
    title: str
    content: str
    styles: dict[str, str]
    metadata: dict[str, Any]

    def clone(self) -> Self:
        """Create a deep copy of this template."""
        return copy.deepcopy(self)

    def with_title(self, title: str) -> Self:
        """Clone with a new title."""
        cloned = self.clone()
        cloned.title = title
        return cloned

# Usage
template = DocumentTemplate(
    title="Invoice Template",
    content="...",
    styles={"font": "Arial", "size": "12"},
    metadata={"version": "1.0"},
)

# Create variations without affecting original
invoice_jan = template.with_title("January Invoice")
invoice_feb = template.with_title("February Invoice")
```

**Applicability:**
- You need to copy objects without depending on their concrete classes
- You want to reduce subclasses that only differ in initialization
- Object creation is more expensive than cloning

**Consequences:**

| Pros | Cons |
|------|------|
| Clone without coupling to concrete classes | Cloning objects with circular references is tricky |
| Reduce repetitive initialization | Deep copy can be expensive |
| Produce complex objects more conveniently | |

---

### Singleton

> Ensures a class has only one instance with global access.

**Problem:**
You need to ensure that a class has just a single instance (e.g., database connection, configuration manager) and provide a global access point to it.

**Solution:**
Make the constructor private and create a static method that returns the same instance on every call.

**Warning:** Singleton is often overused and can make testing difficult. Prefer dependency injection.

**Example:**
```python
from __future__ import annotations
from threading import Lock
from typing import Any, ClassVar

class Configuration:
    """Thread-safe singleton configuration manager."""
    _instance: ClassVar[Configuration | None] = None
    _lock: ClassVar[Lock] = Lock()
    _initialized: bool

    def __new__(cls) -> Configuration:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-check
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._settings: dict[str, Any] = {}
        self._initialized = True

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._settings[key] = value

# Better alternative: module-level instance
# config.py
_config: Configuration | None = None

def get_config() -> Configuration:
    global _config
    if _config is None:
        _config = Configuration()
    return _config
```

**Applicability:**
- Exactly one instance needed (logging, configuration, connection pool)
- Need stricter global access control than global variable
- Want lazy initialization of a single instance

**Consequences:**

| Pros | Cons |
|------|------|
| Guaranteed single instance | Violates Single Responsibility |
| Global access point | Hard to unit test |
| Lazy initialization | Requires thread-safety in multithreaded apps |
| | Can mask bad design (hidden dependencies) |

---

### Creational Patterns Summary

| Pattern | Intent | Use When |
|---------|--------|----------|
| Factory Method | Create objects via subclasses | Don't know exact types needed |
| Abstract Factory | Create families of related objects | Need compatible product families |
| Builder | Step-by-step complex construction | Many optional parameters |
| Prototype | Clone existing objects | Copying is cheaper than creating |
| Singleton | Single instance with global access | Need exactly one instance (use sparingly) |

---
