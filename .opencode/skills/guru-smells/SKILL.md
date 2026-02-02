---
name: guru-smells
description: >
  Comprehensive catalog of code smells with detection and remediation. Covers Bloaters (Long Method, Large Class),
  Object-Orientation Abusers (Switch Statements, Refused Bequest), Change Preventers (Divergent Change, Shotgun Surgery),
  Dispensables (Dead Code, Speculative Generality), and Couplers (Feature Envy, Inappropriate Intimacy).
  Each smell includes symptoms, causes, and recommended refactoring treatments.
related:
  - guru-refactor-methods
  - guru-refactor-moving
  - guru-refactor-conditionals
  - test-standards
---

## CODE SMELLS

Code smells are symptoms of deeper problems in your code. They indicate that something might be wrong and that refactoring could improve the code's structure and maintainability.

> **Reference**: Full details at [refactoring.guru/refactoring/smells](https://refactoring.guru/refactoring/smells)

---

### Bloaters

Code, methods, and classes that have grown so large that they are hard to work with.

---

#### Long Method

> Methods with too many lines that do too much.

**🔍 Signs:**
- Method exceeds 12 lines (strict limit for this project)
- Multiple levels of abstraction in one method
- Hard to name—it does too many things
- Extensive comments explaining sections
- Multiple indentation levels
- You need to scroll to read the whole method

**🔴 Causes:**
- Adding "just one more line" repeatedly
- Fear of creating new methods ("overhead")
- Not recognizing extraction opportunities
- Copy-paste programming

**🟢 Treatment:**
- **Extract Method**: Pull out logical sections into separate methods
- **Replace Temp with Query**: Extract expressions into methods
- **Introduce Parameter Object**: Group related parameters
- **Decompose Conditional**: Extract conditional branches
- **Replace Method with Method Object**: For complex methods with many local variables

**💻 Example:**
```python
# ❌ BAD: Long method doing too much
def process_order(order_data: dict, user: User, db: Database) -> Order:
    # Validate order data
    if not order_data.get("items"):
        raise ValidationError("Order must have items")
    if not order_data.get("shipping_address"):
        raise ValidationError("Shipping address required")
    for item in order_data["items"]:
        if item["quantity"] < 1:
            raise ValidationError("Quantity must be positive")
        if item["price"] < 0:
            raise ValidationError("Price must be non-negative")
    
    # Check inventory
    for item in order_data["items"]:
        product = db.query(Product).get(item["product_id"])
        if product.stock < item["quantity"]:
            raise ValidationError(f"Insufficient stock for {product.name}")
    
    # Calculate totals
    subtotal = sum(item["price"] * item["quantity"] for item in order_data["items"])
    tax = subtotal * 0.1
    shipping = 5.99 if subtotal < 50 else 0
    total = subtotal + tax + shipping
    
    # Create order
    order = Order(
        user_id=user.id,
        items=[OrderItem(**item) for item in order_data["items"]],
        subtotal=subtotal,
        tax=tax,
        shipping=shipping,
        total=total,
    )
    
    # Save to database
    db.add(order)
    db.commit()
    
    # Send confirmation email
    email_body = f"Thank you for your order #{order.id}..."
    send_email(user.email, "Order Confirmation", email_body)
    
    return order

# ✅ GOOD: Extracted into focused methods
def process_order(order_data: dict, user: User, db: Database) -> Order:
    validated_data = _validate_order_data(order_data)
    _check_inventory(validated_data.items, db)
    totals = _calculate_totals(validated_data.items)
    order = _create_order(user, validated_data, totals, db)
    _send_confirmation(user, order)
    return order

def _validate_order_data(data: dict) -> ValidatedOrderData:
    if not data.get("items"):
        raise ValidationError("Order must have items")
    if not data.get("shipping_address"):
        raise ValidationError("Shipping address required")
    return ValidatedOrderData(
        items=[_validate_item(item) for item in data["items"]],
        shipping_address=data["shipping_address"],
    )

def _validate_item(item: dict) -> ValidatedItem:
    if item["quantity"] < 1:
        raise ValidationError("Quantity must be positive")
    if item["price"] < 0:
        raise ValidationError("Price must be non-negative")
    return ValidatedItem(**item)

def _calculate_totals(items: list[ValidatedItem]) -> OrderTotals:
    subtotal = sum(item.price * item.quantity for item in items)
    tax = subtotal * TAX_RATE
    shipping = SHIPPING_COST if subtotal < FREE_SHIPPING_THRESHOLD else 0
    return OrderTotals(subtotal=subtotal, tax=tax, shipping=shipping)
```

---

#### Large Class

> Classes with too many fields, methods, or lines of code.

**🔍 Signs:**
- Class exceeds 200 lines
- More than 10 public methods
- More than 5 instance attributes
- Multiple unrelated responsibilities
- Methods that don't use the same fields
- "God class" that knows everything

**🔴 Causes:**
- Adding features without refactoring
- "Just one more method" syndrome
- Unclear separation of concerns
- Fear of creating new classes

**🟢 Treatment:**
- **Extract Class**: Move related functionality to new class
- **Extract Subclass**: Create specialized subclasses
- **Extract Interface**: Define focused interfaces
- **Duplicate Observed Data**: Separate domain from UI

**💻 Example:**
```python
# ❌ BAD: God class
class UserManager:
    def create_user(self, data): ...
    def update_user(self, user_id, data): ...
    def delete_user(self, user_id): ...
    def get_user(self, user_id): ...
    def list_users(self, filters): ...
    def validate_email(self, email): ...
    def hash_password(self, password): ...
    def verify_password(self, password, hash): ...
    def send_welcome_email(self, user): ...
    def send_password_reset(self, user): ...
    def generate_auth_token(self, user): ...
    def verify_auth_token(self, token): ...
    def check_permissions(self, user, resource): ...
    def log_user_action(self, user, action): ...

# ✅ GOOD: Separated concerns
class UserRepository:
    """Data access only."""
    def create(self, user: User) -> User: ...
    def update(self, user: User) -> User: ...
    def delete(self, user_id: int) -> None: ...
    def get(self, user_id: int) -> User | None: ...
    def list(self, filters: UserFilters) -> list[User]: ...

class PasswordService:
    """Password handling only."""
    def hash(self, password: str) -> str: ...
    def verify(self, password: str, hash: str) -> bool: ...

class EmailService:
    """Email sending only."""
    def send_welcome(self, user: User) -> None: ...
    def send_password_reset(self, user: User, token: str) -> None: ...

class AuthService:
    """Authentication only."""
    def generate_token(self, user: User) -> str: ...
    def verify_token(self, token: str) -> User | None: ...

class AuthorizationService:
    """Authorization only."""
    def check_permission(self, user: User, resource: str) -> bool: ...
```

---

#### Primitive Obsession

> Using primitives instead of small objects for simple tasks.

**🔍 Signs:**
- Field names with type suffixes (`user_id_string`, `amount_cents`)
- Primitives for domain concepts (string for email, int for money)
- Magic numbers/strings throughout code
- Type code variables (`status = 1, 2, 3`)
- String parsing for structured data

**🔴 Causes:**
- "It's just a string/number" thinking
- Fear of creating "too many" classes
- Started simple, grew complex
- Unfamiliarity with value objects

**🟢 Treatment:**
- **Replace Data Value with Object**: Create value objects
- **Replace Type Code with Class**: Use enums or classes
- **Introduce Parameter Object**: Group related primitives
- **Replace Array with Object**: Named fields instead of indices

**💻 Example:**
```python
# ❌ BAD: Primitives everywhere
def create_order(
    customer_email: str,  # Should be Email
    amount_cents: int,  # Should be Money
    currency: str,  # Part of Money
    country_code: str,  # Should be Country
    postal_code: str,  # Part of Address
    city: str,  # Part of Address
    street: str,  # Part of Address
) -> dict:
    if "@" not in customer_email:
        raise ValueError("Invalid email")
    if amount_cents < 0:
        raise ValueError("Invalid amount")
    if len(country_code) != 2:
        raise ValueError("Invalid country code")
    ...

# ✅ GOOD: Value objects
@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if "@" not in self.value:
            raise ValueError(f"Invalid email: {self.value}")

@dataclass(frozen=True)
class Money:
    amount_cents: int
    currency: str

    def __post_init__(self) -> None:
        if self.amount_cents < 0:
            raise ValueError("Amount cannot be negative")
        if len(self.currency) != 3:
            raise ValueError("Currency must be 3-letter code")

    @property
    def amount(self) -> Decimal:
        return Decimal(self.amount_cents) / 100

    def add(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount_cents + other.amount_cents, self.currency)

@dataclass(frozen=True)
class Address:
    street: str
    city: str
    postal_code: str
    country_code: str

    def __post_init__(self) -> None:
        if len(self.country_code) != 2:
            raise ValueError("Country code must be 2 letters")

def create_order(
    customer_email: Email,
    amount: Money,
    shipping_address: Address,
) -> Order:
    # Validation already done in value objects!
    ...
```

---

#### Long Parameter List

> Methods with too many parameters.

**🔍 Signs:**
- More than 4 parameters
- Boolean flag parameters
- Parameters that always travel together
- Hard to remember parameter order
- Many optional parameters with defaults

**🔴 Causes:**
- Method does too much (needs too much data)
- Passing individual fields instead of object
- Adding parameters instead of refactoring
- Not recognizing data clumps

**🟢 Treatment:**
- **Introduce Parameter Object**: Group with dataclass or TypedDict
- **Preserve Whole Object**: Pass object instead of its fields
- **Replace Parameter with Method Call**: Derive value instead of passing
- **Split into separate methods**: Especially for boolean flags

**💻 Example:**
```python
# ❌ BAD: Too many parameters
def search_products(
    query: str,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock: bool | None = None,
    brand: str | None = None,
    sort_by: str = "relevance",
    sort_desc: bool = False,
    page: int = 1,
    per_page: int = 20,
    include_variants: bool = False,
) -> ProductSearchResult:
    ...

# ✅ GOOD: Parameter object
@dataclass
class PriceRange:
    min: float | None = None
    max: float | None = None

@dataclass
class SortOption:
    field: str = "relevance"
    descending: bool = False

@dataclass
class Pagination:
    page: int = 1
    per_page: int = 20

@dataclass
class ProductSearchCriteria:
    query: str
    category: str | None = None
    price_range: PriceRange | None = None
    in_stock: bool | None = None
    brand: str | None = None
    sort: SortOption = field(default_factory=SortOption)
    pagination: Pagination = field(default_factory=Pagination)
    include_variants: bool = False

def search_products(criteria: ProductSearchCriteria) -> ProductSearchResult:
    ...

# Usage is now clear and self-documenting
results = search_products(ProductSearchCriteria(
    query="laptop",
    price_range=PriceRange(min=500, max=2000),
    sort=SortOption(field="price", descending=True),
))
```

---

#### Data Clumps

> Groups of data that appear together in multiple places.

**🔍 Signs:**
- Same fields in multiple classes
- Same parameters in multiple method signatures
- Related values always used together
- Duplicated data structures

**🔴 Causes:**
- Copy-paste programming
- Not recognizing a missing abstraction
- Evolving code without refactoring

**🟢 Treatment:**
- **Extract Class**: Create class for the clump
- **Introduce Parameter Object**: Group parameters
- **Preserve Whole Object**: Pass object instead of fields

**💻 Example:**
```python
# ❌ BAD: Same data appears everywhere
def calculate_shipping(street: str, city: str, postal: str, country: str) -> float: ...
def validate_address(street: str, city: str, postal: str, country: str) -> bool: ...
def format_address(street: str, city: str, postal: str, country: str) -> str: ...

class Order:
    shipping_street: str
    shipping_city: str
    shipping_postal: str
    shipping_country: str
    billing_street: str
    billing_city: str
    billing_postal: str
    billing_country: str

# ✅ GOOD: Extract the clump into a class
@dataclass(frozen=True)
class Address:
    street: str
    city: str
    postal_code: str
    country: str

    def format(self) -> str:
        return f"{self.street}\n{self.city}, {self.postal_code}\n{self.country}"

def calculate_shipping(address: Address) -> float: ...
def validate_address(address: Address) -> bool: ...

class Order:
    shipping_address: Address
    billing_address: Address
```

---

### Object-Orientation Abusers

Incomplete or incorrect application of object-oriented programming principles.

---

#### Switch Statements

> Complex switch/match statements that switch on type codes.

**🔍 Signs:**
- Same switch in multiple places
- Switch on object type or type code
- Adding new types requires modifying switches
- Long if-elif-else chains on type

**🔴 Causes:**
- Procedural thinking in OO context
- Not recognizing polymorphism opportunity
- Legacy code evolution

**🟢 Treatment:**
- **Replace Conditional with Polymorphism**: Create class per type
- **Replace Type Code with State/Strategy**: Use patterns
- **Introduce Null Object**: Handle absence with special class

**💻 Example:**
```python
# ❌ BAD: Switch on type repeated everywhere
def calculate_area(shape: dict) -> float:
    match shape["type"]:
        case "circle":
            return 3.14159 * shape["radius"] ** 2
        case "rectangle":
            return shape["width"] * shape["height"]
        case "triangle":
            return 0.5 * shape["base"] * shape["height"]
        case _:
            raise ValueError(f"Unknown shape: {shape['type']}")

def draw(shape: dict) -> None:
    match shape["type"]:  # Same switch again!
        case "circle":
            ...

# ✅ GOOD: Polymorphism
class Shape(Protocol):
    def area(self) -> float: ...
    def draw(self) -> None: ...

@dataclass
class Circle:
    radius: float

    def area(self) -> float:
        return 3.14159 * self.radius ** 2

    def draw(self) -> None: ...

@dataclass
class Rectangle:
    width: float
    height: float

    def area(self) -> float:
        return self.width * self.height

    def draw(self) -> None: ...

# Adding new shapes requires no modification to existing code
```

---

#### Temporary Field

> Fields that are only set in certain circumstances.

**🔍 Signs:**
- Fields that are often None/null
- Fields only used in specific methods
- Conditional logic checking if field is set
- Initialization in some constructors but not others

**🔴 Causes:**
- Complex algorithm that needs temporary storage
- Passing data between methods via fields
- Optional features bolted on

**🟢 Treatment:**
- **Extract Class**: For the conditional behavior
- **Introduce Null Object**: Provide default behavior
- **Replace Temp with Query**: Calculate when needed

**💻 Example:**
```python
# ❌ BAD: Temporary fields
class ReportGenerator:
    def __init__(self) -> None:
        self._data: list[dict] | None = None  # Only set during generate
        self._summary: dict | None = None  # Only set after analyze

    def generate(self, data: list[dict]) -> Report:
        self._data = data
        self._analyze()
        report = self._format()
        self._data = None
        self._summary = None
        return report

# ✅ GOOD: Pass data through methods
class ReportGenerator:
    def generate(self, data: list[dict]) -> Report:
        summary = self._analyze(data)
        return self._format(data, summary)

    def _analyze(self, data: list[dict]) -> Summary:
        ...

    def _format(self, data: list[dict], summary: Summary) -> Report:
        ...
```

---

#### Refused Bequest

> Subclass doesn't use inherited behavior.

**🔍 Signs:**
- Overriding methods to do nothing
- `NotImplementedError` in inherited methods
- Subclass ignores parent's fields/methods
- Inheritance used for code reuse, not "is-a"

**🔴 Causes:**
- Inheriting for convenience, not relationship
- Interface is too broad for all implementations
- Evolution of requirements

**🟢 Treatment:**
- **Replace Inheritance with Delegation**: Compose instead
- **Extract Subclass**: Push specialized behavior down
- **Push Down Method/Field**: Move unused members to subclasses

**💻 Example:**
```python
# ❌ BAD: Bird can't fly!
class Bird:
    def fly(self) -> None:
        print("Flying...")

    def eat(self) -> None:
        print("Eating...")

class Penguin(Bird):
    def fly(self) -> None:
        raise NotImplementedError("Penguins can't fly!")  # Refused bequest!

# ✅ GOOD: Proper abstraction
class Bird(Protocol):
    def eat(self) -> None: ...

class FlyingBird(Protocol):
    def fly(self) -> None: ...
    def eat(self) -> None: ...

class Sparrow:  # Implements both
    def fly(self) -> None:
        print("Flying...")

    def eat(self) -> None:
        print("Eating seeds...")

class Penguin:  # Only implements Bird
    def eat(self) -> None:
        print("Eating fish...")

    def swim(self) -> None:  # Has its own abilities
        print("Swimming...")
```

---

#### Alternative Classes with Different Interfaces

> Classes that do similar things but have different method signatures.

**🔍 Signs:**
- Two classes have methods that do the same thing
- Method names or parameters differ
- Can't use them interchangeably

**🔴 Causes:**
- Different developers created similar classes
- Parallel development without coordination
- Third-party library with different conventions

**🟢 Treatment:**
- **Rename Method**: Align naming
- **Move Method**: Consolidate in one class
- **Extract Superclass/Interface**: Create common interface
- **Adapter**: Wrap one to match the other

---

### Change Preventers

Smells that make code difficult to change.

---

#### Divergent Change

> One class is commonly changed for different reasons.

**🔍 Signs:**
- "I need to change this class for feature X AND feature Y"
- Class changes for multiple unrelated features
- Different parts of the class change at different times
- Changes for different stakeholders

**🔴 Causes:**
- Poor separation of concerns
- "Kitchen sink" class
- Growing organically without refactoring

**🟢 Treatment:**
- **Extract Class**: Split by responsibility
- **Extract Superclass/Subclass**: Separate variation points

**💻 Example:**
```python
# ❌ BAD: Changed for UI, database, and business rules
class OrderProcessor:
    def process(self, order):
        # Business rules (change when rules change)
        if order.total < 0:
            raise ValidationError("Invalid total")
        if order.items_count > 100:
            order.apply_bulk_discount()

        # Database (changes when schema changes)
        self._db.orders.insert(order.to_dict())
        self._db.inventory.update_stock(order.items)

        # UI formatting (changes when UI changes)
        return {
            "display_total": f"${order.total:.2f}",
            "items_html": self._render_items(order.items),
        }

# ✅ GOOD: Separate concerns
class OrderValidator:
    def validate(self, order: Order) -> None: ...

class OrderRepository:
    def save(self, order: Order) -> None: ...

class OrderPresenter:
    def to_response(self, order: Order) -> dict: ...
```

---

#### Shotgun Surgery

> One change requires many small changes in many classes.

**🔍 Signs:**
- Simple change touches many files
- Adding a field requires changes everywhere
- "Ripple effect" changes
- Fear of making changes

**🔴 Causes:**
- Responsibility scattered across classes
- Copy-paste without abstraction
- Missing central concept

**🟢 Treatment:**
- **Move Method/Field**: Consolidate scattered code
- **Inline Class**: Merge overly distributed classes
- **Extract Class**: Create missing abstraction

**💻 Example:**
```python
# ❌ BAD: Adding new user field requires changes everywhere
# In User class
class User:
    phone: str  # New field

# In UserForm (change 1)
class UserForm:
    phone_input = CharField()

# In UserSerializer (change 2)
class UserSerializer:
    phone = StringField()

# In UserValidator (change 3)
class UserValidator:
    def validate_phone(self, phone): ...

# In UserRepository (change 4)
class UserRepository:
    def save(self, user):
        self._db.execute("INSERT ... phone ...", user.phone)

# In UserDTO (change 5)
@dataclass
class UserDTO:
    phone: str

# ✅ GOOD: Centralized configuration drives everything
@dataclass
class UserField:
    name: str
    type: type
    validator: Callable
    required: bool = True

USER_FIELDS = [
    UserField("name", str, validate_name, required=True),
    UserField("email", str, validate_email, required=True),
    UserField("phone", str, validate_phone, required=False),  # Add once!
]

# Form, serializer, validator, etc. all derive from USER_FIELDS
```

---

#### Parallel Inheritance Hierarchies

> Creating a subclass requires creating another subclass elsewhere.

**🔍 Signs:**
- Two hierarchies with matching prefixes (OrderValidator, ProductValidator)
- Adding to one requires adding to the other
- 1:1 relationship between hierarchies

**🔴 Causes:**
- Strategy pattern gone wrong
- Over-engineering with patterns
- Missing composition

**🟢 Treatment:**
- **Move Method/Field**: Consolidate hierarchies
- **Replace Inheritance with Delegation**: Use composition

---

### Dispensables

Pointless code that could be removed.

---

#### Comments (Over-commenting)

> Comments that explain what code does instead of why.

**🔍 Signs:**
- Comments restating the code
- Commented-out code
- TODO comments that never get done
- Javadoc on obvious methods

**🔴 Causes:**
- Code is too complex (needs explaining)
- Unclear naming
- Developer fear of forgetting
- Mandated documentation style

**🟢 Treatment:**
- **Extract Method**: With descriptive name
- **Rename Method/Variable**: Self-documenting code
- **Introduce Assertion**: For invariants
- Delete the comment if code is clear

**💻 Example:**
```python
# ❌ BAD: Comment explains what
# Loop through users and check if active
for user in users:
    # Check if user is active
    if user.status == "active":
        # Add to active users list
        active_users.append(user)

# ✅ GOOD: Code is self-explanatory
active_users = [user for user in users if user.is_active()]

# ✅ GOOD: Comment explains why (business reason)
# Per legal requirement GDPR-2023-04, we must exclude EU users
# from marketing emails unless they've explicitly opted in
eu_marketing_users = [u for u in users if u.region != "EU" or u.marketing_consent]
```

---

#### Duplicate Code

> Same code structure in multiple places.

**🔍 Signs:**
- Copy-paste code
- Same bug fixed in multiple places
- Similar methods with slight variations
- Parallel modifications needed

**🔴 Causes:**
- Copy-paste programming
- Time pressure
- Not recognizing duplication
- Different developers writing same code

**🟢 Treatment:**
- **Extract Method**: For duplicated code in same class
- **Extract Class**: For duplicated code across classes
- **Pull Up Method**: For duplicated code in subclasses
- **Form Template Method**: For similar methods with variations

---

#### Lazy Class

> Class that doesn't do enough to justify its existence.

**🔍 Signs:**
- Class with only 1-2 methods
- Wrapper that just delegates
- Class created for "future extensibility" that never came
- More boilerplate than actual logic

**🔴 Causes:**
- Over-engineering
- Refactoring that went too far
- "Design patterns everywhere" mentality
- Speculative generality

**🟢 Treatment:**
- **Inline Class**: Merge into user
- **Collapse Hierarchy**: Merge with parent/child

---

#### Data Class

> Class with only fields and no behavior.

**🔍 Signs:**
- Class has only fields and getters/setters
- All logic operating on class is elsewhere
- Class is just a dumb data container

**🔴 Causes:**
- Procedural thinking in OO context
- Anemic domain model
- Over-separation of data and behavior

**🟢 Treatment:**
- **Move Method**: Bring behavior to data
- **Encapsulate Field**: Add validation in setters
- **Encapsulate Collection**: Protect internal collections

**Note:** In Python, `@dataclass` is often appropriate for DTOs, value objects, and configuration. Not every data class is a smell—consider context.

---

#### Dead Code

> Code that is never executed.

**🔍 Signs:**
- Unreachable code after return/raise
- Unused variables, parameters, methods, classes
- Commented-out code
- Feature flags that are never enabled

**🔴 Causes:**
- Incomplete refactoring
- Deleted features
- "Just in case" code
- Fear of deleting

**🟢 Treatment:**
- **Delete it!** Version control has your back.
- Use linting tools (ruff can detect dead code)
- Trust your tests

---

#### Speculative Generality

> Code created "just in case" for future requirements that never came.

**🔍 Signs:**
- Abstract classes with only one subclass
- Unused parameters "for future use"
- Methods named with "handler" or "processor" that handle one thing
- Complex infrastructure for simple needs

**🔴 Causes:**
- Trying to predict the future
- Over-engineering
- "Design pattern fever"
- Fear of change

**🟢 Treatment:**
- **Collapse Hierarchy**: Remove unnecessary abstraction
- **Inline Class**: Merge unnecessary classes
- **Remove Parameter**: Delete unused parameters
- Follow YAGNI

---

### Couplers

Smells that create excessive coupling between classes.

---

#### Feature Envy

> Method uses another class's data more than its own.

**🔍 Signs:**
- Method calls many getters on another object
- Method does calculations with another object's data
- Method belongs more logically to another class

**🔴 Causes:**
- Behavior in wrong class
- Missing domain method
- Procedural thinking

**🟢 Treatment:**
- **Move Method**: To the class whose data is used
- **Extract Method**: Then move extracted method

**💻 Example:**
```python
# ❌ BAD: Feature envy - uses customer's data extensively
class OrderPrinter:
    def print_shipping_label(self, order: Order) -> str:
        customer = order.customer
        return (
            f"{customer.first_name} {customer.last_name}\n"
            f"{customer.address.street}\n"
            f"{customer.address.city}, {customer.address.postal_code}\n"
            f"{customer.address.country}"
        )

# ✅ GOOD: Move behavior to the class with the data
class Customer:
    def format_shipping_label(self) -> str:
        return (
            f"{self.first_name} {self.last_name}\n"
            f"{self.address.format()}"
        )

class OrderPrinter:
    def print_shipping_label(self, order: Order) -> str:
        return order.customer.format_shipping_label()
```

---

#### Inappropriate Intimacy

> Classes know too much about each other's internals.

**🔍 Signs:**
- Classes access each other's private fields
- Bidirectional associations
- Classes form a "clique" that's hard to separate
- Subclass accesses too many parent internals

**🔴 Causes:**
- Tight coupling from design
- Public fields that should be private
- Convenience over encapsulation

**🟢 Treatment:**
- **Move Method/Field**: Reduce interdependence
- **Change Bidirectional to Unidirectional**: Simplify relationship
- **Extract Class**: Create intermediary
- **Hide Delegate**: Add intermediary methods

---

#### Message Chains

> Client asks object A for object B, then asks B for object C, etc.

**🔍 Signs:**
- Chains like `a.b().c().d().e()`
- Client depends on navigation structure
- Changes to structure break clients

**🔴 Causes:**
- Law of Demeter violations
- Navigating object graph directly
- Missing convenience methods

**🟢 Treatment:**
- **Hide Delegate**: Add methods to reduce chain length
- **Extract Method**: Encapsulate chain
- **Move Method**: Put logic where data lives

**💻 Example:**
```python
# ❌ BAD: Message chain
def get_manager_phone(employee: Employee) -> str:
    return employee.department.manager.contact_info.phone_number

# ✅ GOOD: Hide delegate
class Employee:
    def get_manager_phone(self) -> str:
        return self._department.get_manager_phone()

class Department:
    def get_manager_phone(self) -> str:
        return self._manager.get_phone()
```

---

#### Middle Man

> Class that only delegates to another class.

**🔍 Signs:**
- Most methods just call same method on delegate
- Class adds no value
- Every new feature requires adding delegation method

**🔴 Causes:**
- Over-application of Hide Delegate
- Refactoring that left empty wrapper
- Abstraction layer that isn't needed

**🟢 Treatment:**
- **Remove Middle Man**: Let clients call delegate directly
- **Inline Method**: Eliminate trivial delegations
- If some methods add value, keep those, inline the rest

---

#### Incomplete Library Class

> A library class doesn't provide functionality you need.

**🔍 Signs:**
- You can't modify the library code
- You need to extend library class behavior
- Same workaround code appears in multiple places
- You're wrapping library calls with additional logic everywhere

**🔴 Causes:**
- Library is not designed for your use case
- Library maintainers can't anticipate all needs
- Requirements evolved after library adoption
- Using a library for unintended purposes

**🟢 Treatment:**
- **Introduce Foreign Method**: Add utility method to your code that takes library object
- **Introduce Local Extension**: Create wrapper class or subclass
- **Adapter Pattern**: Create adapter to provide missing interface

**💻 Example:**
```python
# ❌ BAD: Workaround code scattered everywhere
from datetime import date

# In module A
next_week = date.today().replace(day=date.today().day + 7)  # Wrong!

# In module B  
import datetime
next_week = date.today() + datetime.timedelta(days=7)  # Repeated

# In module C
from datetime import timedelta
next_week = date.today() + timedelta(days=7)  # Same thing again

# ✅ GOOD: Introduce Foreign Method (utility function)
from datetime import date, timedelta

def add_days(d: date, days: int) -> date:
    """Foreign method: adds days to a date."""
    return d + timedelta(days=days)

def next_week(d: date) -> date:
    """Foreign method: returns date one week from given date."""
    return add_days(d, 7)

# Usage is now consistent
next_week_date = next_week(date.today())

# ✅ GOOD: Introduce Local Extension (enhanced date class)
class EnhancedDate(date):
    """Local extension: date with additional convenience methods."""
    
    def add_days(self, days: int) -> EnhancedDate:
        result = self + timedelta(days=days)
        return EnhancedDate(result.year, result.month, result.day)
    
    def next_week(self) -> EnhancedDate:
        return self.add_days(7)
    
    def is_weekend(self) -> bool:
        return self.weekday() >= 5
    
    def is_business_day(self) -> bool:
        return not self.is_weekend()

# Usage
today = EnhancedDate.today()
if today.is_business_day():
    deadline = today.next_week()
```

---

### Code Smell Quick Reference

| Smell | Symptom | Quick Fix |
|-------|---------|-----------|
| Long Method | > 12 lines | Extract Method |
| Large Class | > 200 lines, > 10 methods | Extract Class |
| Long Parameter List | > 4 params | Introduce Parameter Object |
| Duplicate Code | Copy-paste | Extract Method/Class |
| Feature Envy | Uses other class's data | Move Method |
| Shotgun Surgery | One change = many files | Move/Consolidate |
| Dead Code | Unused code | Delete it |
| Comments | Explaining what | Rename/Extract |
| Primitive Obsession | Primitives for concepts | Replace with Class |
| Switch Statements | Type-based switching | Polymorphism |
| Lazy Class | Does too little | Inline Class |
| Speculative Generality | "Just in case" code | Delete/Simplify |
| Temporary Field | Sometimes-null fields | Extract Class |
| Message Chains | a.b().c().d() | Hide Delegate |
| Middle Man | Only delegates | Remove/Inline |
| Incomplete Library Class | Library lacks features | Foreign Method/Extension |

---
