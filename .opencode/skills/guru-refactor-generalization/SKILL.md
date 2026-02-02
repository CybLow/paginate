---
name: guru-refactor-generalization
description: >
  RefactoringGuru techniques for managing inheritance hierarchies: Pull Up Field/Method,
  Pull Up Constructor Body, Push Down Field/Method, Extract Subclass/Superclass/Interface,
  Collapse Hierarchy, Form Template Method, Replace Inheritance with Delegation,
  Replace Delegation with Inheritance.
version: "2.0"
source: refactoring.guru
related:
  - guru-smells
  - guru-refactor-moving
  - guru-patterns-behavioral
  - type-hints
---

## DEALING WITH GENERALIZATION

Techniques for managing inheritance hierarchies.

> **Reference**: [refactoring.guru/refactoring/techniques](https://refactoring.guru/refactoring/techniques)

---

### Pull Up Field

> Move a field from subclasses to the superclass.

**When to use:**
- Same field exists in multiple subclasses
- Field has same name and type across subclasses
- Want to eliminate duplication

**Before:**
```python
class Salesman(Employee):
    def __init__(self, name: str) -> None:
        self.name = name


class Engineer(Employee):
    def __init__(self, name: str) -> None:
        self.name = name  # Duplicated!
```

**After:**
```python
class Employee:
    def __init__(self, name: str) -> None:
        self.name = name


class Salesman(Employee):
    pass


class Engineer(Employee):
    pass
```

---

### Pull Up Method

> Move a method from subclasses to the superclass.

**When to use:**
- Same method exists in multiple subclasses
- Method implementations are identical
- Method is part of common interface

**Before:**
```python
class Salesman(Employee):
    def get_name(self) -> str:
        return self.name


class Engineer(Employee):
    def get_name(self) -> str:  # Identical!
        return self.name
```

**After:**
```python
class Employee:
    def get_name(self) -> str:
        return self.name


class Salesman(Employee):
    pass


class Engineer(Employee):
    pass
```

---

### Pull Up Constructor Body

> Move common constructor logic to the superclass.

**When to use:**
- Subclass constructors have common code
- Common code should be in superclass

**Before:**
```python
class Employee:
    pass


class Manager(Employee):
    def __init__(self, name: str, grade: int) -> None:
        self.name = name
        self.grade = grade


class Salesman(Employee):
    def __init__(self, name: str, region: str) -> None:
        self.name = name  # Duplicated
        self.region = region
```

**After:**
```python
class Employee:
    def __init__(self, name: str) -> None:
        self.name = name


class Manager(Employee):
    def __init__(self, name: str, grade: int) -> None:
        super().__init__(name)
        self.grade = grade


class Salesman(Employee):
    def __init__(self, name: str, region: str) -> None:
        super().__init__(name)
        self.region = region
```

---

### Push Down Method

> Move a method from superclass to specific subclasses.

**When to use:**
- Method is only relevant to some subclasses
- Method was in superclass for convenience
- Want to clarify hierarchy

**Before:**
```python
class Employee:
    def get_quota(self) -> float:  # Only relevant for Salesman
        raise NotImplementedError


class Engineer(Employee):
    def get_quota(self) -> float:
        raise NotImplementedError  # Makes no sense here!


class Salesman(Employee):
    def get_quota(self) -> float:
        return self.quota
```

**After:**
```python
class Employee:
    pass


class Engineer(Employee):
    pass  # No quota method


class Salesman(Employee):
    def get_quota(self) -> float:
        return self.quota
```

---

### Push Down Field

> Move a field from superclass to specific subclasses.

**When to use:**
- Field is only used by some subclasses
- Field doesn't belong in superclass
- Want to clarify responsibilities

**Before:**
```python
class Employee:
    quota: float  # Only Salesman uses this


class Engineer(Employee):
    pass  # Has quota but doesn't use it


class Salesman(Employee):
    pass
```

**After:**
```python
class Employee:
    pass


class Engineer(Employee):
    pass


class Salesman(Employee):
    quota: float
```

---

### Extract Subclass

> Create a subclass for a subset of features.

**When to use:**
- Class has features used only in some cases
- Features are based on type codes
- Want to separate concerns

**Before:**
```python
class JobItem:
    def __init__(
        self,
        unit_price: float,
        quantity: int,
        is_labor: bool,
        employee: Employee | None = None,
    ) -> None:
        self.unit_price = unit_price
        self.quantity = quantity
        self.is_labor = is_labor
        self.employee = employee  # Only for labor items

    def get_total_price(self) -> float:
        return self.unit_price * self.quantity

    def get_unit_price(self) -> float:
        if self.is_labor:
            return self.employee.rate
        return self.unit_price
```

**After:**
```python
class JobItem:
    def __init__(self, unit_price: float, quantity: int) -> None:
        self.unit_price = unit_price
        self.quantity = quantity

    def get_total_price(self) -> float:
        return self.get_unit_price() * self.quantity

    def get_unit_price(self) -> float:
        return self.unit_price


class LaborItem(JobItem):
    def __init__(self, quantity: int, employee: Employee) -> None:
        super().__init__(0, quantity)
        self.employee = employee

    def get_unit_price(self) -> float:
        return self.employee.rate
```

---

### Extract Superclass

> Create a superclass for common features.

**When to use:**
- Multiple classes have similar features
- Want to share code through inheritance
- Common abstraction exists

**Before:**
```python
class Employee:
    def __init__(self, name: str, annual_cost: float) -> None:
        self.name = name
        self.annual_cost = annual_cost


class Department:
    def __init__(self, name: str, staff: list[Employee]) -> None:
        self.name = name
        self.staff = staff

    @property
    def annual_cost(self) -> float:
        return sum(e.annual_cost for e in self.staff)
```

**After:**
```python
class Party:
    """Common superclass."""
    def __init__(self, name: str) -> None:
        self.name = name

    @property
    def annual_cost(self) -> float:
        raise NotImplementedError


class Employee(Party):
    def __init__(self, name: str, annual_cost: float) -> None:
        super().__init__(name)
        self._annual_cost = annual_cost

    @property
    def annual_cost(self) -> float:
        return self._annual_cost


class Department(Party):
    def __init__(self, name: str, staff: list[Employee]) -> None:
        super().__init__(name)
        self.staff = staff

    @property
    def annual_cost(self) -> float:
        return sum(e.annual_cost for e in self.staff)
```

---

### Extract Interface

> Create an interface (Protocol) from a class's methods.

**When to use:**
- Multiple classes share same interface
- Want to enable polymorphism
- Defining contracts

**Before:**
```python
class Employee:
    def get_rate(self) -> float: ...
    def has_special_skill(self) -> bool: ...
    def get_name(self) -> str: ...


# Client is coupled to Employee
def calculate_charge(employee: Employee, hours: int) -> float:
    return employee.get_rate() * hours
```

**After:**
```python
class Billable(Protocol):
    def get_rate(self) -> float: ...
    def has_special_skill(self) -> bool: ...


class Employee:
    def get_rate(self) -> float: ...
    def has_special_skill(self) -> bool: ...
    def get_name(self) -> str: ...


class Contractor:  # Also Billable!
    def get_rate(self) -> float: ...
    def has_special_skill(self) -> bool: ...


# Client uses interface
def calculate_charge(billable: Billable, hours: int) -> float:
    return billable.get_rate() * hours
```

---

### Collapse Hierarchy

> Merge a superclass and subclass when they're too similar.

**When to use:**
- Subclass doesn't add much value
- Distinction between classes is unclear
- Hierarchy adds unnecessary complexity

**Before:**
```python
class Employee:
    def __init__(self, name: str, rate: float) -> None:
        self.name = name
        self.rate = rate


class Salesman(Employee):
    pass  # No additional behavior!
```

**After:**
```python
class Employee:
    def __init__(self, name: str, rate: float, is_salesman: bool = False) -> None:
        self.name = name
        self.rate = rate
        self.is_salesman = is_salesman
```

---

### Form Template Method

> Extract common algorithm structure to superclass, leave variations to subclasses.

**When to use:**
- Subclasses have similar methods with variations
- Same algorithm structure, different details
- Want to eliminate duplication

**Before:**
```python
class Site:
    pass


class ResidentialSite(Site):
    def get_bill_text(self) -> str:
        base = self.units * self.rate
        tax = base * self.TAX_RATE
        return f"Base: {base}, Tax: {tax}, Total: {base + tax}"


class LifelineSite(Site):
    def get_bill_text(self) -> str:
        base = self.units * self.rate * 0.5  # Different calculation
        tax = base * self.TAX_RATE * 0.2  # Different tax
        return f"Base: {base}, Tax: {tax}, Total: {base + tax}"
```

**After:**
```python
class Site:
    def get_bill_text(self) -> str:
        """Template method."""
        base = self.get_base_amount()
        tax = self.get_tax_amount(base)
        return f"Base: {base}, Tax: {tax}, Total: {base + tax}"

    def get_base_amount(self) -> float:
        raise NotImplementedError

    def get_tax_amount(self, base: float) -> float:
        raise NotImplementedError


class ResidentialSite(Site):
    def get_base_amount(self) -> float:
        return self.units * self.rate

    def get_tax_amount(self, base: float) -> float:
        return base * self.TAX_RATE


class LifelineSite(Site):
    def get_base_amount(self) -> float:
        return self.units * self.rate * 0.5

    def get_tax_amount(self, base: float) -> float:
        return base * self.TAX_RATE * 0.2
```

---

### Replace Inheritance with Delegation

> Replace inheritance with composition when subclass doesn't need full interface.

**When to use:**
- Subclass only uses part of superclass
- Subclass breaks Liskov Substitution
- "is-a" relationship doesn't hold

**Before:**
```python
class Stack(list):  # Inherits all list methods!
    def push(self, item: T) -> None:
        self.append(item)

    def pop(self) -> T:
        return super().pop()

# Problem: All list methods are available
stack = Stack()
stack.insert(0, "bad")  # Shouldn't be allowed!
```

**After:**
```python
class Stack:
    def __init__(self) -> None:
        self._items: list[T] = []  # Delegation

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

    def is_empty(self) -> bool:
        return len(self._items) == 0

# Only Stack methods are available
stack = Stack()
# stack.insert(0, "bad")  # Not possible!
```

---

### Replace Delegation with Inheritance

> Replace delegation with inheritance when using most of delegatee's interface.

**When to use:**
- Class delegates almost everything
- Full interface of delegatee is needed
- "is-a" relationship makes sense

**Before:**
```python
class Employee:
    def __init__(self, person: Person) -> None:
        self._person = person

    def get_name(self) -> str:
        return self._person.get_name()

    def get_address(self) -> str:
        return self._person.get_address()

    def get_phone(self) -> str:
        return self._person.get_phone()

    def get_email(self) -> str:
        return self._person.get_email()

    # Every Person method is delegated...
```

**After:**
```python
class Employee(Person):
    def __init__(self, name: str, address: str, phone: str, email: str) -> None:
        super().__init__(name, address, phone, email)

    # Employee-specific methods only
    def get_employee_id(self) -> str:
        return self._employee_id
```

---

## Quick Reference

| Technique | When to Use |
|-----------|-------------|
| Pull Up Field | Same field in multiple subclasses |
| Pull Up Method | Same method in multiple subclasses |
| Pull Up Constructor Body | Common constructor code |
| Push Down Method | Method only relevant to some subclasses |
| Push Down Field | Field only used by some subclasses |
| Extract Subclass | Features used only in some cases |
| Extract Superclass | Multiple classes share features |
| Extract Interface | Define contract for polymorphism |
| Collapse Hierarchy | Subclass adds no value |
| Form Template Method | Same algorithm, different details |
| Replace Inheritance with Delegation | Subclass uses part of parent |
| Replace Delegation with Inheritance | Delegating everything |

## Patterns by Code Smell

| Code Smell | Recommended Technique |
|------------|----------------------|
| Duplicate Code (in siblings) | Pull Up Method |
| Refused Bequest | Push Down Method, Replace Inheritance with Delegation |
| Lazy Class | Collapse Hierarchy, Inline Class |
| Parallel Inheritance | Move Method, Move Field |
| Speculative Generality | Collapse Hierarchy |

## Related Skills

- `guru-smells` - Inheritance-related code smells
- `guru-patterns-behavioral` - Template Method pattern
