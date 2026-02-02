---
name: type-hints
description: >
  Complete guide to Python type hints and documentation. Covers basic annotations, Union/Optional syntax,
  generics with TypeVar and Generic, protocols for structural typing, ParamSpec for callable types,
  TypedDict for typed dictionaries, Literal types, and Google-style docstrings. Includes modern Python 3.11+ syntax.
  Includes advanced topics: variance (covariant/contravariant), recursive types, type narrowing with TypeGuard,
  plugin architecture typing, dataclass advanced patterns, attrs integration, Pydantic v2 patterns, and type stub creation.
related:
  - arch-hexagonal
  - guru-patterns-structural
  - api-rest
  - test-standards
---

## TYPE HINTS & DOCUMENTATION

Type hints make code self-documenting and enable static analysis. Documentation explains **why**, not **what**.

---

### Type Annotation Standards

**Required in all files:**
```python
from __future__ import annotations
```

**Annotate all public APIs:**
```python
# Public function - fully annotated
def find_users(
    filters: UserFilters,
    *,
    limit: int = 20,
    offset: int = 0,
) -> list[User]:
    ...

# Private function - annotated (recommended)
def _validate_email(email: str) -> bool:
    ...
```

**Modern syntax (Python 3.11+):**
```python
# Modern (use these)
X | None                  # Optional type
list[str]                 # List with type
dict[str, int]            # Dict with types
tuple[int, str]           # Fixed tuple
tuple[int, ...]           # Variable-length tuple

# Legacy (don't use)
Optional[X]               # Use X | None
List[str]                 # Use list[str]
Dict[str, int]            # Use dict[str, int]
Union[X, Y]               # Use X | Y
```

---

### Common Type Patterns

**Optional values:**
```python
def find_user(user_id: int) -> User | None:
    """Returns None if user not found."""
    ...

def get_user(user_id: int) -> User:
    """Raises UserNotFoundError if not found."""
    ...
```

**Collections:**
```python
from collections.abc import Sequence, Mapping, Iterable, Iterator

# Use abstract types for parameters (more flexible)
def process_items(items: Sequence[Item]) -> None:  # Accepts list, tuple, etc.
    ...

def merge_configs(configs: Mapping[str, Any]) -> dict[str, Any]:  # Accepts dict, etc.
    ...

# Use concrete types for return values (more specific)
def get_items() -> list[Item]:  # Returns exactly a list
    ...
```

**Callable types:**
```python
from collections.abc import Callable

# Simple callable
Handler = Callable[[Request], Response]

# With keyword arguments (use Protocol)
class Validator(Protocol):
    def __call__(self, value: str, *, strict: bool = False) -> bool: ...
```

**Self type:**
```python
from typing import Self

class Builder:
    def with_name(self, name: str) -> Self:
        self._name = name
        return self

class QueryBuilder(Builder):
    def with_limit(self, limit: int) -> Self:
        self._limit = limit
        return self  # Returns QueryBuilder, not Builder
```

---

### Generic Types

**TypeVar for type parameters:**
```python
from typing import TypeVar, Generic

T = TypeVar("T")

class Repository(Generic[T]):
    def get(self, id: int) -> T | None: ...
    def save(self, entity: T) -> T: ...
    def list(self) -> list[T]: ...

# Usage
class UserRepository(Repository[User]):
    def get(self, id: int) -> User | None: ...
```

**Bounded TypeVar:**
```python
from typing import TypeVar

# Must be subclass of Entity
EntityT = TypeVar("EntityT", bound="Entity")

def save_entity(entity: EntityT) -> EntityT:
    entity.save()
    return entity

# Constrained TypeVar (one of specific types)
NumberT = TypeVar("NumberT", int, float, Decimal)

def add(a: NumberT, b: NumberT) -> NumberT:
    return a + b
```

**ParamSpec for decorators:**
```python
from typing import ParamSpec, TypeVar, Callable

P = ParamSpec("P")
R = TypeVar("R")

def log_calls(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_calls
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"

# Type is preserved: greet(name: str, greeting: str = "Hello") -> str
```

---

### Protocol Classes

**Use for structural subtyping (duck typing with types):**
```python
from typing import Protocol, runtime_checkable

class Readable(Protocol):
    def read(self, size: int = -1) -> bytes: ...

class Writable(Protocol):
    def write(self, data: bytes) -> int: ...

class ReadWritable(Readable, Writable, Protocol):
    """Combines multiple protocols."""
    pass

# Any class with matching methods works
class FileWrapper:
    def read(self, size: int = -1) -> bytes:
        ...

    def write(self, data: bytes) -> int:
        ...

def copy_data(source: Readable, dest: Writable) -> None:
    data = source.read()
    dest.write(data)

# Works without explicit inheritance
copy_data(FileWrapper(), FileWrapper())
```

**Runtime checking (use sparingly):**
```python
@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...

# Can use isinstance at runtime
if isinstance(resource, Closeable):
    resource.close()
```

**Protocol vs ABC:**

| Protocol | ABC |
|----------|-----|
| Structural (duck typing) | Nominal (explicit inheritance) |
| No runtime overhead | Runtime overhead |
| Can't have implementation | Can have implementation |
| Preferred for interfaces | Use when sharing code |

---

### TypedDict for Structured Dictionaries

**Define expected dictionary structure:**
```python
from typing import TypedDict, Required, NotRequired

class UserDict(TypedDict):
    id: int
    name: str
    email: str
    age: NotRequired[int]  # Optional key

# All keys are required by default
class ConfigDict(TypedDict, total=False):
    debug: bool  # All keys optional with total=False
    log_level: str

def process_user(user: UserDict) -> None:
    print(user["name"])  # Type-safe access
```

---

### Literal Types

**Restrict to specific values:**
```python
from typing import Literal

Direction = Literal["north", "south", "east", "west"]
LogLevel = Literal["debug", "info", "warning", "error"]

def move(direction: Direction) -> None:
    ...

def log(message: str, level: LogLevel = "info") -> None:
    ...

# Type error if invalid value used
move("up")  # Error: "up" is not a valid Direction
```

---

### Final and ClassVar

**Constants and class variables:**
```python
from typing import Final, ClassVar

# Final - cannot be reassigned
MAX_SIZE: Final = 100
API_VERSION: Final[str] = "v1"

class Counter:
    # ClassVar - class attribute, not instance
    _count: ClassVar[int] = 0
    
    def __init__(self) -> None:
        Counter._count += 1
```

---

### NewType for Type Safety

**Create distinct types from existing ones:**
```python
from typing import NewType

UserId = NewType("UserId", int)
OrderId = NewType("OrderId", int)

def get_user(user_id: UserId) -> User:
    ...

def get_order(order_id: OrderId) -> Order:
    ...

# Type-safe: can't accidentally mix IDs
user_id = UserId(123)
order_id = OrderId(456)

get_user(user_id)    # OK
get_user(order_id)   # Type error!
get_user(123)        # Type error! Must wrap with UserId()
```

---

### Overload for Multiple Signatures

**Define multiple type signatures:**
```python
from typing import overload

@overload
def process(value: str) -> str: ...
@overload
def process(value: int) -> int: ...
@overload
def process(value: list[str]) -> list[str]: ...

def process(value: str | int | list[str]) -> str | int | list[str]:
    if isinstance(value, str):
        return value.upper()
    elif isinstance(value, int):
        return value * 2
    else:
        return [v.upper() for v in value]

# Type checker knows exact return type based on input
result = process("hello")  # str
result = process(42)       # int
result = process(["a"])    # list[str]
```

---

### Type Guards

**Narrow types with custom checks:**
```python
from typing import TypeGuard

def is_string_list(value: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(item, str) for item in value)

def process(items: list[object]) -> None:
    if is_string_list(items):
        # Type checker knows items is list[str] here
        for item in items:
            print(item.upper())  # OK - item is str
```

---

### Docstring Format (Google Style)

**Function docstring:**
```python
def search_users(
    query: str,
    *,
    limit: int = 20,
    include_inactive: bool = False,
) -> list[User]:
    """Search users by name or email.

    Performs a case-insensitive search across user names and email
    addresses. Results are ordered by relevance score.

    Args:
        query: Search query string. Minimum 2 characters.
        limit: Maximum number of results to return. Defaults to 20.
        include_inactive: Whether to include deactivated users.
            Defaults to False.

    Returns:
        List of matching users, ordered by relevance. Empty list if
        no matches found.

    Raises:
        ValueError: If query is shorter than 2 characters.
        DatabaseError: If database connection fails.

    Example:
        >>> users = search_users("john", limit=10)
        >>> len(users)
        3
    """
    ...
```

**Class docstring:**
```python
class OrderService:
    """Manages order lifecycle operations.

    Provides methods for creating, updating, and fulfilling orders.
    Integrates with inventory and payment services.

    Attributes:
        repository: Order data access layer.
        inventory: Inventory service for stock management.
        payment: Payment processing service.

    Example:
        >>> service = OrderService(repo, inventory, payment)
        >>> order = service.create_order(cart)
        >>> service.process_payment(order)
        >>> service.fulfill_order(order)
    """

    def __init__(
        self,
        repository: OrderRepository,
        inventory: InventoryService,
        payment: PaymentService,
    ) -> None:
        """Initialize order service with dependencies.

        Args:
            repository: Order data access.
            inventory: Inventory management service.
            payment: Payment processing service.
        """
        self._repository = repository
        self._inventory = inventory
        self._payment = payment
```

**Module docstring:**
```python
"""Order management module.

This module provides the core order processing functionality including
order creation, payment processing, and fulfillment.

Classes:
    Order: Order entity with line items and totals.
    OrderService: Business logic for order operations.
    OrderRepository: Data access for orders.

Functions:
    calculate_totals: Compute order subtotal, tax, and total.
    validate_order: Validate order before processing.

Example:
    >>> from orders import OrderService, Order
    >>> service = OrderService(...)
    >>> order = service.create_order(items)
"""
```

---

### When to Document

**Always document:**
- All public APIs (functions, classes, methods)
- Complex algorithms with non-obvious logic
- Business rules and their rationale
- Deviations from conventions (with why)
- Module-level docstrings

**Skip documentation for:**
- Obvious code (self-documenting)
- Private methods with clear names
- Simple getters/setters
- Test methods (the test name is the doc)

**Focus on WHY, not WHAT:**
```python
# BAD: States the obvious
def get_user(user_id: int) -> User:
    """Gets a user.

    Args:
        user_id: The user ID.

    Returns:
        The user.
    """
    ...

# GOOD: Explains behavior
def get_user(user_id: int) -> User:
    """Retrieve user by ID, raising if not found.

    Args:
        user_id: Unique identifier for the user.

    Returns:
        User entity with all associated data loaded.

    Raises:
        UserNotFoundError: If no user exists with the given ID.
        DatabaseError: If the database connection fails.
    """
    ...

# GOOD: Explains WHY for complex logic
def calculate_shipping(order: Order) -> Money:
    """Calculate shipping cost based on destination and weight.

    Uses tiered pricing: flat rate for orders under 5kg, weight-based
    for heavier orders. Free shipping for premium members on orders
    over $50 (per marketing promotion PROMO-2024-Q1).

    International orders use carrier API rates with 15% markup to
    cover customs handling (see FINANCE-2023-11 for rationale).
    """
    ...
```

---

### Type Hints Cheat Sheet

```python
from __future__ import annotations
from typing import TypeVar, Generic, Protocol, Self, Any, Final, Literal
from typing import TypedDict, NewType, overload, TypeGuard
from collections.abc import Callable, Sequence, Mapping, Iterator, Iterable

# Basic types
x: int = 1
y: float = 1.0
z: str = "hello"
flag: bool = True

# Optional (can be None)
name: str | None = None

# Collections
items: list[str] = []
unique: set[int] = set()
mapping: dict[str, int] = {}
coords: tuple[float, float] = (0.0, 0.0)
args: tuple[int, ...] = (1, 2, 3)

# Abstract collections (for parameters)
def process(items: Sequence[str]) -> None: ...
def lookup(data: Mapping[str, Any]) -> None: ...
def consume(source: Iterable[int]) -> None: ...

# Callable
Handler = Callable[[Request], Response]
Callback = Callable[[], None]
Transformer = Callable[[str], str]

# Literals (exact values)
Direction = Literal["left", "right", "up", "down"]
def move(direction: Direction) -> None: ...

# Final (constant)
MAX_SIZE: Final = 100

# NewType (distinct types)
UserId = NewType("UserId", int)

# TypeVar
T = TypeVar("T")
def first(items: list[T]) -> T | None:
    return items[0] if items else None

# Generic class
class Box(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value = value

# Self (for fluent APIs)
class Builder:
    def set_name(self, name: str) -> Self:
        self._name = name
        return self

# Protocol (interface)
class Closeable(Protocol):
    def close(self) -> None: ...

# TypedDict
class Config(TypedDict):
    debug: bool
    log_level: str
```

---

### Common Mistakes

| Mistake | Correct |
|---------|---------|
| `List[str]` | `list[str]` |
| `Optional[str]` | `str \| None` |
| `Union[str, int]` | `str \| int` |
| `Dict[str, Any]` | `dict[str, Any]` |
| `Tuple[int, ...]` | `tuple[int, ...]` |
| Missing `from __future__ import annotations` | Always include at top |
| `def func() -> None: pass` | `def func() -> None: ...` for stubs |
| Returning `Any` | Be specific about return type |
| `isinstance(x, List)` | `isinstance(x, list)` |

---

### Mypy Configuration

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_configs = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

---

## ADVANCED TYPE HINTS

### Variance (Covariant and Contravariant Types)

Variance describes how type parameters relate when their containing types are subtyped.

**Invariant (default):** Type must match exactly.
```python
from typing import TypeVar, Generic

T = TypeVar("T")  # Invariant by default

class Box(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value = value
    
    def get(self) -> T:
        return self._value
    
    def set(self, value: T) -> None:
        self._value = value

# Box[Animal] and Box[Dog] are completely unrelated types
# Can't assign Box[Dog] to Box[Animal] or vice versa
```

**Covariant:** Subtype relationship preserved. Use for **read-only** containers.
```python
from typing import TypeVar, Generic

T_co = TypeVar("T_co", covariant=True)

class ReadOnlyBox(Generic[T_co]):
    """Covariant - can only return T, never accept it."""
    
    def __init__(self, value: T_co) -> None:
        self._value = value
    
    def get(self) -> T_co:
        return self._value
    
    # CANNOT have: def set(self, value: T_co) -> None
    # Covariant types can only appear in return positions

class Animal: ...
class Dog(Animal): ...

def process_animals(box: ReadOnlyBox[Animal]) -> None:
    animal = box.get()  # Always safe - returns Animal or subtype

# Dog is subtype of Animal, so ReadOnlyBox[Dog] is subtype of ReadOnlyBox[Animal]
dog_box: ReadOnlyBox[Dog] = ReadOnlyBox(Dog())
process_animals(dog_box)  # OK - covariant allows this
```

**Contravariant:** Subtype relationship reversed. Use for **write-only** containers or callbacks.
```python
from typing import TypeVar, Generic
from collections.abc import Callable

T_contra = TypeVar("T_contra", contravariant=True)

class Handler(Generic[T_contra]):
    """Contravariant - can only accept T, never return it."""
    
    def __init__(self, callback: Callable[[T_contra], None]) -> None:
        self._callback = callback
    
    def handle(self, item: T_contra) -> None:
        self._callback(item)
    
    # CANNOT have: def get_item(self) -> T_contra
    # Contravariant types can only appear in parameter positions

class Animal: ...
class Dog(Animal): ...

def process_any_animal(animal: Animal) -> None:
    print(f"Processing {animal}")

# Handler[Animal] can handle any Animal
animal_handler: Handler[Animal] = Handler(process_any_animal)

# Dog is subtype of Animal, so Handler[Animal] is subtype of Handler[Dog]
# (relationship reversed!)
dog_handler: Handler[Dog] = animal_handler  # OK - contravariant allows this
dog_handler.handle(Dog())  # Safe - handler expects Animal, Dog is-a Animal
```

**Variance Quick Reference:**

| Variance | TypeVar | Use When | Subtyping |
|----------|---------|----------|-----------|
| Invariant | `T = TypeVar("T")` | Read AND write | No relationship |
| Covariant | `T_co = TypeVar("T_co", covariant=True)` | Read only (return) | Same direction |
| Contravariant | `T_contra = TypeVar("T_contra", contravariant=True)` | Write only (params) | Reversed |

**Common covariant types:** `Sequence`, `Mapping`, `Iterator`, `Iterable`
**Common contravariant types:** `Callable` parameters

**Callable variance:**
```python
from collections.abc import Callable

# Callable is contravariant in parameters, covariant in return type
# Callable[[ParamType], ReturnType]
#            ↑ contra    ↑ co

class Animal: ...
class Dog(Animal): ...

# Function that accepts Animal and returns Dog
def make_dog(animal: Animal) -> Dog:
    return Dog()

# Can assign to Callable that accepts Dog and returns Animal
handler: Callable[[Dog], Animal] = make_dog  # OK!
# - Parameter: Dog is subtype of Animal, contravariance allows Animal -> Dog
# - Return: Dog is subtype of Animal, covariance allows Dog -> Animal
```

---

### Recursive Types

**Self-referential types using TypeAlias:**
```python
from typing import TypeAlias

# JSON type (recursive)
JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None

def parse_json(data: str) -> JSON:
    import json
    return json.loads(data)

def process_json(value: JSON) -> None:
    if isinstance(value, dict):
        for key, val in value.items():
            process_json(val)  # Recursive call with same type
    elif isinstance(value, list):
        for item in value:
            process_json(item)
```

**Tree structures:**
```python
from __future__ import annotations
from dataclasses import dataclass
from typing import TypeAlias

@dataclass
class TreeNode:
    value: int
    children: list[TreeNode]  # Self-reference works with annotations import

# Alternative with TypeAlias
Tree: TypeAlias = dict[str, "Tree"] | str

config: Tree = {
    "database": {
        "host": "localhost",
        "port": "5432",
    },
    "cache": "redis://localhost",
}
```

**Linked list:**
```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")

@dataclass
class Node(Generic[T]):
    value: T
    next: Node[T] | None = None

# Usage
head: Node[int] = Node(1, Node(2, Node(3)))
```

**Recursive TypedDict:**
```python
from typing import TypedDict

class MenuItem(TypedDict):
    label: str
    url: str | None
    children: list["MenuItem"]  # Forward reference for recursion

menu: list[MenuItem] = [
    {
        "label": "Home",
        "url": "/",
        "children": [],
    },
    {
        "label": "Products",
        "url": None,
        "children": [
            {"label": "Widget", "url": "/products/widget", "children": []},
            {"label": "Gadget", "url": "/products/gadget", "children": []},
        ],
    },
]
```

**Expression trees (AST pattern):**
```python
from __future__ import annotations
from dataclasses import dataclass
from typing import TypeAlias

@dataclass
class Literal:
    value: int

@dataclass
class BinaryOp:
    left: Expr
    op: str
    right: Expr

@dataclass
class UnaryOp:
    op: str
    operand: Expr

# Recursive union type
Expr: TypeAlias = Literal | BinaryOp | UnaryOp

def evaluate(expr: Expr) -> int:
    match expr:
        case Literal(value):
            return value
        case BinaryOp(left, "+", right):
            return evaluate(left) + evaluate(right)
        case BinaryOp(left, "*", right):
            return evaluate(left) * evaluate(right)
        case UnaryOp("-", operand):
            return -evaluate(operand)
        case _:
            raise ValueError(f"Unknown expression: {expr}")

# (2 + 3) * -4
expr = BinaryOp(
    BinaryOp(Literal(2), "+", Literal(3)),
    "*",
    UnaryOp("-", Literal(4)),
)
result = evaluate(expr)  # -20
```

---

### Type Narrowing

Type narrowing refines a broad type to a more specific one within a code block.

**isinstance narrowing:**
```python
def process(value: str | int | list[str]) -> str:
    if isinstance(value, str):
        # Type narrowed to str
        return value.upper()
    elif isinstance(value, int):
        # Type narrowed to int
        return str(value * 2)
    else:
        # Type narrowed to list[str]
        return ", ".join(value)
```

**None checks:**
```python
def greet(name: str | None) -> str:
    if name is None:
        return "Hello, stranger!"
    # Type narrowed to str
    return f"Hello, {name.upper()}!"

# Also works with truthiness
def greet_truthy(name: str | None) -> str:
    if not name:  # Catches None and empty string
        return "Hello, stranger!"
    return f"Hello, {name}!"
```

**assert narrowing:**
```python
def process_user(user: User | None) -> str:
    assert user is not None, "User must be provided"
    # Type narrowed to User
    return user.name.upper()

# With isinstance
def get_length(value: object) -> int:
    assert isinstance(value, (str, list))
    # Type narrowed to str | list[Any]
    return len(value)
```

**Pattern matching (Python 3.10+):**
```python
from dataclasses import dataclass

@dataclass
class Circle:
    radius: float

@dataclass
class Rectangle:
    width: float
    height: float

Shape = Circle | Rectangle

def area(shape: Shape) -> float:
    match shape:
        case Circle(radius=r):
            # Type narrowed to Circle
            return 3.14159 * r ** 2
        case Rectangle(width=w, height=h):
            # Type narrowed to Rectangle
            return w * h
```

**TypeGuard (custom type narrowing):**
```python
from typing import TypeGuard

def is_string_list(value: list[object]) -> TypeGuard[list[str]]:
    """Type guard that narrows list[object] to list[str]."""
    return all(isinstance(item, str) for item in value)

def is_non_empty(value: list[str]) -> TypeGuard[list[str]]:
    """Ensure list is not empty."""
    return len(value) > 0

def process(items: list[object]) -> str:
    if is_string_list(items):
        # Type narrowed to list[str]
        if is_non_empty(items):
            return items[0].upper()
    return ""
```

**TypeGuard with classes:**
```python
from typing import TypeGuard, Any

class User:
    def __init__(self, name: str, email: str) -> None:
        self.name = name
        self.email = email

def is_user(obj: Any) -> TypeGuard[User]:
    """Check if object is a valid User."""
    return (
        isinstance(obj, dict)
        and "name" in obj
        and "email" in obj
        and isinstance(obj["name"], str)
        and isinstance(obj["email"], str)
    )

def process_data(data: Any) -> str:
    if is_user(data):
        # Type narrowed to User
        return f"{data.name} <{data.email}>"
    return "Unknown"
```

**TypeIs (Python 3.13+) - Stricter than TypeGuard:**
```python
from typing import TypeIs

def is_str(value: object) -> TypeIs[str]:
    """TypeIs narrows in both branches."""
    return isinstance(value, str)

def process(value: str | int) -> None:
    if is_str(value):
        # value is str here
        print(value.upper())
    else:
        # value is int here (TypeIs narrows the else branch too!)
        print(value * 2)
```

**Narrowing with callbacks:**
```python
from typing import TypeGuard
from collections.abc import Callable

def filter_by_type[T](
    items: list[object],
    predicate: Callable[[object], TypeGuard[T]],
) -> list[T]:
    """Filter items using a type guard predicate."""
    return [item for item in items if predicate(item)]

def is_int(x: object) -> TypeGuard[int]:
    return isinstance(x, int)

mixed: list[object] = [1, "hello", 2, "world", 3]
integers: list[int] = filter_by_type(mixed, is_int)  # [1, 2, 3]
```

---

### Plugin Architecture Typing

**Protocol-based plugin interface:**
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Plugin(Protocol):
    """Plugin interface that all plugins must implement."""
    
    @property
    def name(self) -> str:
        """Unique plugin name."""
        ...
    
    @property
    def version(self) -> str:
        """Plugin version string."""
        ...
    
    def initialize(self) -> None:
        """Called when plugin is loaded."""
        ...
    
    def shutdown(self) -> None:
        """Called when plugin is unloaded."""
        ...

class LoggingPlugin:
    """Concrete plugin - no explicit inheritance needed."""
    
    @property
    def name(self) -> str:
        return "logging"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self) -> None:
        print("Logging plugin initialized")
    
    def shutdown(self) -> None:
        print("Logging plugin shutdown")

# Type checking works via structural typing
plugin: Plugin = LoggingPlugin()  # OK
```

**Generic plugin registry:**
```python
from typing import TypeVar, Generic, Protocol
from collections.abc import Callable

P = TypeVar("P", bound=Protocol)

class PluginRegistry(Generic[P]):
    """Type-safe plugin registry."""
    
    def __init__(self) -> None:
        self._plugins: dict[str, P] = {}
        self._factories: dict[str, Callable[[], P]] = {}
    
    def register(self, name: str, factory: Callable[[], P]) -> None:
        """Register a plugin factory."""
        self._factories[name] = factory
    
    def get(self, name: str) -> P | None:
        """Get or create a plugin instance."""
        if name not in self._plugins:
            factory = self._factories.get(name)
            if factory is None:
                return None
            self._plugins[name] = factory()
        return self._plugins[name]
    
    def list_plugins(self) -> list[str]:
        """List registered plugin names."""
        return list(self._factories.keys())

# Usage
registry: PluginRegistry[Plugin] = PluginRegistry()
registry.register("logging", LoggingPlugin)
plugin = registry.get("logging")  # Type: Plugin | None
```

**Hook-based plugin system:**
```python
from typing import Protocol, TypeVar, Generic
from collections.abc import Callable
from dataclasses import dataclass, field

class Request:
    def __init__(self, path: str) -> None:
        self.path = path

class Response:
    def __init__(self, status: int, body: str) -> None:
        self.status = status
        self.body = body

# Hook protocols
class BeforeRequestHook(Protocol):
    def __call__(self, request: Request) -> Request | None:
        """Return modified request or None to abort."""
        ...

class AfterResponseHook(Protocol):
    def __call__(self, request: Request, response: Response) -> Response:
        """Return modified response."""
        ...

@dataclass
class HookManager:
    """Manages typed hooks for extensibility."""
    
    before_request: list[BeforeRequestHook] = field(default_factory=list)
    after_response: list[AfterResponseHook] = field(default_factory=list)
    
    def run_before_request(self, request: Request) -> Request | None:
        for hook in self.before_request:
            result = hook(request)
            if result is None:
                return None
            request = result
        return request
    
    def run_after_response(
        self, request: Request, response: Response
    ) -> Response:
        for hook in self.after_response:
            response = hook(request, response)
        return response

# Plugin that adds hooks
def logging_before_request(request: Request) -> Request:
    print(f"Request: {request.path}")
    return request

def add_header_after_response(
    request: Request, response: Response
) -> Response:
    response.body += "\n<!-- Generated by MyApp -->"
    return response

# Registration
hooks = HookManager()
hooks.before_request.append(logging_before_request)
hooks.after_response.append(add_header_after_response)
```

**Dynamic plugin loading with type safety:**
```python
from typing import Protocol, TypeVar, Any
from importlib import import_module
import inspect

class Plugin(Protocol):
    name: str
    def execute(self, data: dict[str, Any]) -> dict[str, Any]: ...

def load_plugin(module_path: str, class_name: str) -> Plugin | None:
    """Dynamically load a plugin with type checking."""
    try:
        module = import_module(module_path)
        plugin_class = getattr(module, class_name)
        
        # Verify it implements Plugin protocol
        instance = plugin_class()
        if not isinstance(instance, Plugin):
            raise TypeError(f"{class_name} does not implement Plugin protocol")
        
        return instance
    except (ImportError, AttributeError) as e:
        print(f"Failed to load plugin: {e}")
        return None

# Plugin configuration
PLUGINS: list[tuple[str, str]] = [
    ("myapp.plugins.transform", "TransformPlugin"),
    ("myapp.plugins.validate", "ValidatePlugin"),
]

def load_all_plugins() -> list[Plugin]:
    """Load all configured plugins."""
    plugins: list[Plugin] = []
    for module_path, class_name in PLUGINS:
        plugin = load_plugin(module_path, class_name)
        if plugin is not None:
            plugins.append(plugin)
    return plugins
```

---

### Dataclass Advanced Patterns

**field() options:**
```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Order:
    # Required fields (no default)
    customer_id: int
    
    # Default value
    status: str = "pending"
    
    # Default factory for mutable defaults
    items: list[str] = field(default_factory=list)
    
    # Computed at instantiation
    created_at: datetime = field(default_factory=datetime.now)
    
    # Excluded from __init__ (set in __post_init__)
    total: float = field(init=False)
    
    # Excluded from repr
    _internal_id: str = field(default="", repr=False)
    
    # Excluded from comparison
    metadata: dict[str, str] = field(
        default_factory=dict, compare=False
    )
    
    # Excluded from hash (if frozen=True)
    cache: dict[str, object] = field(
        default_factory=dict, hash=False
    )
```

**__post_init__ for derived fields:**
```python
from dataclasses import dataclass, field

@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)
    perimeter: float = field(init=False)
    
    def __post_init__(self) -> None:
        self.area = self.width * self.height
        self.perimeter = 2 * (self.width + self.height)

rect = Rectangle(3.0, 4.0)
print(rect.area)       # 12.0
print(rect.perimeter)  # 14.0
```

**InitVar for init-only parameters:**
```python
from dataclasses import dataclass, field, InitVar

@dataclass
class User:
    name: str
    password: InitVar[str]  # Only in __init__, not stored
    password_hash: str = field(init=False)
    
    def __post_init__(self, password: str) -> None:
        import hashlib
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()

user = User("alice", "secret123")
print(user.name)           # alice
print(user.password_hash)  # hashed value
# user.password  # AttributeError - not stored
```

**frozen with slots for immutability and performance:**
```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Point:
    """Immutable, memory-efficient point."""
    x: float
    y: float
    
    def distance_to(self, other: "Point") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

p1 = Point(0, 0)
p2 = Point(3, 4)
print(p1.distance_to(p2))  # 5.0

# p1.x = 1  # FrozenInstanceError - immutable
```

**KW_ONLY (Python 3.10+):**
```python
from dataclasses import dataclass, KW_ONLY

@dataclass
class Config:
    name: str           # Positional OK
    _: KW_ONLY         # Everything after this is keyword-only
    debug: bool = False
    log_level: str = "INFO"
    timeout: int = 30

# Must use keyword arguments for debug, log_level, timeout
config = Config("myapp", debug=True, log_level="DEBUG")
# config = Config("myapp", True)  # TypeError
```

**Inheritance patterns:**
```python
from dataclasses import dataclass, field

@dataclass
class Entity:
    """Base entity with ID."""
    id: int = field(default=0)

@dataclass
class TimestampMixin:
    """Mixin for timestamps."""
    created_at: str = field(default="")
    updated_at: str = field(default="")

# Multiple inheritance
@dataclass
class User(Entity, TimestampMixin):
    name: str = ""
    email: str = ""

# Proper field ordering with defaults
user = User(id=1, name="Alice", email="alice@example.com")
```

**Dataclass with validation:**
```python
from dataclasses import dataclass

@dataclass
class Email:
    address: str
    
    def __post_init__(self) -> None:
        if "@" not in self.address:
            raise ValueError(f"Invalid email: {self.address}")
        self.address = self.address.lower().strip()

@dataclass
class PositiveInt:
    value: int
    
    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError(f"Value must be positive: {self.value}")
```

---

### Attrs Integration

**Basic attrs usage:**
```python
import attrs

@attrs.define
class User:
    name: str
    email: str
    age: int = 0

user = User("Alice", "alice@example.com", 30)
print(user)  # User(name='Alice', email='alice@example.com', age=30)
```

**attrs vs dataclasses:**

| Feature | attrs | dataclasses |
|---------|-------|-------------|
| Validators | Built-in | Manual in __post_init__ |
| Converters | Built-in | Manual |
| Slots | `@define` (auto) | `slots=True` |
| Frozen | `@frozen` | `frozen=True` |
| Factory | `attrs.Factory` | `field(default_factory=)` |
| Performance | Slightly faster | Standard library |

**Validators:**
```python
import attrs
from attrs import validators

@attrs.define
class User:
    name: str = attrs.field(
        validator=[
            validators.instance_of(str),
            validators.min_len(1),
            validators.max_len(100),
        ]
    )
    email: str = attrs.field(
        validator=validators.matches_re(r"^[\w.-]+@[\w.-]+\.\w+$")
    )
    age: int = attrs.field(
        validator=[
            validators.instance_of(int),
            validators.ge(0),
            validators.le(150),
        ]
    )

# Custom validator
def validate_not_empty(instance: object, attribute: attrs.Attribute, value: str) -> None:
    if not value.strip():
        raise ValueError(f"{attribute.name} cannot be empty or whitespace")

@attrs.define
class Comment:
    text: str = attrs.field(validator=validate_not_empty)
```

**Converters:**
```python
import attrs
from datetime import datetime

def parse_datetime(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)

@attrs.define
class Event:
    name: str
    timestamp: datetime = attrs.field(converter=parse_datetime)
    tags: frozenset[str] = attrs.field(converter=frozenset)

# Converters applied automatically
event = Event(
    name="Deployment",
    timestamp="2024-01-15T10:30:00",
    tags=["production", "urgent"],
)
print(event.timestamp)  # datetime(2024, 1, 15, 10, 30)
print(event.tags)       # frozenset({'production', 'urgent'})
```

**slots and frozen:**
```python
import attrs

# slots=True is default with @define
@attrs.define
class Point:
    x: float
    y: float

# Frozen (immutable)
@attrs.frozen
class ImmutablePoint:
    x: float
    y: float

p = ImmutablePoint(1.0, 2.0)
# p.x = 3.0  # FrozenInstanceError
```

**evolve pattern (immutable updates):**
```python
import attrs

@attrs.frozen
class Config:
    host: str
    port: int
    debug: bool = False

# Create new instance with modified values
config = Config("localhost", 8080)
dev_config = attrs.evolve(config, debug=True, port=3000)

print(config)      # Config(host='localhost', port=8080, debug=False)
print(dev_config)  # Config(host='localhost', port=3000, debug=True)
```

**Factory with context:**
```python
import attrs
from uuid import uuid4

@attrs.define
class Task:
    name: str
    # Factory with no arguments
    id: str = attrs.field(factory=lambda: str(uuid4()))
    
    # Factory that takes the instance
    description: str = attrs.field()
    
    @description.default
    def _default_description(self) -> str:
        return f"Task: {self.name}"

task = Task("Build feature")
print(task.id)           # Random UUID
print(task.description)  # "Task: Build feature"
```

---

### Pydantic V2 Patterns

**BaseModel basics:**
```python
from pydantic import BaseModel, Field
from datetime import datetime

class User(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=100)
    email: str
    created_at: datetime = Field(default_factory=datetime.now)
    tags: list[str] = Field(default_factory=list)

# Automatic validation and parsing
user = User(id=1, name="Alice", email="alice@example.com")
print(user.model_dump())  # {'id': 1, 'name': 'Alice', ...}

# From dict
user = User.model_validate({"id": 1, "name": "Alice", "email": "a@b.com"})

# From JSON
user = User.model_validate_json('{"id": 1, "name": "Alice", "email": "a@b.com"}')
```

**Field validators:**
```python
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Self

class User(BaseModel):
    username: str
    email: str
    password: str
    password_confirm: str
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v.lower()
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()
    
    @model_validator(mode="after")
    def validate_passwords_match(self) -> Self:
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self
```

**model_config:**
```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,    # Strip whitespace from strings
        str_min_length=1,             # Minimum string length
        frozen=True,                  # Make immutable
        extra="forbid",               # Error on extra fields
        validate_assignment=True,     # Validate on attribute assignment
        use_enum_values=True,         # Use enum values instead of enum objects
        populate_by_name=True,        # Allow field aliases
        strict=False,                 # Allow type coercion
    )
    
    id: int
    name: str
```

**Serialization:**
```python
from pydantic import BaseModel, Field
from datetime import datetime

class Article(BaseModel):
    title: str
    content: str
    created_at: datetime
    internal_id: str = Field(exclude=True)  # Exclude from serialization
    
    def model_dump(self, **kwargs) -> dict:
        # Custom serialization logic
        data = super().model_dump(**kwargs)
        data["created_at"] = self.created_at.isoformat()
        return data

# Serialization options
article = Article(
    title="Hello",
    content="World",
    created_at=datetime.now(),
    internal_id="abc123",
)

article.model_dump()                    # Dict without internal_id
article.model_dump_json()               # JSON string
article.model_dump(mode="json")         # JSON-compatible dict
article.model_dump(include={"title"})   # Only title
article.model_dump(exclude={"content"}) # Without content
```

**Computed fields:**
```python
from pydantic import BaseModel, computed_field

class Rectangle(BaseModel):
    width: float
    height: float
    
    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height
    
    @computed_field
    @property
    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

rect = Rectangle(width=3.0, height=4.0)
print(rect.area)       # 12.0
print(rect.perimeter)  # 14.0
print(rect.model_dump())  # Includes area and perimeter
```

**Discriminated unions:**
```python
from pydantic import BaseModel, Field
from typing import Literal, Annotated, Union

class Cat(BaseModel):
    pet_type: Literal["cat"] = "cat"
    name: str
    meows_per_day: int

class Dog(BaseModel):
    pet_type: Literal["dog"] = "dog"
    name: str
    barks_per_day: int

class Fish(BaseModel):
    pet_type: Literal["fish"] = "fish"
    name: str
    tank_size: float

# Discriminated union for efficient parsing
Pet = Annotated[
    Union[Cat, Dog, Fish],
    Field(discriminator="pet_type"),
]

class Owner(BaseModel):
    name: str
    pets: list[Pet]

# Pydantic uses pet_type to determine which model to use
owner = Owner(
    name="Alice",
    pets=[
        {"pet_type": "cat", "name": "Whiskers", "meows_per_day": 50},
        {"pet_type": "dog", "name": "Rex", "barks_per_day": 30},
    ],
)
print(type(owner.pets[0]))  # Cat
print(type(owner.pets[1]))  # Dog
```

**Nested models and type coercion:**
```python
from pydantic import BaseModel
from datetime import datetime

class Address(BaseModel):
    street: str
    city: str
    country: str = "USA"

class User(BaseModel):
    name: str
    email: str
    address: Address  # Nested model
    joined: datetime  # Automatic parsing from string

# Nested dict is automatically converted to Address
user = User(
    name="Alice",
    email="alice@example.com",
    address={"street": "123 Main St", "city": "Boston"},
    joined="2024-01-15T10:30:00",
)
print(type(user.address))  # Address
print(type(user.joined))   # datetime
```

---

### Type Stubs

**Creating .pyi files:**
```python
# mymodule.pyi - type stub for mymodule.py

from typing import overload

# Function stubs
def process(data: str) -> str: ...
def calculate(x: int, y: int) -> int: ...

# Class stubs
class DataProcessor:
    def __init__(self, config: dict[str, str]) -> None: ...
    def run(self, input: bytes) -> bytes: ...
    
    @property
    def status(self) -> str: ...

# Overloaded functions
@overload
def parse(value: str) -> dict[str, str]: ...
@overload
def parse(value: bytes) -> dict[str, bytes]: ...
def parse(value: str | bytes) -> dict[str, str] | dict[str, bytes]: ...

# Variables
VERSION: str
DEBUG: bool
```

**stubgen usage:**
```bash
# Generate stubs for a module
stubgen -m mymodule -o stubs/

# Generate stubs for a package
stubgen -p mypackage -o stubs/

# Generate stubs from source
stubgen src/mymodule.py -o stubs/

# Options
stubgen -m mymodule --include-private  # Include _private
stubgen -m mymodule --export-less      # Minimal exports
```

**Inline type comments for legacy code:**
```python
# For Python 2/3 compatible code or when annotations aren't possible

# Variable annotations
x = 1  # type: int
data = {}  # type: dict[str, int]

# Function annotations
def legacy_func(name, count):
    # type: (str, int) -> list[str]
    return [name] * count

# Multi-line function signatures
def complex_func(
    name,  # type: str
    count,  # type: int
    options,  # type: dict[str, bool]
):
    # type: (...) -> list[str]
    return [name] * count

# Ignore type errors
result = unknown_function()  # type: ignore
risky_call()  # type: ignore[arg-type]
```

**py.typed marker:**
```
# File: src/mypackage/py.typed
# (empty file)

# This marker indicates the package supports type checking (PEP 561)
# Place in package root alongside __init__.py

# Directory structure:
# src/
#   mypackage/
#     __init__.py
#     py.typed          <-- marker file
#     module.py
#     subpackage/
#       __init__.py
```

**pyproject.toml for typed packages:**
```toml
[project]
name = "mypackage"
version = "1.0.0"

[tool.setuptools.package-data]
mypackage = ["py.typed", "*.pyi"]

# Alternatively, include stubs package
[project.optional-dependencies]
types = ["types-mypackage"]
```

**Stub packages:**
```python
# Types for third-party packages without inline types
# Install from typeshed or PyPI

# pip install types-requests
import requests  # Now has type information

# Common type stub packages:
# types-requests
# types-redis
# types-PyYAML
# types-python-dateutil
# types-setuptools
# pandas-stubs
# boto3-stubs
```

**Creating stub-only packages:**
```
# Package structure for types-mylib
types-mylib/
  mylib-stubs/
    __init__.pyi
    module.pyi
    subpackage/
      __init__.pyi
  setup.py

# setup.py
from setuptools import setup
setup(
    name="types-mylib",
    packages=["mylib-stubs"],
    package_data={"mylib-stubs": ["*.pyi", "**/*.pyi"]},
)
```

---

### Type Hints Quick Reference

**Variance:**
```python
T = TypeVar("T")                           # Invariant
T_co = TypeVar("T_co", covariant=True)     # Covariant (return only)
T_contra = TypeVar("T_contra", contravariant=True)  # Contravariant (param only)
```

**Narrowing:**
```python
isinstance(x, Type)           # Narrows to Type
x is None / x is not None     # Narrows optional
assert isinstance(x, Type)    # Narrows after assert
TypeGuard[T]                  # Custom narrowing (if branch only)
TypeIs[T]                     # Custom narrowing (both branches, 3.13+)
```

**Recursive:**
```python
JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
```

**Dataclass:**
```python
@dataclass(frozen=True, slots=True)
class Point:
    x: float
    y: float
    _: KW_ONLY
    name: str = ""
```

**attrs:**
```python
@attrs.frozen
class Config:
    value: str = attrs.field(validator=validators.min_len(1))
    count: int = attrs.field(converter=int)
```

**Pydantic:**
```python
class User(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    name: str = Field(min_length=1)
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.strip()
    
    @computed_field
    @property
    def display_name(self) -> str:
        return self.name.title()
```

**Stubs:**
```python
# module.pyi
def func(x: int) -> str: ...
class MyClass:
    attr: str
    def method(self) -> None: ...
```
