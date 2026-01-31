# AGENTS.md - Coding Standards & Best Practices

## Project Goal

**pypaginate** is an advanced pagination, filtering, and search toolkit for Python. It provides a unified API for paginating data from various sources (in-memory collections, SQLAlchemy, Django ORM, MongoDB, etc.) with support for cursor-based and offset-based pagination, filtering, sorting, and full-text search.

---

## Table of Contents

1. [Core Principles](#core-principles)
2. [Design Patterns](#design-patterns)
3. [Code Smells to Avoid](#code-smells-to-avoid)
4. [Size Limits](#size-limits)
5. [Naming Conventions](#naming-conventions)
6. [Type Hints](#type-hints)
7. [Testing Standards](#testing-standards)
8. [Git Conventions](#git-conventions)
9. [Architecture Guidelines](#architecture-guidelines)
10. [Security Guidelines](#security-guidelines)
11. [Performance Guidelines](#performance-guidelines)
12. [API Design Principles](#api-design-principles)
13. [Refactoring Techniques](#refactoring-techniques)
14. [Code Review Checklist](#code-review-checklist)

---

## Core Principles

### SOLID Principles

#### Single Responsibility Principle (SRP)

A class should have only one reason to change.

```python
# Bad - Multiple responsibilities
class UserManager:
    def create_user(self, data): ...
    def send_email(self, user): ...
    def generate_report(self, users): ...

# Good - Single responsibility
class UserRepository:
    def create(self, data): ...

class EmailService:
    def send(self, recipient, message): ...

class ReportGenerator:
    def generate(self, data): ...
```

#### Open/Closed Principle (OCP)

Open for extension, closed for modification.

```python
# Good - Extensible via abstraction
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def process(self, amount: float) -> bool: ...

class StripeProcessor(PaymentProcessor):
    def process(self, amount: float) -> bool:
        # Stripe-specific implementation
        return True

class PayPalProcessor(PaymentProcessor):
    def process(self, amount: float) -> bool:
        # PayPal-specific implementation
        return True
```

#### Liskov Substitution Principle (LSP)

Subtypes must be substitutable for their base types.

```python
# Good - Subtypes honor the contract
class Bird(ABC):
    @abstractmethod
    def move(self) -> None: ...

class Sparrow(Bird):
    def move(self) -> None:
        self.fly()

class Penguin(Bird):
    def move(self) -> None:
        self.swim()
```

#### Interface Segregation Principle (ISP)

Clients should not depend on interfaces they don't use.

```python
# Bad - Fat interface
class Worker(ABC):
    @abstractmethod
    def work(self): ...
    @abstractmethod
    def eat(self): ...
    @abstractmethod
    def sleep(self): ...

# Good - Segregated interfaces
class Workable(ABC):
    @abstractmethod
    def work(self): ...

class Eatable(ABC):
    @abstractmethod
    def eat(self): ...
```

#### Dependency Inversion Principle (DIP)

Depend on abstractions, not concretions.

```python
# Good - Depends on abstraction
class OrderService:
    def __init__(self, repository: OrderRepository):
        self._repository = repository

    def get_order(self, order_id: str) -> Order:
        return self._repository.find(order_id)
```

### Other Core Principles

| Principle | Description |
|-----------|-------------|
| **KISS** | Keep It Simple, Stupid - Avoid unnecessary complexity |
| **DRY** | Don't Repeat Yourself - Extract common logic |
| **YAGNI** | You Aren't Gonna Need It - Don't build speculative features |
| **SoC** | Separation of Concerns - Divide into distinct sections |
| **Composition > Inheritance** | Favor object composition over class inheritance |
| **Law of Demeter** | Only talk to immediate friends |
| **Fail Fast** | Detect and report errors immediately |
| **POLA** | Principle of Least Astonishment - Behave as expected |
| **Boy Scout Rule** | Leave code cleaner than you found it |

---

## Design Patterns

### Creational Patterns

#### Factory Method

Define an interface for creating objects, let subclasses decide which class to instantiate.

```python
from abc import ABC, abstractmethod

class Document(ABC):
    @abstractmethod
    def render(self) -> str: ...

class PDFDocument(Document):
    def render(self) -> str:
        return "Rendering PDF"

class HTMLDocument(Document):
    def render(self) -> str:
        return "Rendering HTML"

class DocumentFactory(ABC):
    @abstractmethod
    def create_document(self) -> Document: ...

class PDFFactory(DocumentFactory):
    def create_document(self) -> Document:
        return PDFDocument()
```

#### Abstract Factory

Create families of related objects without specifying concrete classes.

```python
class GUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button: ...
    @abstractmethod
    def create_checkbox(self) -> Checkbox: ...

class WindowsFactory(GUIFactory):
    def create_button(self) -> Button:
        return WindowsButton()
    def create_checkbox(self) -> Checkbox:
        return WindowsCheckbox()

class MacFactory(GUIFactory):
    def create_button(self) -> Button:
        return MacButton()
    def create_checkbox(self) -> Checkbox:
        return MacCheckbox()
```

#### Builder

Construct complex objects step by step.

```python
class QueryBuilder:
    def __init__(self):
        self._query = Query()

    def select(self, *fields: str) -> "QueryBuilder":
        self._query.fields = fields
        return self

    def where(self, condition: str) -> "QueryBuilder":
        self._query.conditions.append(condition)
        return self

    def limit(self, count: int) -> "QueryBuilder":
        self._query.limit = count
        return self

    def build(self) -> Query:
        return self._query

# Usage
query = QueryBuilder().select("id", "name").where("active=true").limit(10).build()
```

#### Prototype

Clone existing objects without depending on their classes.

```python
import copy
from abc import ABC, abstractmethod

class Prototype(ABC):
    @abstractmethod
    def clone(self) -> "Prototype": ...

class ConcretePrototype(Prototype):
    def __init__(self, data: dict):
        self.data = data

    def clone(self) -> "ConcretePrototype":
        return copy.deepcopy(self)
```

#### Singleton

Ensure a class has only one instance.

```python
class DatabaseConnection:
    _instance = None

    def __new__(cls) -> "DatabaseConnection":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### Structural Patterns

#### Adapter

Convert interface of a class into another interface clients expect.

```python
class LegacyPrinter:
    def print_document(self, text: str) -> None:
        print(f"Legacy: {text}")

class ModernPrinter(ABC):
    @abstractmethod
    def print(self, content: str) -> None: ...

class PrinterAdapter(ModernPrinter):
    def __init__(self, legacy: LegacyPrinter):
        self._legacy = legacy

    def print(self, content: str) -> None:
        self._legacy.print_document(content)
```

#### Bridge

Separate abstraction from implementation.

```python
class Renderer(ABC):
    @abstractmethod
    def render_circle(self, radius: float) -> str: ...

class VectorRenderer(Renderer):
    def render_circle(self, radius: float) -> str:
        return f"Drawing circle with radius {radius} as vectors"

class Shape(ABC):
    def __init__(self, renderer: Renderer):
        self.renderer = renderer

class Circle(Shape):
    def __init__(self, renderer: Renderer, radius: float):
        super().__init__(renderer)
        self.radius = radius

    def draw(self) -> str:
        return self.renderer.render_circle(self.radius)
```

#### Composite

Compose objects into tree structures.

```python
class Component(ABC):
    @abstractmethod
    def operation(self) -> str: ...

class Leaf(Component):
    def __init__(self, name: str):
        self.name = name

    def operation(self) -> str:
        return self.name

class Composite(Component):
    def __init__(self):
        self._children: list[Component] = []

    def add(self, component: Component) -> None:
        self._children.append(component)

    def operation(self) -> str:
        results = [child.operation() for child in self._children]
        return f"Branch({', '.join(results)})"
```

#### Decorator

Attach additional responsibilities dynamically.

```python
class DataSource(ABC):
    @abstractmethod
    def read(self) -> str: ...
    @abstractmethod
    def write(self, data: str) -> None: ...

class FileDataSource(DataSource):
    def read(self) -> str:
        return "file content"
    def write(self, data: str) -> None:
        pass

class DataSourceDecorator(DataSource):
    def __init__(self, source: DataSource):
        self._source = source

    def read(self) -> str:
        return self._source.read()

    def write(self, data: str) -> None:
        self._source.write(data)

class EncryptionDecorator(DataSourceDecorator):
    def read(self) -> str:
        return self._decrypt(self._source.read())

    def write(self, data: str) -> None:
        self._source.write(self._encrypt(data))

    def _encrypt(self, data: str) -> str:
        return f"encrypted({data})"

    def _decrypt(self, data: str) -> str:
        return data.replace("encrypted(", "").rstrip(")")
```

#### Facade

Provide a simplified interface to a complex subsystem.

```python
class VideoConverter:
    def convert(self, filename: str, format: str) -> str:
        # Hides complexity of codec, bitrate, audio mixing, etc.
        file = VideoFile(filename)
        codec = CodecFactory.extract(file)
        result = BitrateReader.convert(file, codec)
        return AudioMixer.fix(result)
```

#### Flyweight

Share common state between multiple objects.

```python
class TreeType:
    """Flyweight - shared intrinsic state"""
    def __init__(self, name: str, color: str, texture: str):
        self.name = name
        self.color = color
        self.texture = texture

class TreeFactory:
    _types: dict[str, TreeType] = {}

    @classmethod
    def get_tree_type(cls, name: str, color: str, texture: str) -> TreeType:
        key = f"{name}_{color}_{texture}"
        if key not in cls._types:
            cls._types[key] = TreeType(name, color, texture)
        return cls._types[key]

class Tree:
    """Context - unique extrinsic state"""
    def __init__(self, x: int, y: int, tree_type: TreeType):
        self.x = x
        self.y = y
        self.type = tree_type
```

#### Proxy

Provide a surrogate or placeholder for another object.

```python
class Service(ABC):
    @abstractmethod
    def request(self) -> str: ...

class RealService(Service):
    def request(self) -> str:
        return "Real service response"

class CachingProxy(Service):
    def __init__(self, service: Service):
        self._service = service
        self._cache: str | None = None

    def request(self) -> str:
        if self._cache is None:
            self._cache = self._service.request()
        return self._cache
```

### Behavioral Patterns

#### Chain of Responsibility

Pass requests along a chain of handlers.

```python
class Handler(ABC):
    def __init__(self):
        self._next: Handler | None = None

    def set_next(self, handler: "Handler") -> "Handler":
        self._next = handler
        return handler

    def handle(self, request: str) -> str | None:
        if self._next:
            return self._next.handle(request)
        return None

class AuthHandler(Handler):
    def handle(self, request: str) -> str | None:
        if "auth" in request:
            return "Authenticated"
        return super().handle(request)
```

#### Command

Encapsulate a request as an object.

```python
class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...
    @abstractmethod
    def undo(self) -> None: ...

class InsertTextCommand(Command):
    def __init__(self, editor: Editor, text: str):
        self._editor = editor
        self._text = text

    def execute(self) -> None:
        self._editor.insert(self._text)

    def undo(self) -> None:
        self._editor.delete(len(self._text))
```

#### Iterator

Access elements sequentially without exposing underlying representation.

```python
from collections.abc import Iterator, Iterable

class AlphabeticalIterator(Iterator[str]):
    def __init__(self, collection: list[str], reverse: bool = False):
        self._collection = sorted(collection, reverse=reverse)
        self._position = 0

    def __next__(self) -> str:
        if self._position >= len(self._collection):
            raise StopIteration
        value = self._collection[self._position]
        self._position += 1
        return value

class WordsCollection(Iterable[str]):
    def __init__(self):
        self._items: list[str] = []

    def __iter__(self) -> AlphabeticalIterator:
        return AlphabeticalIterator(self._items)
```

#### Mediator

Define an object that encapsulates how objects interact.

```python
class Mediator(ABC):
    @abstractmethod
    def notify(self, sender: object, event: str) -> None: ...

class AuthMediator(Mediator):
    def __init__(self):
        self.login_form = LoginForm(self)
        self.login_button = LoginButton(self)

    def notify(self, sender: object, event: str) -> None:
        if event == "login_clicked":
            self._validate_and_login()

class Component:
    def __init__(self, mediator: Mediator):
        self._mediator = mediator
```

#### Memento

Capture and restore an object's internal state.

```python
class EditorMemento:
    def __init__(self, content: str, cursor: int):
        self._content = content
        self._cursor = cursor

    def get_state(self) -> tuple[str, int]:
        return self._content, self._cursor

class Editor:
    def __init__(self):
        self._content = ""
        self._cursor = 0

    def save(self) -> EditorMemento:
        return EditorMemento(self._content, self._cursor)

    def restore(self, memento: EditorMemento) -> None:
        self._content, self._cursor = memento.get_state()
```

#### Observer

Define a subscription mechanism to notify multiple objects.

```python
class Subject(ABC):
    @abstractmethod
    def attach(self, observer: "Observer") -> None: ...
    @abstractmethod
    def detach(self, observer: "Observer") -> None: ...
    @abstractmethod
    def notify(self) -> None: ...

class Observer(ABC):
    @abstractmethod
    def update(self, subject: Subject) -> None: ...

class EventManager(Subject):
    def __init__(self):
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self) -> None:
        for observer in self._observers:
            observer.update(self)
```

#### State

Alter behavior when internal state changes.

```python
class State(ABC):
    @abstractmethod
    def handle(self, context: "Context") -> None: ...

class ConcreteStateA(State):
    def handle(self, context: "Context") -> None:
        context.state = ConcreteStateB()

class ConcreteStateB(State):
    def handle(self, context: "Context") -> None:
        context.state = ConcreteStateA()

class Context:
    def __init__(self, state: State):
        self.state = state

    def request(self) -> None:
        self.state.handle(self)
```

#### Strategy

Define a family of algorithms, encapsulate each one.

```python
class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data: list[int]) -> list[int]: ...

class QuickSort(SortStrategy):
    def sort(self, data: list[int]) -> list[int]:
        # Quick sort implementation
        return sorted(data)

class MergeSort(SortStrategy):
    def sort(self, data: list[int]) -> list[int]:
        # Merge sort implementation
        return sorted(data)

class Sorter:
    def __init__(self, strategy: SortStrategy):
        self._strategy = strategy

    def sort(self, data: list[int]) -> list[int]:
        return self._strategy.sort(data)
```

#### Template Method

Define the skeleton of an algorithm, defer steps to subclasses.

```python
class DataMiner(ABC):
    def mine(self, path: str) -> None:
        file = self.open_file(path)
        data = self.extract_data(file)
        parsed = self.parse_data(data)
        self.analyze(parsed)

    @abstractmethod
    def open_file(self, path: str) -> object: ...
    @abstractmethod
    def extract_data(self, file: object) -> str: ...
    @abstractmethod
    def parse_data(self, data: str) -> dict: ...

    def analyze(self, data: dict) -> None:
        # Common analysis logic
        pass
```

#### Visitor

Separate algorithms from the objects on which they operate.

```python
class Visitor(ABC):
    @abstractmethod
    def visit_dot(self, dot: "Dot") -> str: ...
    @abstractmethod
    def visit_circle(self, circle: "Circle") -> str: ...

class Shape(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor) -> str: ...

class Dot(Shape):
    def accept(self, visitor: Visitor) -> str:
        return visitor.visit_dot(self)

class XMLExportVisitor(Visitor):
    def visit_dot(self, dot: Dot) -> str:
        return "<dot/>"

    def visit_circle(self, circle: "Circle") -> str:
        return "<circle/>"
```

---

## Code Smells to Avoid

### Bloaters

| Smell | Description | Solution |
|-------|-------------|----------|
| Long Method | Method too long (>12 lines) | Extract Method |
| Large Class | Class doing too much (>200 lines) | Extract Class |
| Primitive Obsession | Overuse of primitives | Replace with Value Objects |
| Long Parameter List | Too many parameters (>4) | Introduce Parameter Object |
| Data Clumps | Groups of data appearing together | Extract Class |

### Object-Orientation Abusers

| Smell | Description | Solution |
|-------|-------------|----------|
| Switch Statements | Complex switch/if-else chains | Replace with Polymorphism |
| Temporary Field | Fields only used sometimes | Extract Class |
| Refused Bequest | Subclass doesn't use parent methods | Replace with Delegation |
| Alternative Classes | Similar classes, different interfaces | Unify Interface |

### Change Preventers

| Smell | Description | Solution |
|-------|-------------|----------|
| Divergent Change | One class changed for multiple reasons | Extract Class |
| Shotgun Surgery | One change requires many class edits | Move Method/Field |
| Parallel Inheritance | Creating subclass requires another | Merge Hierarchies |

### Dispensables

| Smell | Description | Solution |
|-------|-------------|----------|
| Comments | Excessive comments explaining bad code | Refactor code to be self-documenting |
| Duplicate Code | Same code in multiple places | Extract Method |
| Lazy Class | Class that does too little | Inline Class |
| Data Class | Class with only getters/setters | Move Behavior to Class |
| Dead Code | Unused code | Delete It |
| Speculative Generality | Unused abstractions "just in case" | Collapse Hierarchy |

### Couplers

| Smell | Description | Solution |
|-------|-------------|----------|
| Feature Envy | Method uses another class more than its own | Move Method |
| Inappropriate Intimacy | Classes too intertwined | Move Method/Field |
| Message Chains | Long chains: a.b().c().d() | Hide Delegate |
| Middle Man | Class only delegates | Remove Middle Man |

---

## Size Limits

### Strict Limits (MUST Follow)

| Element | Maximum | Preferred |
|---------|---------|-----------|
| **File** | 200 lines | 150 lines |
| **Function/Method** | 12 lines | 10 lines |
| **Class** | 200 lines | 150 lines |
| **Parameters** | 4 | 3 |
| **Nesting Depth** | 3 levels | 2 levels |
| **Line Length** | 88 chars | 80 chars |
| **Cyclomatic Complexity** | 10 | 7 |

### Enforcement

```toml
# pyproject.toml
[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = ["C901"]  # McCabe complexity

[tool.ruff.lint.mccabe]
max-complexity = 10
```

---

## Naming Conventions

### General Rules

| Element | Convention | Example |
|---------|------------|---------|
| Classes | PascalCase | `UserRepository` |
| Functions/Methods | snake_case | `get_user_by_id` |
| Variables | snake_case | `user_count` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Private | Leading underscore | `_internal_method` |
| Protected | Leading underscore | `_protected_attr` |
| Type Variables | Single uppercase or PascalCase | `T`, `KeyType` |
| Modules | snake_case | `user_service.py` |

### Semantic Naming

```python
# Functions - use verbs
def calculate_total() -> float: ...
def is_valid() -> bool: ...
def has_permission() -> bool: ...
def can_execute() -> bool: ...

# Classes - use nouns
class UserRepository: ...
class PaymentProcessor: ...
class EmailValidator: ...

# Booleans - use is/has/can/should prefixes
is_active: bool
has_children: bool
can_edit: bool
should_notify: bool

# Collections - use plural nouns
users: list[User]
active_orders: set[Order]
```

### Avoid

```python
# Bad - Ambiguous names
data = get_data()  # What data?
temp = process()   # Temporary what?
x = calculate()    # What is x?

# Good - Descriptive names
user_profiles = fetch_active_users()
pending_orders = process_checkout_queue()
total_revenue = calculate_monthly_revenue()
```

---

## Type Hints

### Required Type Hints

All public APIs MUST have complete type hints.

```python
from typing import TypeVar, Generic
from collections.abc import Callable, Iterator

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

# Function signatures
def find_user(user_id: str) -> User | None: ...

def process_items(
    items: list[Item],
    filter_fn: Callable[[Item], bool],
) -> Iterator[Item]: ...

# Generic classes
class Repository(Generic[T]):
    def find(self, id: str) -> T | None: ...
    def save(self, entity: T) -> T: ...

# TypedDict for structured dictionaries
from typing import TypedDict

class UserDict(TypedDict):
    id: str
    name: str
    email: str
```

### Type Hint Best Practices

```python
# Use | instead of Union (Python 3.10+)
def get_value(key: str) -> str | None: ...

# Use collections.abc for abstract types
from collections.abc import Mapping, Sequence, Iterable

def process(items: Sequence[int]) -> Mapping[str, int]: ...

# Use Self for return type of instance methods (Python 3.11+)
from typing import Self

class Builder:
    def with_name(self, name: str) -> Self:
        self._name = name
        return self
```

---

## Testing Standards

### Test Structure

```
tests/
├── conftest.py          # Shared fixtures
├── fixtures/            # Test data fixtures
├── factories/           # Test data factories
├── unit/                # Fast, isolated tests
├── integration/         # Database/service tests
├── e2e/                 # End-to-end tests
├── property/            # Property-based tests (Hypothesis)
├── benchmarks/          # Performance tests
└── snapshots/           # Snapshot test data
```

### Test Naming

```python
# Pattern: test_<unit>_<scenario>_<expected_result>
def test_user_creation_with_valid_data_succeeds(): ...
def test_user_creation_with_empty_name_raises_validation_error(): ...
def test_pagination_with_empty_list_returns_zero_pages(): ...
```

### Arrange-Act-Assert (AAA)

```python
def test_order_total_calculation():
    # Arrange
    order = Order()
    order.add_item(Item(price=10.00, quantity=2))
    order.add_item(Item(price=5.00, quantity=1))

    # Act
    total = order.calculate_total()

    # Assert
    assert total == 25.00
```

### Test Types and Markers

```python
import pytest

@pytest.mark.unit
def test_fast_unit_test(): ...

@pytest.mark.integration
def test_database_integration(): ...

@pytest.mark.e2e
def test_full_user_flow(): ...

@pytest.mark.slow
def test_performance_critical(): ...

@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature(): ...
```

### Coverage Requirements

| Type | Minimum Coverage |
|------|-----------------|
| Unit Tests | 90% |
| Integration | 80% |
| Overall | 85% |

---

## Git Conventions

### Branch Naming

| Branch Type | Pattern | Example |
|-------------|---------|---------|
| Main | `main` | Production-ready code |
| Develop | `develop` | Integration branch |
| Feature | `feature/<description>` | `feature/add-cursor-pagination` |
| Fix | `fix/<description>` | `fix/null-pointer-exception` |
| Hotfix | `hotfix/<description>` | `hotfix/security-patch` |
| Release | `release/v<version>` | `release/v1.2.0` |
| Refactor | `refactor/<description>` | `refactor/extract-base-class` |
| Docs | `docs/<description>` | `docs/api-documentation` |
| Test | `test/<description>` | `test/add-e2e-tests` |
| Chore | `chore/<description>` | `chore/update-dependencies` |

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

#### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code change, no feature/fix |
| `perf` | Performance improvement |
| `test` | Adding/fixing tests |
| `build` | Build system changes |
| `ci` | CI configuration changes |
| `chore` | Other changes |
| `revert` | Revert previous commit |

#### Examples

```bash
feat(pagination): add cursor-based pagination support

Implement cursor pagination for large datasets to improve
performance and provide stable pagination results.

Closes #123
```

```bash
fix(filters): handle null values in range filters

Previously, null values caused IndexError. Now they are
filtered out before processing.

Fixes #456
```

---

## Architecture Guidelines

### Layer Architecture

```
┌─────────────────────────────────────┐
│           Presentation              │  ← API endpoints, CLI
├─────────────────────────────────────┤
│           Application               │  ← Use cases, orchestration
├─────────────────────────────────────┤
│             Domain                  │  ← Business logic, entities
├─────────────────────────────────────┤
│          Infrastructure             │  ← Database, external services
└─────────────────────────────────────┘
```

### Dependency Rule

Dependencies point inward. Inner layers know nothing about outer layers.

```python
# Domain layer - no external dependencies
class User:
    def __init__(self, id: str, email: str):
        self.id = id
        self.email = email

# Application layer - depends on domain
class CreateUserUseCase:
    def __init__(self, repository: UserRepository):
        self._repository = repository

    def execute(self, email: str) -> User:
        user = User(id=generate_id(), email=email)
        return self._repository.save(user)

# Infrastructure layer - implements domain interfaces
class SQLAlchemyUserRepository(UserRepository):
    def save(self, user: User) -> User:
        # Database implementation
        pass
```

### Module Organization

```
src/
├── __init__.py
├── core/               # Domain entities and interfaces
│   ├── entities/
│   └── interfaces/
├── application/        # Use cases
│   └── use_cases/
├── infrastructure/     # External implementations
│   ├── database/
│   └── external/
└── presentation/       # API layer
    ├── api/
    └── cli/
```

---

## Security Guidelines

### Input Validation

```python
from pydantic import BaseModel, Field, validator

class UserInput(BaseModel):
    email: str = Field(..., max_length=255)
    name: str = Field(..., min_length=1, max_length=100)

    @validator("email")
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()
```

### SQL Injection Prevention

```python
# Bad - SQL injection vulnerable
query = f"SELECT * FROM users WHERE id = '{user_id}'"

# Good - Parameterized queries
query = "SELECT * FROM users WHERE id = :id"
result = session.execute(text(query), {"id": user_id})
```

### Secrets Management

```python
# Never hardcode secrets
# Bad
API_KEY = "sk-12345abcdef"

# Good - Use environment variables
import os
API_KEY = os.environ["API_KEY"]

# Better - Use secrets management
from your_secrets_lib import get_secret
API_KEY = get_secret("api-key")
```

### Sensitive Data

```python
# Exclude sensitive fields from logs/responses
class User(BaseModel):
    id: str
    email: str
    password_hash: str = Field(exclude=True)

    class Config:
        # Exclude from __repr__
        fields = {"password_hash": {"exclude": True}}
```

---

## Performance Guidelines

### Database Optimization

```python
# Use eager loading to avoid N+1 queries
users = session.query(User).options(
    joinedload(User.orders)
).all()

# Use pagination for large result sets
def get_users(page: int, size: int) -> list[User]:
    return session.query(User).offset(page * size).limit(size).all()

# Index frequently queried columns
class User(Base):
    __tablename__ = "users"
    email = Column(String, index=True)
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_configuration(key: str) -> str:
    # Expensive operation
    return load_from_database(key)

# For async/more control, use explicit cache
class CachedRepository:
    def __init__(self, cache: Cache, repository: Repository):
        self._cache = cache
        self._repository = repository

    def find(self, id: str) -> Entity | None:
        cached = self._cache.get(id)
        if cached:
            return cached
        entity = self._repository.find(id)
        if entity:
            self._cache.set(id, entity)
        return entity
```

### Async Operations

```python
import asyncio
from collections.abc import Coroutine

async def fetch_all(urls: list[str]) -> list[Response]:
    tasks: list[Coroutine] = [fetch(url) for url in urls]
    return await asyncio.gather(*tasks)
```

---

## API Design Principles

### RESTful Conventions

| Method | Endpoint | Action |
|--------|----------|--------|
| GET | `/users` | List users |
| GET | `/users/{id}` | Get user |
| POST | `/users` | Create user |
| PUT | `/users/{id}` | Replace user |
| PATCH | `/users/{id}` | Update user |
| DELETE | `/users/{id}` | Delete user |

### Response Format

```python
# Success response
{
    "data": {...},
    "meta": {
        "page": 1,
        "total": 100
    }
}

# Error response
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input",
        "details": [
            {"field": "email", "message": "Invalid format"}
        ]
    }
}
```

### Versioning

```python
# URL versioning (preferred)
/api/v1/users
/api/v2/users

# Header versioning
Accept: application/vnd.api+json; version=1
```

### Pagination

```python
# Offset-based
GET /users?page=2&size=20

# Cursor-based (preferred for large datasets)
GET /users?cursor=abc123&size=20
```

---

## Refactoring Techniques

### Extract Method

```python
# Before
def process_order(order: Order) -> None:
    # Validate order
    if not order.items:
        raise ValueError("Empty order")
    if order.total < 0:
        raise ValueError("Invalid total")
    # Calculate shipping
    if order.total > 100:
        shipping = 0
    else:
        shipping = 10
    # Process payment
    payment.charge(order.total + shipping)

# After
def process_order(order: Order) -> None:
    validate_order(order)
    shipping = calculate_shipping(order)
    process_payment(order, shipping)

def validate_order(order: Order) -> None:
    if not order.items:
        raise ValueError("Empty order")
    if order.total < 0:
        raise ValueError("Invalid total")

def calculate_shipping(order: Order) -> float:
    return 0 if order.total > 100 else 10

def process_payment(order: Order, shipping: float) -> None:
    payment.charge(order.total + shipping)
```

### Replace Conditional with Polymorphism

```python
# Before
def calculate_area(shape: dict) -> float:
    if shape["type"] == "circle":
        return 3.14 * shape["radius"] ** 2
    elif shape["type"] == "rectangle":
        return shape["width"] * shape["height"]
    else:
        raise ValueError("Unknown shape")

# After
class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return 3.14 * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height
```

### Introduce Parameter Object

```python
# Before
def search_users(
    name: str | None,
    email: str | None,
    age_min: int | None,
    age_max: int | None,
    active: bool | None,
) -> list[User]: ...

# After
@dataclass
class UserSearchCriteria:
    name: str | None = None
    email: str | None = None
    age_min: int | None = None
    age_max: int | None = None
    active: bool | None = None

def search_users(criteria: UserSearchCriteria) -> list[User]: ...
```

---

## Code Review Checklist

### Functionality

- [ ] Code works as intended
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] No obvious bugs

### Code Quality

- [ ] Follows naming conventions
- [ ] Functions are ≤12 lines
- [ ] Files are ≤200 lines
- [ ] No code duplication (DRY)
- [ ] Single responsibility (SRP)
- [ ] No hardcoded values

### Type Safety

- [ ] All public APIs have type hints
- [ ] No `Any` types without justification
- [ ] Generics used appropriately

### Testing

- [ ] Unit tests for new code
- [ ] Edge cases tested
- [ ] Tests are readable (AAA pattern)
- [ ] No flaky tests

### Security

- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] SQL injection prevented
- [ ] Sensitive data protected

### Performance

- [ ] No N+1 queries
- [ ] Appropriate caching
- [ ] No unnecessary computations
- [ ] Large data sets paginated

### Documentation

- [ ] Complex logic explained
- [ ] Public APIs documented
- [ ] README updated if needed

### Git

- [ ] Commit messages follow conventions
- [ ] Commits are atomic
- [ ] No merge conflicts
- [ ] Branch is up to date

---

## Quick Reference

### Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test types
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Lint and format
ruff check .
ruff format .

# Type checking
mypy src/
```

### File Template

```python
"""Module docstring explaining purpose."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

# Constants
MAX_ITEMS = 100

# Classes and functions below...
```

---

*Last updated: 2024*
