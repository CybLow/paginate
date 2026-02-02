---
name: guru-refactor-moving
description: >
  RefactoringGuru techniques for moving features between objects: Move Method, Move Field,
  Extract Class, Inline Class, Hide Delegate, Remove Middle Man, Introduce Foreign Method,
  Introduce Local Extension. Focus on proper responsibility distribution.
version: "2.0"
source: refactoring.guru
related:
  - guru-smells
  - guru-refactor-methods
  - guru-refactor-generalization
  - arch-principles
---

## MOVING FEATURES

Techniques for moving functionality between classes.

> **Reference**: [refactoring.guru/refactoring/techniques](https://refactoring.guru/refactoring/techniques)

---

### Move Method

> Move a method to the class that uses its data most.

**When to use:**
- Method uses more data from another class (Feature Envy)
- Method would be simpler in another class
- Method doesn't belong in current class

**Before:**
```python
class Account:
    def __init__(self, account_type: AccountType, days_overdrawn: int) -> None:
        self.account_type = account_type
        self.days_overdrawn = days_overdrawn

    def overdraft_charge(self) -> float:
        if self.account_type.is_premium:
            result = 10.0
            if self.days_overdrawn > 7:
                result += (self.days_overdrawn - 7) * 0.85
            return result
        return self.days_overdrawn * 1.75
```

**After:**
```python
class Account:
    def __init__(self, account_type: AccountType, days_overdrawn: int) -> None:
        self.account_type = account_type
        self.days_overdrawn = days_overdrawn

    def overdraft_charge(self) -> float:
        return self.account_type.overdraft_charge(self.days_overdrawn)


class AccountType:
    def __init__(self, is_premium: bool) -> None:
        self.is_premium = is_premium

    def overdraft_charge(self, days_overdrawn: int) -> float:
        if self.is_premium:
            result = 10.0
            if days_overdrawn > 7:
                result += (days_overdrawn - 7) * 0.85
            return result
        return days_overdrawn * 1.75
```

---

### Extract Class

> Create a new class and move relevant fields and methods to it.

**When to use:**
- Class has too many responsibilities
- Subset of fields/methods are closely related
- Class is too large (> 200 lines)

**Before:**
```python
class Person:
    def __init__(
        self,
        name: str,
        office_area_code: str,
        office_number: str,
        home_area_code: str,
        home_number: str,
    ) -> None:
        self.name = name
        self.office_area_code = office_area_code
        self.office_number = office_number
        self.home_area_code = home_area_code
        self.home_number = home_number

    def get_office_phone(self) -> str:
        return f"({self.office_area_code}) {self.office_number}"

    def get_home_phone(self) -> str:
        return f"({self.home_area_code}) {self.home_number}"
```

**After:**
```python
@dataclass
class PhoneNumber:
    area_code: str
    number: str

    def format(self) -> str:
        return f"({self.area_code}) {self.number}"


class Person:
    def __init__(
        self,
        name: str,
        office_phone: PhoneNumber,
        home_phone: PhoneNumber,
    ) -> None:
        self.name = name
        self.office_phone = office_phone
        self.home_phone = home_phone
```

---

### Hide Delegate

> Create methods on the server to hide the delegate.

**When to use:**
- Client calls `a.b().c()` (Message Chains smell)
- Want to reduce coupling between client and delegate
- Delegate structure might change

**Before:**
```python
# Client code
manager = employee.department.manager
manager_name = employee.department.manager.name
```

**After:**
```python
class Employee:
    def get_manager(self) -> Employee:
        return self._department.manager

    def get_manager_name(self) -> str:
        return self._department.manager.name


# Client code
manager = employee.get_manager()
manager_name = employee.get_manager_name()
```

---

### Move Field

> Move a field to the class that uses it most.

**When to use:**
- Field is used more by another class
- Field doesn't belong in current class conceptually
- Reducing coupling between classes

**Before:**
```python
class Customer:
    def __init__(self, name: str, discount_rate: float) -> None:
        self.name = name
        self.discount_rate = discount_rate  # Used mainly by Order


class Order:
    def __init__(self, customer: Customer, amount: float) -> None:
        self.customer = customer
        self.amount = amount

    def discounted_amount(self) -> float:
        return self.amount * (1 - self.customer.discount_rate)
```

**After:**
```python
class CustomerType:
    def __init__(self, discount_rate: float) -> None:
        self.discount_rate = discount_rate  # Field moved here


class Customer:
    def __init__(self, name: str, customer_type: CustomerType) -> None:
        self.name = name
        self.customer_type = customer_type

    @property
    def discount_rate(self) -> float:
        return self.customer_type.discount_rate


class Order:
    def __init__(self, customer: Customer, amount: float) -> None:
        self.customer = customer
        self.amount = amount

    def discounted_amount(self) -> float:
        return self.amount * (1 - self.customer.discount_rate)
```

---

### Inline Class

> Merge a class into another class that uses it.

**When to use:**
- Class does too little to justify existence (Lazy Class)
- Class has lost its responsibilities through refactoring
- Merging would simplify the design

**Before:**
```python
class TelephoneNumber:
    def __init__(self, area_code: str, number: str) -> None:
        self.area_code = area_code
        self.number = number


class Person:
    def __init__(self, name: str, telephone: TelephoneNumber) -> None:
        self.name = name
        self._telephone = telephone

    @property
    def area_code(self) -> str:
        return self._telephone.area_code

    @property
    def number(self) -> str:
        return self._telephone.number
```

**After:**
```python
class Person:
    def __init__(self, name: str, area_code: str, number: str) -> None:
        self.name = name
        self.area_code = area_code
        self.number = number
```

---

### Remove Middle Man

> Let the client call the delegate directly.

**When to use:**
- Too many delegating methods (Middle Man smell)
- Server class is just passing calls through
- Direct access to delegate is acceptable

**Before:**
```python
class Employee:
    def __init__(self, department: Department) -> None:
        self._department = department

    def get_manager(self) -> Employee:
        return self._department.manager

    def get_department_name(self) -> str:
        return self._department.name

    def get_department_budget(self) -> float:
        return self._department.budget

    # Many more delegation methods...
```

**After:**
```python
class Employee:
    def __init__(self, department: Department) -> None:
        self.department = department  # Expose directly

# Client accesses delegate directly
manager = employee.department.manager
name = employee.department.name
```

---

### Introduce Foreign Method

> Create a utility method for a class you can't modify.

**When to use:**
- Library class lacks a method you need
- You can't modify the library class
- Only need the method in one or two places

**Before:**
```python
from datetime import date, timedelta

# Same calculation repeated
next_day = date.today() + timedelta(days=1)
# ...
start = end_date + timedelta(days=1)
```

**After:**
```python
from datetime import date, timedelta

def next_day(d: date) -> date:
    """Foreign method for date class."""
    return d + timedelta(days=1)

# Clean usage
tomorrow = next_day(date.today())
start = next_day(end_date)
```

---

### Introduce Local Extension

> Create a subclass or wrapper for a class you can't modify.

**When to use:**
- Library class lacks several methods you need
- Foreign Methods would be scattered everywhere
- Want to encapsulate extensions in one place

**Before:**
```python
from datetime import date, timedelta

# Utility functions scattered across codebase
def next_day(d: date) -> date: ...
def add_months(d: date, months: int) -> date: ...
def is_weekend(d: date) -> bool: ...
def days_until(d: date, target: date) -> int: ...
```

**After:**
```python
from datetime import date, timedelta
from calendar import monthrange


class ExtendedDate(date):
    """Local extension of date with additional methods."""

    def next_day(self) -> ExtendedDate:
        return self._from_date(self + timedelta(days=1))

    def add_months(self, months: int) -> ExtendedDate:
        month = self.month + months
        year = self.year + (month - 1) // 12
        month = (month - 1) % 12 + 1
        day = min(self.day, monthrange(year, month)[1])
        return ExtendedDate(year, month, day)

    def is_weekend(self) -> bool:
        return self.weekday() >= 5

    def days_until(self, target: date) -> int:
        return (target - self).days

    @classmethod
    def _from_date(cls, d: date) -> ExtendedDate:
        return cls(d.year, d.month, d.day)

    @classmethod
    def today_extended(cls) -> ExtendedDate:
        return cls._from_date(date.today())
```

---

## Quick Reference

| Technique | When to Use |
|-----------|-------------|
| Move Method | Feature Envy - method uses other class's data |
| Move Field | Field used more by another class |
| Extract Class | Class has too many responsibilities |
| Inline Class | Lazy Class - does too little |
| Hide Delegate | Message Chains - a.b().c() patterns |
| Remove Middle Man | Too many delegation methods |
| Introduce Foreign Method | Need one method on unmodifiable class |
| Introduce Local Extension | Need many methods on unmodifiable class |

## Related Skills

- `guru-smells` - Code smells these techniques address
- `guru-refactor-methods` - Composing methods
- `guru-refactor-data` - Organizing data
