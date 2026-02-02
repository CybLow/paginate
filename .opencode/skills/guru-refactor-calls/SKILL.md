---
name: guru-refactor-calls
description: >
  RefactoringGuru techniques for simplifying method calls: Rename Method, Separate Query
  from Modifier, Introduce Parameter Object, Add/Remove Parameter, Parameterize Method,
  Replace Parameter with Explicit Methods, Preserve Whole Object, Replace Parameter with
  Method Call, Remove Setting Method, Hide Method, Replace Constructor with Factory Method,
  Replace Error Code with Exception, Replace Exception with Test.
version: "2.0"
source: refactoring.guru
related:
  - guru-smells
  - guru-refactor-methods
  - guru-patterns-creational
  - api-rest
---

## SIMPLIFYING METHOD CALLS

Techniques for making method signatures clearer.

> **Reference**: [refactoring.guru/refactoring/techniques](https://refactoring.guru/refactoring/techniques)

---

### Rename Method

> Give the method a name that reveals its purpose.

**Before:**
```python
def proc(d: dict) -> dict: ...
def handle(x: Any) -> None: ...
def do_it(item: Item) -> Item: ...
```

**After:**
```python
def process_order(order_data: dict) -> dict: ...
def handle_payment_webhook(event: WebhookEvent) -> None: ...
def validate_and_save(item: Item) -> Item: ...
```

---

### Separate Query from Modifier

> Split methods that return data AND change state.

**Before:**
```python
class Stack:
    def pop_and_get_top(self) -> T:
        """Returns top item AND removes it."""
        item = self._items[-1]
        del self._items[-1]
        return item
```

**After:**
```python
class Stack:
    def top(self) -> T:
        """Returns top item (query, no side effect)."""
        return self._items[-1]

    def pop(self) -> None:
        """Removes top item (modifier)."""
        del self._items[-1]

# Usage: get then remove
item = stack.top()
stack.pop()
```

---

### Introduce Parameter Object

> Replace groups of related parameters with an object.

**Before:**
```python
def search_orders(
    start_date: date,
    end_date: date,
    min_total: float,
    max_total: float,
    status: str,
    customer_id: int | None,
) -> list[Order]: ...
```

**After:**
```python
@dataclass
class DateRange:
    start: date
    end: date


@dataclass
class AmountRange:
    min: float | None = None
    max: float | None = None


@dataclass
class OrderSearchCriteria:
    date_range: DateRange
    amount_range: AmountRange | None = None
    status: str | None = None
    customer_id: int | None = None


def search_orders(criteria: OrderSearchCriteria) -> list[Order]: ...
```

---

### Add Parameter

> Add a parameter to pass additional data to a method.

**When to use:**
- Method needs more information to do its job
- Extending method functionality
- Making method more flexible

**Before:**
```python
def get_contact(self) -> str:
    return self.email  # Always returns email
```

**After:**
```python
def get_contact(self, contact_type: str = "email") -> str:
    match contact_type:
        case "email":
            return self.email
        case "phone":
            return self.phone
        case _:
            raise ValueError(f"Unknown contact type: {contact_type}")
```

---

### Remove Parameter

> Remove a parameter that's no longer needed.

**When to use:**
- Parameter is never used in the method body
- Default behavior is always what callers want
- Parameter was added speculatively

**Before:**
```python
def get_discount(customer: Customer, date: date, code: str) -> float:
    # 'date' is never used!
    if code == "VIP":
        return 0.2
    return 0.1
```

**After:**
```python
def get_discount(customer: Customer, code: str) -> float:
    if code == "VIP":
        return 0.2
    return 0.1
```

---

### Parameterize Method

> Combine similar methods by adding a parameter.

**When to use:**
- Multiple methods do similar things with different values
- Methods differ only in a literal value
- Want to reduce duplication

**Before:**
```python
def five_percent_raise(self) -> None:
    self.salary *= 1.05


def ten_percent_raise(self) -> None:
    self.salary *= 1.10
```

**After:**
```python
def raise_salary(self, percentage: float) -> None:
    self.salary *= (1 + percentage / 100)

# Usage
employee.raise_salary(5)
employee.raise_salary(10)
```

---

### Replace Parameter with Explicit Methods

> Split a method that depends on a parameter value into separate methods.

**When to use:**
- Parameter changes behavior significantly
- Limited, discrete set of parameter values
- Separate methods would be clearer

**Before:**
```python
def set_value(self, name: str, value: int) -> None:
    match name:
        case "height":
            self.height = value
        case "width":
            self.width = value
        case _:
            raise ValueError(f"Unknown field: {name}")
```

**After:**
```python
def set_height(self, height: int) -> None:
    self.height = height


def set_width(self, width: int) -> None:
    self.width = width
```

---

### Preserve Whole Object

> Pass the whole object instead of extracting values from it.

**When to use:**
- Extracting multiple values from an object to pass as parameters
- Method might need other values from the object in the future
- Reduces coupling between caller and callee

**Before:**
```python
def is_within_plan(plan: Plan, low: int, high: int) -> bool:
    return plan.within_range(low, high)

# Caller extracts values
result = is_within_plan(plan, room.days_temp_range.low, room.days_temp_range.high)
```

**After:**
```python
def is_within_plan(plan: Plan, temp_range: TempRange) -> bool:
    return plan.within_range(temp_range.low, temp_range.high)

# Caller passes whole object
result = is_within_plan(plan, room.days_temp_range)
```

---

### Replace Parameter with Method Call

> Remove a parameter by having the method get the value itself.

**When to use:**
- Method can obtain the value on its own
- Value is already accessible to the method
- Simplifies the interface

**Before:**
```python
def get_discounted_price(base_price: float, discount_level: int) -> float:
    return base_price * DISCOUNT_TABLE[discount_level]


# Caller
price = get_discounted_price(order.base_price, customer.discount_level)
```

**After:**
```python
class Order:
    def get_discounted_price(self) -> float:
        discount_level = self.customer.discount_level
        return self.base_price * DISCOUNT_TABLE[discount_level]


# Caller - simpler
price = order.get_discounted_price()
```

---

### Remove Setting Method

> Remove a setter when a field should only be set at creation.

**When to use:**
- Field should not change after construction
- Setter is only called in constructor
- Want to enforce immutability

**Before:**
```python
class Employee:
    def __init__(self, id: str) -> None:
        self._id = ""
        self.set_id(id)

    def get_id(self) -> str:
        return self._id

    def set_id(self, id: str) -> None:  # Shouldn't be called after init!
        self._id = id
```

**After:**
```python
class Employee:
    def __init__(self, id: str) -> None:
        self._id = id

    @property
    def id(self) -> str:
        return self._id  # Read-only
```

---

### Hide Method

> Make a public method private when it's only used internally.

**When to use:**
- Method is not used by other classes
- Method was public for testing but tests were refactored
- Reducing public interface

**Before:**
```python
class Account:
    def calculate_balance(self) -> float:  # Public but only used internally
        return sum(t.amount for t in self.transactions)

    def get_statement(self) -> Statement:
        balance = self.calculate_balance()  # Only caller
        return Statement(self.transactions, balance)
```

**After:**
```python
class Account:
    def _calculate_balance(self) -> float:  # Now private
        return sum(t.amount for t in self.transactions)

    def get_statement(self) -> Statement:
        balance = self._calculate_balance()
        return Statement(self.transactions, balance)
```

---

### Replace Constructor with Factory Method

> Replace constructor with a factory method for more flexibility.

**When to use:**
- Constructor logic is complex
- Need to return subtype based on parameters
- Want descriptive creation method names

**Before:**
```python
class Employee:
    def __init__(self, type_code: int) -> None:
        self.type_code = type_code

# Unclear what 0 means
employee = Employee(0)
```

**After:**
```python
class Employee:
    def __init__(self, type_code: int) -> None:
        self._type_code = type_code

    @classmethod
    def create_engineer(cls) -> Employee:
        return cls(0)

    @classmethod
    def create_manager(cls) -> Employee:
        return cls(1)

    @classmethod
    def create_salesman(cls) -> Employee:
        return cls(2)

# Clear intent
employee = Employee.create_engineer()
```

---

### Replace Error Code with Exception

> Replace error codes with exceptions.

**When to use:**
- Method returns special value to indicate error
- Callers must check return value
- Error handling is scattered

**Before:**
```python
def withdraw(self, amount: float) -> int:
    if amount > self.balance:
        return -1  # Error code
    self.balance -= amount
    return 0  # Success

# Caller must check
if account.withdraw(100) == -1:
    print("Insufficient funds")
```

**After:**
```python
class InsufficientFundsError(Exception):
    pass


def withdraw(self, amount: float) -> None:
    if amount > self.balance:
        raise InsufficientFundsError(f"Cannot withdraw {amount}, balance is {self.balance}")
    self.balance -= amount


# Caller uses exception handling
try:
    account.withdraw(100)
except InsufficientFundsError as e:
    print(e)
```

---

### Replace Exception with Test

> Replace exception handling with a conditional test.

**When to use:**
- Exception is used for control flow
- Condition can be tested beforehand
- Exception is expected/normal, not exceptional

**Before:**
```python
def get_value_for_period(self, period: int) -> float:
    try:
        return self.values[period]
    except IndexError:
        return 0.0
```

**After:**
```python
def get_value_for_period(self, period: int) -> float:
    if period >= len(self.values):
        return 0.0
    return self.values[period]
```

---

## Quick Reference

| Technique | When to Use |
|-----------|-------------|
| Rename Method | Unclear method names |
| Separate Query from Modifier | Method both returns and modifies |
| Introduce Parameter Object | Long parameter lists, data clumps |
| Add Parameter | Method needs more information |
| Remove Parameter | Unused parameters |
| Parameterize Method | Similar methods with different values |
| Replace Parameter with Explicit Methods | Parameter switches behavior |
| Preserve Whole Object | Extracting multiple values to pass |
| Replace Parameter with Method Call | Method can get value itself |
| Remove Setting Method | Field should be immutable |
| Hide Method | Method only used internally |
| Replace Constructor with Factory Method | Complex/variant construction |
| Replace Error Code with Exception | Returning error codes |
| Replace Exception with Test | Using exceptions for control flow |

## Related Skills

- `guru-smells` - Long Parameter List and other call smells
- `guru-refactor-methods` - Composing methods
