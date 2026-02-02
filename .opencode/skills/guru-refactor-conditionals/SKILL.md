---
name: guru-refactor-conditionals
description: >
  RefactoringGuru techniques for simplifying conditional logic: Decompose Conditional,
  Replace Nested Conditional with Guard Clauses, Replace Conditional with Polymorphism,
  Consolidate Conditional Expression, Consolidate Duplicate Conditional Fragments,
  Remove Control Flag, Introduce Null Object, Introduce Assertion.
version: "2.0"
source: refactoring.guru
related:
  - guru-smells
  - guru-refactor-methods
  - guru-patterns-behavioral
  - perf-core
---

## SIMPLIFYING CONDITIONALS

Techniques for simplifying conditional logic.

> **Reference**: [refactoring.guru/refactoring/techniques](https://refactoring.guru/refactoring/techniques)

---

### Decompose Conditional

> Extract complex conditional expressions into methods.

**Before:**
```python
def calculate_charge(date: date, quantity: int) -> float:
    if date < SUMMER_START or date > SUMMER_END:
        charge = quantity * WINTER_RATE + WINTER_SERVICE_CHARGE
    else:
        charge = quantity * SUMMER_RATE
    return charge
```

**After:**
```python
def calculate_charge(date: date, quantity: int) -> float:
    if _is_summer(date):
        return _summer_charge(quantity)
    return _winter_charge(quantity)


def _is_summer(date: date) -> bool:
    return SUMMER_START <= date <= SUMMER_END


def _summer_charge(quantity: int) -> float:
    return quantity * SUMMER_RATE


def _winter_charge(quantity: int) -> float:
    return quantity * WINTER_RATE + WINTER_SERVICE_CHARGE
```

---

### Replace Nested Conditional with Guard Clauses

> Use guard clauses for special cases, leaving the main logic un-nested.

**Before:**
```python
def get_pay_amount(employee: Employee) -> float:
    if employee.is_separated:
        result = separated_amount(employee)
    else:
        if employee.is_retired:
            result = retired_amount(employee)
        else:
            result = normal_amount(employee)
    return result
```

**After:**
```python
def get_pay_amount(employee: Employee) -> float:
    if employee.is_separated:
        return separated_amount(employee)

    if employee.is_retired:
        return retired_amount(employee)

    return normal_amount(employee)
```

---

### Replace Conditional with Polymorphism

> Replace type-checking conditionals with polymorphic behavior.

**Before:**
```python
class Bird:
    def __init__(self, bird_type: str) -> None:
        self.bird_type = bird_type

    def get_speed(self) -> float:
        match self.bird_type:
            case "european":
                return 35.0
            case "african":
                return 40.0
            case "norwegian_blue":
                if self.is_nailed:
                    return 0.0
                return 24.0
        raise ValueError(f"Unknown bird type: {self.bird_type}")
```

**After:**
```python
class Bird(Protocol):
    def get_speed(self) -> float: ...


class EuropeanSwallow:
    def get_speed(self) -> float:
        return 35.0


class AfricanSwallow:
    def get_speed(self) -> float:
        return 40.0


class NorwegianBlueParrot:
    def __init__(self, is_nailed: bool = False) -> None:
        self.is_nailed = is_nailed

    def get_speed(self) -> float:
        if self.is_nailed:
            return 0.0
        return 24.0
```

---

### Consolidate Conditional Expression

> Combine multiple conditionals that lead to the same result.

**When to use:**
- Multiple conditions result in the same action
- Conditions are related and can be combined
- Want to clarify the logic

**Before:**
```python
def disability_amount(employee: Employee) -> float:
    if employee.seniority < 2:
        return 0
    if employee.months_disabled > 12:
        return 0
    if employee.is_part_time:
        return 0
    # Calculate disability amount...
    return base_disability_amount()
```

**After:**
```python
def disability_amount(employee: Employee) -> float:
    if _is_not_eligible_for_disability(employee):
        return 0
    return base_disability_amount()


def _is_not_eligible_for_disability(employee: Employee) -> bool:
    return (
        employee.seniority < 2
        or employee.months_disabled > 12
        or employee.is_part_time
    )
```

---

### Consolidate Duplicate Conditional Fragments

> Move identical code outside of conditional branches.

**When to use:**
- Same code appears in all branches
- Code is duplicated before or after branches

**Before:**
```python
def calculate_price(is_special: bool) -> float:
    if is_special:
        total = price * 0.95
        send_notification()
    else:
        total = price * 0.98
        send_notification()
    return total
```

**After:**
```python
def calculate_price(is_special: bool) -> float:
    if is_special:
        total = price * 0.95
    else:
        total = price * 0.98
    send_notification()  # Moved outside
    return total
```

---

### Remove Control Flag

> Replace a control flag with break, return, or restructured logic.

**When to use:**
- Boolean variable controls loop flow
- Hard to understand when loop ends
- Flag obscures the real exit condition

**Before:**
```python
def check_security(users: list[str]) -> bool:
    found = False
    for user in users:
        if not found:
            if user == "Don":
                send_alert()
                found = True
            if user == "John":
                send_alert()
                found = True
    return found
```

**After:**
```python
def check_security(users: list[str]) -> bool:
    for user in users:
        if user in ("Don", "John"):
            send_alert()
            return True
    return False
```

---

### Introduce Null Object

> Replace null checks with a special null object.

**When to use:**
- Frequent null/None checks throughout code
- Default behavior exists when object is absent
- Want to simplify client code

**Before:**
```python
class Customer:
    def __init__(self, name: str, plan: BillingPlan) -> None:
        self.name = name
        self.plan = plan


def get_billing_plan(customer: Customer | None) -> BillingPlan:
    if customer is None:
        return BillingPlan.basic()
    return customer.plan


def get_customer_name(customer: Customer | None) -> str:
    if customer is None:
        return "Occupant"
    return customer.name
```

**After:**
```python
class Customer(Protocol):
    name: str
    plan: BillingPlan


class RealCustomer:
    def __init__(self, name: str, plan: BillingPlan) -> None:
        self.name = name
        self.plan = plan


class NullCustomer:
    """Null object with sensible defaults."""
    name: str = "Occupant"
    plan: BillingPlan = BillingPlan.basic()


# Client code - no more null checks!
def get_billing_plan(customer: Customer) -> BillingPlan:
    return customer.plan


def get_customer_name(customer: Customer) -> str:
    return customer.name
```

---

### Introduce Assertion

> Add assertions to document and verify assumptions.

**When to use:**
- Code assumes certain conditions are true
- Assumptions are not obvious from the code
- Want to fail fast during development

**Before:**
```python
def get_expense_limit(employee: Employee) -> float:
    # Assumes employee has either expense limit or primary project
    if employee.expense_limit is not None:
        return employee.expense_limit
    return employee.primary_project.expense_limit
```

**After:**
```python
def get_expense_limit(employee: Employee) -> float:
    assert (
        employee.expense_limit is not None
        or employee.primary_project is not None
    ), "Employee must have expense limit or primary project"

    if employee.expense_limit is not None:
        return employee.expense_limit
    return employee.primary_project.expense_limit
```

---

## Quick Reference

| Technique | When to Use |
|-----------|-------------|
| Decompose Conditional | Complex condition expressions |
| Replace Nested Conditional with Guard Clauses | Deep nesting, special cases |
| Replace Conditional with Polymorphism | Type-checking switch statements |
| Consolidate Conditional Expression | Multiple conditions, same result |
| Consolidate Duplicate Conditional Fragments | Same code in all branches |
| Remove Control Flag | Boolean flags controlling loops |
| Introduce Null Object | Frequent null checks |
| Introduce Assertion | Document assumptions, fail fast |

## Patterns by Code Smell

| Code Smell | Recommended Technique |
|------------|----------------------|
| Long Method (with conditionals) | Decompose Conditional |
| Arrow Code (deep nesting) | Replace Nested Conditional with Guard Clauses |
| Switch Statements | Replace Conditional with Polymorphism |
| Duplicated Code (in branches) | Consolidate Duplicate Conditional Fragments |
| Null Checks everywhere | Introduce Null Object |

## Related Skills

- `guru-smells` - Conditional-related code smells
- `guru-patterns-behavioral` - Strategy pattern for polymorphism
