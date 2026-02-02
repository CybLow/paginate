---
name: guru-refactor-data
description: >
  RefactoringGuru techniques for organizing data: Replace Magic Number with Constant,
  Encapsulate Collection, Replace Type Code with Class, Self Encapsulate Field,
  Replace Data Value with Object, Change Value to Reference, Change Reference to Value,
  Replace Array with Object, Encapsulate Field, Replace Type Code with Subclasses,
  Replace Type Code with State/Strategy, Replace Subclass with Fields.
version: "2.0"
source: refactoring.guru
related:
  - guru-smells
  - guru-refactor-methods
  - arch-ddd
  - type-hints
---

## ORGANIZING DATA

Techniques for handling data organization.

> **Reference**: [refactoring.guru/refactoring/techniques](https://refactoring.guru/refactoring/techniques)

---

### Replace Magic Number with Constant

> Replace magic literals with named constants.

**Before:**
```python
def calculate_price(quantity: int, unit_price: float) -> float:
    return quantity * unit_price * 1.1  # What's 1.1?
```

**After:**
```python
TAX_RATE = 0.1
TAX_MULTIPLIER = 1 + TAX_RATE

def calculate_price(quantity: int, unit_price: float) -> float:
    return quantity * unit_price * TAX_MULTIPLIER
```

---

### Encapsulate Collection

> Return a copy or read-only view of a collection instead of the collection itself.

**Before:**
```python
class Course:
    def __init__(self) -> None:
        self._students: list[Student] = []

    def get_students(self) -> list[Student]:
        return self._students  # Caller can modify!
```

**After:**
```python
class Course:
    def __init__(self) -> None:
        self._students: list[Student] = []

    def get_students(self) -> tuple[Student, ...]:
        return tuple(self._students)  # Immutable copy

    def add_student(self, student: Student) -> None:
        self._students.append(student)

    def remove_student(self, student: Student) -> None:
        self._students.remove(student)

    def student_count(self) -> int:
        return len(self._students)
```

---

### Replace Type Code with Class

> Replace primitive type codes with proper classes.

**Before:**
```python
class Employee:
    ENGINEER = 0
    SALESMAN = 1
    MANAGER = 2

    def __init__(self, type_code: int) -> None:
        self.type_code = type_code

    def get_bonus(self) -> float:
        match self.type_code:
            case Employee.ENGINEER:
                return 1000
            case Employee.SALESMAN:
                return 2000
            case Employee.MANAGER:
                return 5000
```

**After:**
```python
from enum import Enum

class EmployeeType(Enum):
    ENGINEER = "engineer"
    SALESMAN = "salesman"
    MANAGER = "manager"

    def get_bonus(self) -> float:
        bonuses = {
            EmployeeType.ENGINEER: 1000,
            EmployeeType.SALESMAN: 2000,
            EmployeeType.MANAGER: 5000,
        }
        return bonuses[self]


class Employee:
    def __init__(self, employee_type: EmployeeType) -> None:
        self.employee_type = employee_type

    def get_bonus(self) -> float:
        return self.employee_type.get_bonus()
```

---

### Self Encapsulate Field

> Access a field through getter/setter even within the class.

**When to use:**
- Subclasses need to override access to the field
- Want to add lazy initialization or validation
- Preparing for more complex access logic

**Before:**
```python
class Range:
    def __init__(self, low: int, high: int) -> None:
        self.low = low
        self.high = high

    def includes(self, value: int) -> bool:
        return self.low <= value <= self.high
```

**After:**
```python
class Range:
    def __init__(self, low: int, high: int) -> None:
        self._low = low
        self._high = high

    @property
    def low(self) -> int:
        return self._low

    @property
    def high(self) -> int:
        return self._high

    def includes(self, value: int) -> bool:
        return self.low <= value <= self.high  # Uses properties
```

---

### Replace Data Value with Object

> Replace a primitive with a rich object that adds behavior.

**When to use:**
- Primitive has associated behavior or validation
- Same primitive used with same logic in multiple places
- Primitive represents a domain concept

**Before:**
```python
class Order:
    def __init__(self, customer_name: str) -> None:
        self.customer_name = customer_name  # Just a string

# Validation logic scattered
if "@" in order.customer_name:  # Is it email or name?
    ...
```

**After:**
```python
@dataclass(frozen=True)
class Customer:
    name: str
    email: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Customer name cannot be empty")


class Order:
    def __init__(self, customer: Customer) -> None:
        self.customer = customer  # Rich object
```

---

### Change Value to Reference

> Convert a value object to a reference object.

**When to use:**
- Multiple objects should share the same instance
- Need to synchronize changes across all references
- Object represents an entity (not just a value)

**Before:**
```python
# Each order has its own Customer instance (value)
order1 = Order(Customer("John", "john@example.com"))
order2 = Order(Customer("John", "john@example.com"))  # Duplicate!

# Changes don't propagate
order1.customer.email = "new@example.com"
print(order2.customer.email)  # Still "john@example.com"
```

**After:**
```python
# Customer registry (reference objects)
class CustomerRegistry:
    _customers: dict[str, Customer] = {}

    @classmethod
    def get(cls, customer_id: str) -> Customer:
        return cls._customers[customer_id]

    @classmethod
    def register(cls, customer: Customer) -> None:
        cls._customers[customer.id] = customer

# Both orders share the same Customer instance
customer = Customer("cust_1", "John", "john@example.com")
CustomerRegistry.register(customer)

order1 = Order(CustomerRegistry.get("cust_1"))
order2 = Order(CustomerRegistry.get("cust_1"))  # Same instance!
```

---

### Change Reference to Value

> Convert a reference object to a value object.

**When to use:**
- Object is small and immutable
- Object identity doesn't matter, only its values
- Want simpler comparison semantics

**Before:**
```python
class Money:
    def __init__(self, amount: int, currency: str) -> None:
        self.amount = amount
        self.currency = currency

# Reference equality fails
m1 = Money(100, "USD")
m2 = Money(100, "USD")
print(m1 == m2)  # False - different objects!
```

**After:**
```python
@dataclass(frozen=True)  # Immutable value object
class Money:
    amount: int
    currency: str

    def add(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(self.amount + other.amount, self.currency)

# Value equality works
m1 = Money(100, "USD")
m2 = Money(100, "USD")
print(m1 == m2)  # True - same values!
```

---

### Replace Array with Object

> Replace an array with an object with named fields.

**When to use:**
- Array elements have different meanings
- Hard to remember what each index represents
- Elements have different types

**Before:**
```python
# What does each index mean?
performance = ["Liverpool", 15, 5]  # Team, wins, losses

name = performance[0]
wins = performance[1]
losses = performance[2]
```

**After:**
```python
@dataclass
class Performance:
    team_name: str
    wins: int
    losses: int

    @property
    def win_rate(self) -> float:
        total = self.wins + self.losses
        return self.wins / total if total > 0 else 0.0

performance = Performance("Liverpool", 15, 5)
print(performance.team_name)  # Clear!
```

---

### Encapsulate Field

> Make a public field private and provide accessors.

**When to use:**
- Need to add validation or transformation
- Want to maintain invariants
- Preparing for computed properties

**Before:**
```python
class Person:
    def __init__(self, name: str) -> None:
        self.name = name  # Public, no validation

person.name = ""  # Oops, invalid!
```

**After:**
```python
class Person:
    def __init__(self, name: str) -> None:
        self._name = ""
        self.name = name  # Uses setter

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value.strip():
            raise ValueError("Name cannot be empty")
        self._name = value.strip()
```

---

### Replace Type Code with Subclasses

> Replace type codes with subclasses.

**When to use:**
- Type code affects behavior (not just data)
- Different types have different methods
- Want to use polymorphism

**Before:**
```python
class Employee:
    ENGINEER = "engineer"
    MANAGER = "manager"

    def __init__(self, type_code: str) -> None:
        self.type_code = type_code

    def get_bonus(self) -> float:
        if self.type_code == Employee.ENGINEER:
            return 1000
        elif self.type_code == Employee.MANAGER:
            return 5000
        return 0
```

**After:**
```python
class Employee:
    def get_bonus(self) -> float:
        return 0


class Engineer(Employee):
    def get_bonus(self) -> float:
        return 1000


class Manager(Employee):
    def get_bonus(self) -> float:
        return 5000


# Factory to create correct subclass
def create_employee(type_code: str) -> Employee:
    match type_code:
        case "engineer":
            return Engineer()
        case "manager":
            return Manager()
        case _:
            return Employee()
```

---

### Replace Type Code with State/Strategy

> Replace type code with a State or Strategy object.

**When to use:**
- Type code changes at runtime
- Can't use subclasses (type changes during object lifetime)
- Type code affects multiple methods

**Before:**
```python
class Employee:
    def __init__(self, type_code: str) -> None:
        self.type_code = type_code

    def promote(self) -> None:
        if self.type_code == "engineer":
            self.type_code = "senior_engineer"
        elif self.type_code == "senior_engineer":
            self.type_code = "manager"

    def get_bonus(self) -> float:
        match self.type_code:
            case "engineer":
                return 1000
            case "senior_engineer":
                return 2000
            case "manager":
                return 5000
```

**After:**
```python
class EmployeeType(Protocol):
    def get_bonus(self) -> float: ...
    def get_next_level(self) -> EmployeeType: ...


class Engineer:
    def get_bonus(self) -> float:
        return 1000

    def get_next_level(self) -> EmployeeType:
        return SeniorEngineer()


class SeniorEngineer:
    def get_bonus(self) -> float:
        return 2000

    def get_next_level(self) -> EmployeeType:
        return Manager()


class Manager:
    def get_bonus(self) -> float:
        return 5000

    def get_next_level(self) -> EmployeeType:
        return self  # Already at top


class Employee:
    def __init__(self, employee_type: EmployeeType) -> None:
        self._type = employee_type

    def promote(self) -> None:
        self._type = self._type.get_next_level()

    def get_bonus(self) -> float:
        return self._type.get_bonus()
```

---

### Replace Subclass with Fields

> Replace subclasses that differ only in constant data with fields.

**When to use:**
- Subclasses only return different constant values
- No polymorphic behavior, just data differences
- Hierarchy adds complexity without benefit

**Before:**
```python
class Person:
    def get_code(self) -> str:
        raise NotImplementedError


class Male(Person):
    def get_code(self) -> str:
        return "M"


class Female(Person):
    def get_code(self) -> str:
        return "F"
```

**After:**
```python
class Person:
    def __init__(self, code: str) -> None:
        self._code = code

    def get_code(self) -> str:
        return self._code

    @classmethod
    def create_male(cls) -> Person:
        return cls("M")

    @classmethod
    def create_female(cls) -> Person:
        return cls("F")
```

---

## Quick Reference

| Technique | When to Use |
|-----------|-------------|
| Replace Magic Number with Constant | Unexplained literals in code |
| Encapsulate Collection | Prevent external mutation of collections |
| Replace Type Code with Class | Primitive type codes without behavior |
| Self Encapsulate Field | Need access control within class |
| Replace Data Value with Object | Primitive needs behavior/validation |
| Change Value to Reference | Need shared instances |
| Change Reference to Value | Small immutable objects |
| Replace Array with Object | Array elements have different meanings |
| Encapsulate Field | Need validation on field access |
| Replace Type Code with Subclasses | Type affects behavior, fixed at creation |
| Replace Type Code with State/Strategy | Type affects behavior, changes at runtime |
| Replace Subclass with Fields | Subclasses differ only in constants |

## Related Skills

- `guru-smells` - Primitive Obsession and other data smells
- `guru-refactor-generalization` - Inheritance techniques
