---
name: guru-patterns-behavioral
description: >
  Behavioral design patterns for object interaction, responsibility delegation, and algorithm encapsulation in Python.
version: "1.0"
related:
  - guru-patterns-creational
  - guru-patterns-structural
  - arch-ddd
  - arch-cqrs-es
---

## BEHAVIORAL DESIGN PATTERNS

Patterns that deal with object interaction, communication, and responsibility delegation.

---

### Chain of Responsibility

> Passes requests along a chain of handlers until one handles it.

**Problem:**
You have multiple handlers that could process a request, but you don't know which one ahead of time, or you want multiple handlers to process it.

**Solution:**
Chain handlers together. Each handler decides whether to process the request and/or pass it to the next handler.

**Example:**
```python
from typing import Protocol
from dataclasses import dataclass

@dataclass
class Request:
    user: str
    resource: str
    action: str

@dataclass
class AuthResult:
    allowed: bool
    reason: str = ""

class AuthHandler(Protocol):
    def set_next(self, handler: AuthHandler) -> AuthHandler: ...
    def handle(self, request: Request) -> AuthResult: ...

class BaseAuthHandler:
    def __init__(self) -> None:
        self._next: AuthHandler | None = None

    def set_next(self, handler: AuthHandler) -> AuthHandler:
        self._next = handler
        return handler

    def handle(self, request: Request) -> AuthResult:
        if self._next:
            return self._next.handle(request)
        return AuthResult(allowed=True)

class AuthenticationHandler(BaseAuthHandler):
    def __init__(self, valid_users: set[str]) -> None:
        super().__init__()
        self._valid_users = valid_users

    def handle(self, request: Request) -> AuthResult:
        if request.user not in self._valid_users:
            return AuthResult(allowed=False, reason="User not authenticated")
        return super().handle(request)

class RateLimitHandler(BaseAuthHandler):
    def __init__(self, max_requests: int) -> None:
        super().__init__()
        self._requests: dict[str, int] = {}
        self._max = max_requests

    def handle(self, request: Request) -> AuthResult:
        count = self._requests.get(request.user, 0)
        if count >= self._max:
            return AuthResult(allowed=False, reason="Rate limit exceeded")
        self._requests[request.user] = count + 1
        return super().handle(request)

class PermissionHandler(BaseAuthHandler):
    def __init__(self, permissions: dict[str, set[str]]) -> None:
        super().__init__()
        self._permissions = permissions

    def handle(self, request: Request) -> AuthResult:
        user_perms = self._permissions.get(request.user, set())
        required = f"{request.resource}:{request.action}"
        if required not in user_perms:
            return AuthResult(allowed=False, reason="Permission denied")
        return super().handle(request)

# Build chain
auth = AuthenticationHandler({"alice", "bob"})
rate_limit = RateLimitHandler(max_requests=100)
perms = PermissionHandler({"alice": {"users:read", "users:write"}})

auth.set_next(rate_limit).set_next(perms)

# Use chain
result = auth.handle(Request("alice", "users", "read"))
```

**Applicability:**
- Multiple handlers could process a request
- Handler isn't known beforehand
- Execute handlers in particular order
- Set of handlers changes dynamically

**Consequences:**

| Pros | Cons |
|------|------|
| Control order of handling | Some requests may go unhandled |
| Single Responsibility | |
| Open/Closed: add new handlers without changing existing | |

---

### Command

> Encapsulates a request as an object, allowing parameterization and queuing.

**Problem:**
You need to parameterize objects with operations, queue operations, schedule execution, or support undo.

**Solution:**
Encapsulate all request details in a command object with an `execute` method.

**Example:**
```python
from typing import Protocol
from dataclasses import dataclass

class Command(Protocol):
    def execute(self) -> None: ...
    def undo(self) -> None: ...

@dataclass
class CreateOrderCommand:
    order_service: OrderService
    customer_id: str
    items: list[OrderItem]
    _created_order: Order | None = None

    def execute(self) -> None:
        self._created_order = self.order_service.create(
            self.customer_id, self.items
        )

    def undo(self) -> None:
        if self._created_order:
            self.order_service.cancel(self._created_order.id)

@dataclass
class SendEmailCommand:
    email_service: EmailService
    recipient: str
    subject: str
    body: str

    def execute(self) -> None:
        self.email_service.send(self.recipient, self.subject, self.body)

    def undo(self) -> None:
        pass  # Can't unsend email

class CommandQueue:
    """Queues commands for execution."""

    def __init__(self) -> None:
        self._queue: list[Command] = []
        self._history: list[Command] = []

    def add(self, command: Command) -> None:
        self._queue.append(command)

    def execute_all(self) -> None:
        while self._queue:
            command = self._queue.pop(0)
            command.execute()
            self._history.append(command)

    def undo_last(self) -> None:
        if self._history:
            command = self._history.pop()
            command.undo()

# Usage
queue = CommandQueue()
queue.add(CreateOrderCommand(order_service, "cust_123", items))
queue.add(SendEmailCommand(email_service, "user@example.com", "Order Confirmed", "..."))
queue.execute_all()
queue.undo_last()  # Undoes email (no-op) then order
```

**Applicability:**
- Parameterize objects with operations
- Queue, schedule, or execute remotely
- Implement undo/redo
- Assemble complex commands from simple ones

**Consequences:**

| Pros | Cons |
|------|------|
| Single Responsibility: decouple invoker from performer | More classes |
| Open/Closed: add new commands | |
| Implement undo/redo | |
| Assemble complex commands | |

---

### Iterator

> Provides a way to traverse elements without exposing underlying structure.

**Problem:**
Collections have different internal structures (list, tree, graph), but clients need a uniform way to traverse them.

**Solution:**
Extract traversal logic into iterator objects. The collection provides a method to create an iterator.

**Example:**
```python
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Self

@dataclass
class TreeNode:
    value: int
    left: TreeNode | None = None
    right: TreeNode | None = None

class BinaryTree:
    def __init__(self, root: TreeNode | None = None) -> None:
        self._root = root

    def __iter__(self) -> Iterator[int]:
        """Default iteration: in-order traversal."""
        return InOrderIterator(self._root)

    def breadth_first(self) -> Iterator[int]:
        """Alternative iteration: breadth-first."""
        return BreadthFirstIterator(self._root)

class InOrderIterator:
    """Iterates tree in-order (left, root, right)."""

    def __init__(self, root: TreeNode | None) -> None:
        self._stack: list[TreeNode] = []
        self._current = root

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> int:
        while self._current or self._stack:
            if self._current:
                self._stack.append(self._current)
                self._current = self._current.left
            else:
                node = self._stack.pop()
                self._current = node.right
                return node.value
        raise StopIteration

class BreadthFirstIterator:
    """Iterates tree level by level."""

    def __init__(self, root: TreeNode | None) -> None:
        self._queue: list[TreeNode] = [root] if root else []

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> int:
        if not self._queue:
            raise StopIteration
        node = self._queue.pop(0)
        if node.left:
            self._queue.append(node.left)
        if node.right:
            self._queue.append(node.right)
        return node.value

# Usage
tree = BinaryTree(TreeNode(5, TreeNode(3), TreeNode(7)))

for value in tree:  # In-order
    print(value)  # 3, 5, 7

for value in tree.breadth_first():  # Breadth-first
    print(value)  # 5, 3, 7
```

**Applicability:**
- Traverse collection without exposing structure
- Support multiple traversal algorithms
- Provide uniform interface for different collections

**Consequences:**

| Pros | Cons |
|------|------|
| Single Responsibility: clean collection code | Overkill for simple collections |
| Open/Closed: new iterators without changing collection | Less efficient than direct access |
| Parallel iteration on same collection | |

---

### Mediator

> Reduces direct dependencies between objects by making them communicate through a mediator.

**Problem:**
Objects have many direct relationships, creating a tangled web of dependencies that's hard to modify or reuse.

**Solution:**
Force objects to communicate only through a mediator object, which knows how to redirect calls.

**Example:**
```python
from typing import Protocol

class Mediator(Protocol):
    def notify(self, sender: Component, event: str) -> None: ...

class Component:
    def __init__(self, mediator: Mediator | None = None) -> None:
        self._mediator = mediator

    def set_mediator(self, mediator: Mediator) -> None:
        self._mediator = mediator

class SubmitButton(Component):
    def click(self) -> None:
        if self._mediator:
            self._mediator.notify(self, "submit")

class ResetButton(Component):
    def click(self) -> None:
        if self._mediator:
            self._mediator.notify(self, "reset")

class TextField(Component):
    def __init__(self, mediator: Mediator | None = None) -> None:
        super().__init__(mediator)
        self.value = ""

    def change(self, value: str) -> None:
        self.value = value
        if self._mediator:
            self._mediator.notify(self, "text_changed")

    def clear(self) -> None:
        self.value = ""

class FormMediator:
    """Coordinates form components."""

    def __init__(self) -> None:
        self.submit_button = SubmitButton(self)
        self.reset_button = ResetButton(self)
        self.name_field = TextField(self)
        self.email_field = TextField(self)
        self._submit_enabled = False

    def notify(self, sender: Component, event: str) -> None:
        match event:
            case "submit":
                self._handle_submit()
            case "reset":
                self._handle_reset()
            case "text_changed":
                self._validate_form()

    def _handle_submit(self) -> None:
        if self._submit_enabled:
            print(f"Submitting: {self.name_field.value}, {self.email_field.value}")

    def _handle_reset(self) -> None:
        self.name_field.clear()
        self.email_field.clear()
        self._submit_enabled = False

    def _validate_form(self) -> None:
        self._submit_enabled = bool(self.name_field.value and self.email_field.value)
```

**Applicability:**
- Objects are tightly coupled
- You can't reuse components due to dependencies
- Creating lots of component subclasses to customize behavior

**Consequences:**

| Pros | Cons |
|------|------|
| Single Responsibility | Mediator can become god object |
| Open/Closed: add new mediators | |
| Reduce coupling | |
| Reuse components | |

---

### Memento

> Saves and restores previous state without exposing implementation details.

**Problem:**
You need to save snapshots of an object's state to restore it later, but the object has private fields you can't access from outside.

**Solution:**
The object itself creates a memento containing a snapshot. Only the originator can restore state from the memento.

**Example:**
```python
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EditorMemento:
    """Stores editor state. Immutable and opaque to caretaker."""
    _state: dict[str, Any]

class TextEditor:
    """Originator: creates and restores from mementos."""

    def __init__(self) -> None:
        self._content = ""
        self._cursor_position = 0
        self._selection: tuple[int, int] | None = None

    def type(self, text: str) -> None:
        self._content = (
            self._content[:self._cursor_position] +
            text +
            self._content[self._cursor_position:]
        )
        self._cursor_position += len(text)

    def save(self) -> EditorMemento:
        return EditorMemento({
            "content": self._content,
            "cursor": self._cursor_position,
            "selection": self._selection,
        })

    def restore(self, memento: EditorMemento) -> None:
        self._content = memento._state["content"]
        self._cursor_position = memento._state["cursor"]
        self._selection = memento._state["selection"]

    @property
    def content(self) -> str:
        return self._content

class History:
    """Caretaker: manages mementos without knowing their content."""

    def __init__(self, editor: TextEditor) -> None:
        self._editor = editor
        self._history: list[EditorMemento] = []
        self._current = -1

    def save(self) -> None:
        # Remove any redo history
        self._history = self._history[:self._current + 1]
        self._history.append(self._editor.save())
        self._current += 1

    def undo(self) -> None:
        if self._current > 0:
            self._current -= 1
            self._editor.restore(self._history[self._current])

    def redo(self) -> None:
        if self._current < len(self._history) - 1:
            self._current += 1
            self._editor.restore(self._history[self._current])

# Usage
editor = TextEditor()
history = History(editor)

editor.type("Hello")
history.save()

editor.type(" World")
history.save()

print(editor.content)  # "Hello World"
history.undo()
print(editor.content)  # "Hello"
history.redo()
print(editor.content)  # "Hello World"
```

**Applicability:**
- Create snapshots to restore previous states
- Direct access to object's fields violates encapsulation
- Implement undo/redo

**Consequences:**

| Pros | Cons |
|------|------|
| Preserve encapsulation | RAM usage if clients create many mementos |
| Simplify originator code | Caretakers must track lifecycle |
| | Dynamic languages can't guarantee memento privacy |

---

### Observer

> Notifies multiple objects about events in an object they're observing.

**Problem:**
Objects need to be notified when something happens in another object, but you don't want tight coupling.

**Solution:**
Define a subscription mechanism that lets objects subscribe to and unsubscribe from events.

**Example:**
```python
from typing import Protocol, Any

class Observer(Protocol):
    def update(self, event: str, data: Any) -> None: ...

class EventEmitter:
    """Subject: manages observers and notifies them."""

    def __init__(self) -> None:
        self._observers: dict[str, list[Observer]] = {}

    def subscribe(self, event: str, observer: Observer) -> None:
        if event not in self._observers:
            self._observers[event] = []
        self._observers[event].append(observer)

    def unsubscribe(self, event: str, observer: Observer) -> None:
        if event in self._observers:
            self._observers[event].remove(observer)

    def emit(self, event: str, data: Any = None) -> None:
        for observer in self._observers.get(event, []):
            observer.update(event, data)

class Order(EventEmitter):
    def __init__(self, order_id: str) -> None:
        super().__init__()
        self.order_id = order_id
        self.status = "pending"

    def confirm(self) -> None:
        self.status = "confirmed"
        self.emit("order_confirmed", self)

    def ship(self) -> None:
        self.status = "shipped"
        self.emit("order_shipped", self)

# Observers
class EmailNotifier:
    def update(self, event: str, data: Any) -> None:
        if event == "order_confirmed":
            print(f"Email: Order {data.order_id} confirmed!")
        elif event == "order_shipped":
            print(f"Email: Order {data.order_id} shipped!")

class InventoryManager:
    def update(self, event: str, data: Any) -> None:
        if event == "order_confirmed":
            print(f"Inventory: Reserving items for {data.order_id}")

class AnalyticsTracker:
    def update(self, event: str, data: Any) -> None:
        print(f"Analytics: Event '{event}' for order {data.order_id}")

# Usage
order = Order("ORD-123")
order.subscribe("order_confirmed", EmailNotifier())
order.subscribe("order_confirmed", InventoryManager())
order.subscribe("order_confirmed", AnalyticsTracker())
order.subscribe("order_shipped", EmailNotifier())

order.confirm()  # Notifies all "order_confirmed" observers
order.ship()  # Notifies all "order_shipped" observers
```

**Applicability:**
- Changes to one object require changing others
- Some objects should observe others for limited time
- Objects should notify others without knowing who

**Consequences:**

| Pros | Cons |
|------|------|
| Open/Closed: add new subscribers | Subscribers notified in random order |
| Establish relations at runtime | |
| Loose coupling | |

---

### State

> Alters object behavior when its internal state changes.

**Problem:**
Object behaves differently based on its state, leading to massive conditionals checking state everywhere.

**Solution:**
Create state classes for each state. The context delegates state-specific behavior to the current state object.

**Example:**
```python
from typing import Protocol

class InvalidOperationError(Exception):
    """Raised when an operation is invalid for current state."""

class OrderState(Protocol):
    def confirm(self, order: Order) -> None: ...
    def ship(self, order: Order) -> None: ...
    def deliver(self, order: Order) -> None: ...
    def cancel(self, order: Order) -> None: ...

class PendingState:
    def confirm(self, order: Order) -> None:
        print("Order confirmed")
        order.set_state(ConfirmedState())

    def ship(self, order: Order) -> None:
        raise InvalidOperationError("Cannot ship pending order")

    def deliver(self, order: Order) -> None:
        raise InvalidOperationError("Cannot deliver pending order")

    def cancel(self, order: Order) -> None:
        print("Order cancelled")
        order.set_state(CancelledState())

class ConfirmedState:
    def confirm(self, order: Order) -> None:
        raise InvalidOperationError("Already confirmed")

    def ship(self, order: Order) -> None:
        print("Order shipped")
        order.set_state(ShippedState())

    def deliver(self, order: Order) -> None:
        raise InvalidOperationError("Cannot deliver before shipping")

    def cancel(self, order: Order) -> None:
        print("Order cancelled (refund issued)")
        order.set_state(CancelledState())

class ShippedState:
    def confirm(self, order: Order) -> None:
        raise InvalidOperationError("Already confirmed")

    def ship(self, order: Order) -> None:
        raise InvalidOperationError("Already shipped")

    def deliver(self, order: Order) -> None:
        print("Order delivered")
        order.set_state(DeliveredState())

    def cancel(self, order: Order) -> None:
        raise InvalidOperationError("Cannot cancel shipped order")

class DeliveredState:
    def confirm(self, order: Order) -> None:
        raise InvalidOperationError("Order already delivered")

    def ship(self, order: Order) -> None:
        raise InvalidOperationError("Order already delivered")

    def deliver(self, order: Order) -> None:
        raise InvalidOperationError("Order already delivered")

    def cancel(self, order: Order) -> None:
        raise InvalidOperationError("Cannot cancel delivered order")

class CancelledState:
    def confirm(self, order: Order) -> None:
        raise InvalidOperationError("Order is cancelled")

    def ship(self, order: Order) -> None:
        raise InvalidOperationError("Order is cancelled")

    def deliver(self, order: Order) -> None:
        raise InvalidOperationError("Order is cancelled")

    def cancel(self, order: Order) -> None:
        raise InvalidOperationError("Already cancelled")

class Order:
    def __init__(self) -> None:
        self._state: OrderState = PendingState()

    def set_state(self, state: OrderState) -> None:
        self._state = state

    def confirm(self) -> None:
        self._state.confirm(self)

    def ship(self) -> None:
        self._state.ship(self)

    def deliver(self) -> None:
        self._state.deliver(self)

    def cancel(self) -> None:
        self._state.cancel(self)

# Usage
order = Order()
order.confirm()  # OK
order.ship()  # OK
order.cancel()  # Raises InvalidOperationError
```

**Applicability:**
- Object behaves differently based on state
- Many conditionals checking state
- Lots of duplicate code across states

**Consequences:**

| Pros | Cons |
|------|------|
| Single Responsibility: organize state code | Overkill if few states or rare changes |
| Open/Closed: add new states | States may be aware of each other |
| Simplify context code | |

---

### Strategy

> Defines a family of algorithms and makes them interchangeable.

**Problem:**
You have multiple ways to do something and need to select the algorithm at runtime. Hardcoding algorithms leads to bloated classes.

**Solution:**
Extract each algorithm into a separate class with a common interface. The context works with any strategy.

**Example:**
```python
from typing import Protocol
from dataclasses import dataclass

class ShippingStrategy(Protocol):
    def calculate(self, order: Order) -> float: ...

class StandardShipping:
    def calculate(self, order: Order) -> float:
        return 5.99

class ExpressShipping:
    def calculate(self, order: Order) -> float:
        return 15.99

class FreeShipping:
    def calculate(self, order: Order) -> float:
        return 0.0

class WeightBasedShipping:
    def __init__(self, rate_per_kg: float) -> None:
        self._rate = rate_per_kg

    def calculate(self, order: Order) -> float:
        return order.total_weight * self._rate

class ShippingCalculator:
    """Context: uses strategy to calculate shipping."""

    def __init__(self, strategy: ShippingStrategy) -> None:
        self._strategy = strategy

    def set_strategy(self, strategy: ShippingStrategy) -> None:
        self._strategy = strategy

    def calculate(self, order: Order) -> float:
        return self._strategy.calculate(order)

# Usage
calculator = ShippingCalculator(StandardShipping())
print(calculator.calculate(order))  # 5.99

calculator.set_strategy(ExpressShipping())
print(calculator.calculate(order))  # 15.99

# Select strategy based on conditions
def get_shipping_strategy(order: Order, user: User) -> ShippingStrategy:
    if user.is_premium and order.total > 50:
        return FreeShipping()
    if order.is_urgent:
        return ExpressShipping()
    if order.total_weight > 10:
        return WeightBasedShipping(rate_per_kg=2.50)
    return StandardShipping()
```

**Applicability:**
- Use different algorithm variants
- Many similar classes differ only in behavior
- Isolate algorithm logic from context
- Class has massive conditional that switches algorithms

**Consequences:**

| Pros | Cons |
|------|------|
| Swap algorithms at runtime | Clients must know strategies to select one |
| Isolate algorithm implementation | Overkill for few algorithms |
| Replace inheritance with composition | Functional style may be simpler (lambdas) |
| Open/Closed | |

---

### Template Method

> Defines algorithm skeleton, letting subclasses override specific steps.

**Problem:**
You have several classes with similar algorithms but different details. Code duplication across classes.

**Solution:**
Break algorithm into steps. Put common steps in base class, let subclasses override specific steps.

**Example:**
```python
from abc import ABC, abstractmethod

class DataProcessor(ABC):
    """Template method: defines algorithm skeleton."""

    def process(self, source: str) -> Report:
        """Template method - defines the algorithm."""
        data = self.read_data(source)
        cleaned = self.clean_data(data)
        analyzed = self.analyze(cleaned)
        return self.generate_report(analyzed)

    @abstractmethod
    def read_data(self, source: str) -> RawData:
        """Step 1: Read raw data from source."""
        ...

    def clean_data(self, data: RawData) -> CleanedData:
        """Step 2: Clean data (default implementation)."""
        return CleanedData(data.values)

    @abstractmethod
    def analyze(self, data: CleanedData) -> AnalysisResult:
        """Step 3: Perform analysis."""
        ...

    def generate_report(self, result: AnalysisResult) -> Report:
        """Step 4: Generate report (default implementation)."""
        return Report(result.summary)

class CSVDataProcessor(DataProcessor):
    def read_data(self, source: str) -> RawData:
        import csv
        with open(source) as f:
            reader = csv.reader(f)
            return RawData(list(reader))

    def analyze(self, data: CleanedData) -> AnalysisResult:
        # CSV-specific analysis
        return AnalysisResult(summary={"rows": len(data.values)})

class JSONDataProcessor(DataProcessor):
    def read_data(self, source: str) -> RawData:
        import json
        with open(source) as f:
            return RawData(json.load(f))

    def analyze(self, data: CleanedData) -> AnalysisResult:
        # JSON-specific analysis
        return AnalysisResult(summary={"keys": len(data.values)})

    def generate_report(self, result: AnalysisResult) -> Report:
        # Override to add JSON-specific formatting
        report = super().generate_report(result)
        report.format = "json"
        return report
```

**Applicability:**
- Let clients extend specific steps, not whole algorithm
- Several classes have nearly identical algorithms
- Turn monolithic algorithm into steps

**Consequences:**

| Pros | Cons |
|------|------|
| Clients override only specific parts | Clients may be limited by skeleton |
| Reduce code duplication | Violates Liskov if steps have strict contracts |
| | Template methods tend to be harder to maintain |

---

### Visitor

> Separates algorithms from objects they operate on.

**Problem:**
You need to perform operations on elements of a complex object structure, but adding operations to element classes clutters them.

**Solution:**
Place new operations in visitor classes. The object structure accepts visitors and calls their methods.

**Example:**
```python
from typing import Protocol
from dataclasses import dataclass

class ShapeVisitor(Protocol):
    def visit_circle(self, circle: Circle) -> None: ...
    def visit_rectangle(self, rectangle: Rectangle) -> None: ...
    def visit_triangle(self, triangle: Triangle) -> None: ...

class Shape(Protocol):
    def accept(self, visitor: ShapeVisitor) -> None: ...

@dataclass
class Circle:
    radius: float

    def accept(self, visitor: ShapeVisitor) -> None:
        visitor.visit_circle(self)

@dataclass
class Rectangle:
    width: float
    height: float

    def accept(self, visitor: ShapeVisitor) -> None:
        visitor.visit_rectangle(self)

@dataclass
class Triangle:
    base: float
    height: float

    def accept(self, visitor: ShapeVisitor) -> None:
        visitor.visit_triangle(self)

# Visitors - operations separated from shapes
class AreaCalculator:
    def __init__(self) -> None:
        self.total = 0.0

    def visit_circle(self, circle: Circle) -> None:
        self.total += 3.14159 * circle.radius ** 2

    def visit_rectangle(self, rectangle: Rectangle) -> None:
        self.total += rectangle.width * rectangle.height

    def visit_triangle(self, triangle: Triangle) -> None:
        self.total += 0.5 * triangle.base * triangle.height

class SVGExporter:
    def __init__(self) -> None:
        self.svg_elements: list[str] = []

    def visit_circle(self, circle: Circle) -> None:
        self.svg_elements.append(f'<circle r="{circle.radius}"/>')

    def visit_rectangle(self, rectangle: Rectangle) -> None:
        self.svg_elements.append(
            f'<rect width="{rectangle.width}" height="{rectangle.height}"/>'
        )

    def visit_triangle(self, triangle: Triangle) -> None:
        self.svg_elements.append(f'<polygon points="..."/>')

# Usage
shapes = [Circle(5), Rectangle(4, 3), Triangle(6, 4)]

area_calc = AreaCalculator()
for shape in shapes:
    shape.accept(area_calc)
print(f"Total area: {area_calc.total}")

exporter = SVGExporter()
for shape in shapes:
    shape.accept(exporter)
print("\n".join(exporter.svg_elements))
```

**Applicability:**
- Perform operations on complex object structure
- Clean up business logic with auxiliary behaviors
- Behavior makes sense only in some classes, not hierarchy

**Consequences:**

| Pros | Cons |
|------|------|
| Open/Closed: add operations without changing classes | Must update all visitors when adding new element |
| Single Responsibility | Visitors may lack access to private fields |
| Accumulate state while traversing | |

---

## Pattern Selection Guide

| Problem | Recommended Pattern |
|---------|---------------------|
| Process requests through handlers | Chain of Responsibility |
| Encapsulate requests as objects | Command |
| Traverse collection uniformly | Iterator |
| Reduce direct dependencies | Mediator |
| Save/restore object state | Memento |
| Notify multiple objects of changes | Observer |
| Change behavior based on state | State |
| Select algorithm at runtime | Strategy |
| Define algorithm skeleton with variable steps | Template Method |
| Separate algorithms from objects | Visitor |

---

## Related Skills

- `patterns-creational` - Factory, Builder, Singleton, Prototype patterns
- `patterns-structural` - Adapter, Decorator, Facade, Proxy patterns
- `design-patterns` - Overview of all GoF patterns (deprecated)
