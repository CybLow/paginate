---
name: guru-refactor-methods
description: >
  RefactoringGuru techniques for composing methods: Extract Method, Inline Method,
  Replace Temp with Query, Extract Variable, Inline Temp, Split Temporary Variable,
  Remove Assignments to Parameters. Focus on organizing code within methods.
version: "2.0"
source: refactoring.guru
related:
  - guru-smells
  - guru-refactor-moving
  - guru-refactor-conditionals
  - perf-core
---

## COMPOSING METHODS

Techniques for organizing code within methods.

> **Reference**: [refactoring.guru/refactoring/techniques](https://refactoring.guru/refactoring/techniques)

---

### Extract Method

> Move a code fragment into a new method with a descriptive name.

**When to use:**
- Method is too long (> 12 lines)
- Code fragment needs explanation (comment-worthy)
- Same code appears in multiple places
- Method does multiple things

**Before:**
```python
def print_invoice(invoice: Invoice) -> None:
    print("=" * 40)
    print(f"Invoice #{invoice.number}")
    print(f"Date: {invoice.date}")
    print("=" * 40)

    total = 0
    for item in invoice.items:
        line_total = item.quantity * item.unit_price
        print(f"{item.name}: {item.quantity} x ${item.unit_price} = ${line_total}")
        total += line_total

    tax = total * 0.1
    grand_total = total + tax
    print("-" * 40)
    print(f"Subtotal: ${total}")
    print(f"Tax (10%): ${tax}")
    print(f"Total: ${grand_total}")
```

**After:**
```python
def print_invoice(invoice: Invoice) -> None:
    _print_header(invoice)
    subtotal = _print_line_items(invoice.items)
    _print_totals(subtotal)


def _print_header(invoice: Invoice) -> None:
    print("=" * 40)
    print(f"Invoice #{invoice.number}")
    print(f"Date: {invoice.date}")
    print("=" * 40)


def _print_line_items(items: list[InvoiceItem]) -> float:
    total = 0.0
    for item in items:
        line_total = item.quantity * item.unit_price
        print(f"{item.name}: {item.quantity} x ${item.unit_price} = ${line_total}")
        total += line_total
    return total


def _print_totals(subtotal: float) -> None:
    tax = subtotal * TAX_RATE
    grand_total = subtotal + tax
    print("-" * 40)
    print(f"Subtotal: ${subtotal}")
    print(f"Tax ({TAX_RATE*100:.0f}%): ${tax}")
    print(f"Total: ${grand_total}")
```

---

### Inline Method

> Replace a method call with the method's content.

**When to use:**
- Method body is as clear as its name
- Method is only used once
- Method delegation is excessive (Middle Man smell)

**Before:**
```python
def get_rating(driver: Driver) -> int:
    return 2 if self._more_than_five_late_deliveries(driver) else 1


def _more_than_five_late_deliveries(driver: Driver) -> bool:
    return driver.late_deliveries > 5
```

**After:**
```python
def get_rating(driver: Driver) -> int:
    return 2 if driver.late_deliveries > 5 else 1
```

---

### Replace Temp with Query

> Replace a temporary variable with a method call.

**When to use:**
- Temporary variable holds an expression result
- Expression is used in multiple places
- Makes Extract Method easier

**Before:**
```python
def calculate_total(order: Order) -> float:
    base_price = order.quantity * order.item_price

    if base_price > 1000:
        discount = base_price * 0.05
    else:
        discount = base_price * 0.02

    return base_price - discount
```

**After:**
```python
def calculate_total(order: Order) -> float:
    if _base_price(order) > 1000:
        return _base_price(order) * 0.95
    return _base_price(order) * 0.98


def _base_price(order: Order) -> float:
    return order.quantity * order.item_price
```

---

### Extract Variable

> Replace a complex expression with a well-named variable.

**When to use:**
- Complex expression is hard to understand
- Expression is used multiple times
- Want to document what the expression means

**Before:**
```python
def get_price(order: Order) -> float:
    return (
        order.quantity * order.item_price
        - max(0, order.quantity - 500) * order.item_price * 0.05
        + min(order.quantity * order.item_price * 0.1, 100)
    )
```

**After:**
```python
def get_price(order: Order) -> float:
    base_price = order.quantity * order.item_price
    quantity_discount = max(0, order.quantity - 500) * order.item_price * 0.05
    shipping = min(base_price * 0.1, 100)
    return base_price - quantity_discount + shipping
```

---

### Inline Temp

> Replace a temporary variable that's only assigned once with the expression itself.

**When to use:**
- Variable is assigned once and used once
- Variable name doesn't add clarity
- Variable prevents other refactorings

**Before:**
```python
def has_discount(order: Order) -> bool:
    base_price = order.base_price()
    return base_price > 1000
```

**After:**
```python
def has_discount(order: Order) -> bool:
    return order.base_price() > 1000
```

---

### Split Temporary Variable

> Create separate variables for different assignments to a temp.

**When to use:**
- Variable is assigned multiple times for different purposes
- Variable reuse makes code confusing
- Different values represent different concepts

**Before:**
```python
def calculate_metrics(height: float, width: float) -> tuple[float, float]:
    temp = 2 * (height + width)  # Perimeter
    perimeter = temp
    
    temp = height * width  # Now it's area!
    area = temp
    
    return perimeter, area
```

**After:**
```python
def calculate_metrics(height: float, width: float) -> tuple[float, float]:
    perimeter = 2 * (height + width)
    area = height * width
    return perimeter, area
```

---

### Remove Assignments to Parameters

> Use a local variable instead of assigning to a parameter.

**When to use:**
- Function modifies a parameter value
- Confusing whether caller's value is affected
- Want to clarify intent

**Before:**
```python
def discount(input_val: int, quantity: int) -> int:
    if quantity > 50:
        input_val -= 2  # Modifying parameter!
    if quantity > 100:
        input_val -= 1
    return input_val
```

**After:**
```python
def discount(input_val: int, quantity: int) -> int:
    result = input_val
    if quantity > 50:
        result -= 2
    if quantity > 100:
        result -= 1
    return result
```

---

## Quick Reference

| Technique | When to Use |
|-----------|-------------|
| Extract Method | Long methods, duplicate code, comment-worthy blocks |
| Inline Method | Trivial methods, excessive delegation |
| Replace Temp with Query | Temp used in multiple places, enabling extraction |
| Extract Variable | Complex expressions, multiple uses |
| Inline Temp | Single-use temps that don't add clarity |
| Split Temporary Variable | Temp reused for different purposes |
| Remove Assignments to Parameters | Parameter modification confusion |

## Related Skills

- `guru-smells` - Code smells these techniques address
- `guru-refactor-moving` - Moving features between objects
