---
name: guru-patterns-structural
description: >
  Structural design patterns for object composition. Covers Adapter (interface conversion),
  Bridge (abstraction/implementation separation), Composite (tree structures), Decorator (dynamic behavior),
  Facade (simplified interface), Flyweight (memory optimization), and Proxy (access control/lazy loading).
  Each pattern includes problem/solution, UML structure, Python implementation, applicability, and trade-offs.
related:
  - guru-patterns-creational
  - guru-patterns-behavioral
  - arch-hexagonal
  - type-hints
---

## STRUCTURAL DESIGN PATTERNS

Structural patterns deal with object composition, creating relationships between objects to form larger structures. They help ensure that when one part of a system changes, the entire structure doesn't need to change.

> **Reference**: Full details at [refactoring.guru/design-patterns/structural-patterns](https://refactoring.guru/design-patterns/structural-patterns)

---

### Adapter

> Converts one interface to another that clients expect.

**Problem:**
You have a class with a useful interface, but it's incompatible with the interface your code expects. You can't modify the class (third-party or legacy code).

**Solution:**
Create a wrapper class that translates one interface to another.

**Structure:**
```
┌───────────┐        ┌───────────┐        ┌───────────┐
│  Client   │──uses─▶│  Target   │◀─impl──│  Adapter  │
└───────────┘        │(Protocol) │        └───────────┘
                     └───────────┘              │
                                                │wraps
                                                ▼
                                         ┌───────────┐
                                         │  Adaptee  │
                                         └───────────┘
```

**Example:**
```python
from __future__ import annotations
from typing import Protocol
from dataclasses import dataclass
import uuid

@dataclass
class PaymentResult:
    success: bool
    transaction_id: str

# Target interface our code expects
class PaymentGateway(Protocol):
    def charge(self, amount: float, currency: str) -> PaymentResult: ...

# Third-party service with different interface (Adaptee)
class StripeClient:
    def create_charge(
        self,
        amount_cents: int,
        currency_code: str,
        idempotency_key: str,
    ) -> dict:
        # Stripe-specific implementation
        return {"id": "ch_123", "status": "succeeded"}

# Adapter
class StripeAdapter:
    """Adapts StripeClient to PaymentGateway interface."""

    def __init__(self, client: StripeClient) -> None:
        self._client = client

    def charge(self, amount: float, currency: str) -> PaymentResult:
        # Convert interface
        amount_cents = int(amount * 100)
        result = self._client.create_charge(
            amount_cents=amount_cents,
            currency_code=currency.upper(),
            idempotency_key=str(uuid.uuid4()),
        )
        return PaymentResult(
            success=result["status"] == "succeeded",
            transaction_id=result["id"],
        )

# Usage - client code doesn't know about Stripe
@dataclass
class Order:
    total: float
    currency: str

def process_order(gateway: PaymentGateway, order: Order) -> None:
    result = gateway.charge(order.total, order.currency)
    print(f"Payment {'succeeded' if result.success else 'failed'}: {result.transaction_id}")
```

**Applicability:**
- Use existing class but interface doesn't match
- Create reusable class that cooperates with unrelated classes
- Need to use several existing subclasses lacking common functionality

**Consequences:**

| Pros | Cons |
|------|------|
| Single Responsibility: separate interface conversion | Increases complexity |
| Open/Closed: add adapters without changing existing code | Sometimes simpler to change the service class |

---

### Bridge

> Separates abstraction from implementation so both can vary independently.

**Problem:**
You have a class hierarchy that grows in two independent dimensions (e.g., shapes × colors, platforms × features). Inheritance leads to class explosion.

**Solution:**
Switch from inheritance to composition. Extract one dimension into a separate class hierarchy and reference it from the original.

**Example:**
```python
from typing import Protocol

# Implementation hierarchy
class MessageSender(Protocol):
    def send(self, title: str, body: str) -> None: ...

class EmailSender:
    def send(self, title: str, body: str) -> None:
        print(f"Email: {title}\n{body}")

class SlackSender:
    def send(self, title: str, body: str) -> None:
        print(f"Slack: #{title}: {body}")

class SMSSender:
    def send(self, title: str, body: str) -> None:
        print(f"SMS: {title[:20]} - {body[:100]}")

# Abstraction hierarchy
class Notification:
    """Base notification that uses a sender implementation."""

    def __init__(self, sender: MessageSender) -> None:
        self._sender = sender

    def notify(self, message: str) -> None:
        raise NotImplementedError

class AlertNotification(Notification):
    """Urgent alert notification."""

    def notify(self, message: str) -> None:
        self._sender.send("ALERT", message.upper())

class ReminderNotification(Notification):
    """Gentle reminder notification."""

    def notify(self, message: str) -> None:
        self._sender.send("Reminder", message)

# Usage - any combination works
alert_email = AlertNotification(EmailSender())
alert_slack = AlertNotification(SlackSender())
reminder_sms = ReminderNotification(SMSSender())
```

**Applicability:**
- Want to divide monolithic class with multiple variants
- Need to extend class in several independent dimensions
- Need to switch implementations at runtime

**Consequences:**

| Pros | Cons |
|------|------|
| Platform-independent classes | More complexity with one more indirection |
| Open/Closed: add new abstractions and implementations independently | |
| Hide implementation details | |

---

### Composite

> Composes objects into tree structures representing part-whole hierarchies.

**Problem:**
You need to work with tree structures where individual objects and groups of objects should be treated uniformly.

**Solution:**
Define a common interface for both simple and complex elements. Complex elements delegate work to their children.

**Example:**
```python
from __future__ import annotations
from typing import Protocol
from dataclasses import dataclass

class PriceCalculator(Protocol):
    def get_price(self) -> float: ...
    def get_description(self) -> str: ...

# Leaf
@dataclass
class Product:
    name: str
    price: float

    def get_price(self) -> float:
        return self.price

    def get_description(self) -> str:
        return f"{self.name}: ${self.price:.2f}"

# Composite
class ProductBundle:
    def __init__(self, name: str, discount: float = 0.0) -> None:
        self._name = name
        self._discount = discount
        self._items: list[PriceCalculator] = []

    def add(self, item: PriceCalculator) -> None:
        self._items.append(item)

    def remove(self, item: PriceCalculator) -> None:
        self._items.remove(item)

    def get_price(self) -> float:
        total = sum(item.get_price() for item in self._items)
        return total * (1 - self._discount)

    def get_description(self) -> str:
        items_desc = "\n  ".join(item.get_description() for item in self._items)
        return f"{self._name} ({self._discount*100:.0f}% off):\n  {items_desc}"

# Usage - uniform treatment
laptop = Product("Laptop", 999.99)
mouse = Product("Mouse", 29.99)
keyboard = Product("Keyboard", 79.99)

peripherals = ProductBundle("Peripherals Bundle", discount=0.1)
peripherals.add(mouse)
peripherals.add(keyboard)

full_setup = ProductBundle("Complete Setup", discount=0.05)
full_setup.add(laptop)
full_setup.add(peripherals)  # Bundle containing bundle

print(full_setup.get_price())  # Works uniformly
```

**Applicability:**
- Implement tree-like object structure
- Want clients to treat simple and complex elements uniformly
- Recursive structures (file systems, org charts, UI components)

**Consequences:**

| Pros | Cons |
|------|------|
| Work with complex trees using simple interface | Hard to restrict component types in composite |
| Open/Closed: add new element types | Design can become too general |
| Recursive operations are natural | |

---

### Decorator

> Attaches additional responsibilities to objects dynamically.

**Problem:**
You need to add behavior to objects without affecting other objects of the same class. Inheritance is static and doesn't allow removing behavior.

**Solution:**
Wrap the object in a decorator that adds behavior before/after delegating to the wrapped object.

**Example:**
```python
from typing import Protocol
import zlib

class DataSource(Protocol):
    def write(self, data: bytes) -> None: ...
    def read(self) -> bytes: ...

class FileDataSource:
    def __init__(self, filename: str) -> None:
        self._filename = filename

    def write(self, data: bytes) -> None:
        with open(self._filename, "wb") as f:
            f.write(data)

    def read(self) -> bytes:
        with open(self._filename, "rb") as f:
            return f.read()

# Decorator base
class DataSourceDecorator:
    def __init__(self, source: DataSource) -> None:
        self._source = source

    def write(self, data: bytes) -> None:
        self._source.write(data)

    def read(self) -> bytes:
        return self._source.read()

# Concrete decorators
class CompressionDecorator(DataSourceDecorator):
    def write(self, data: bytes) -> None:
        compressed = zlib.compress(data)
        super().write(compressed)

    def read(self) -> bytes:
        data = super().read()
        return zlib.decompress(data)

class EncryptionDecorator(DataSourceDecorator):
    def __init__(self, source: DataSource, key: bytes) -> None:
        super().__init__(source)
        self._key = key

    def _encrypt(self, data: bytes) -> bytes:
        # Simplified XOR encryption for demo
        return bytes(b ^ self._key[i % len(self._key)] for i, b in enumerate(data))

    def _decrypt(self, data: bytes) -> bytes:
        return self._encrypt(data)  # XOR is symmetric

    def write(self, data: bytes) -> None:
        encrypted = self._encrypt(data)
        super().write(encrypted)

    def read(self) -> bytes:
        data = super().read()
        return self._decrypt(data)

# Usage - stack decorators
source = EncryptionDecorator(
    CompressionDecorator(
        FileDataSource("data.bin")
    ),
    key=b"secret",
)
source.write(b"Hello, World!")  # Compresses, then encrypts
```

**Applicability:**
- Add behavior without subclassing
- Add responsibilities at runtime
- Combine behaviors by wrapping multiple decorators
- When extension by subclassing is impractical

**Consequences:**

| Pros | Cons |
|------|------|
| Extend behavior without new subclass | Hard to remove specific wrapper from stack |
| Combine behaviors at runtime | Lots of small classes |
| Single Responsibility: divide monolithic class | Order of decorators matters |

---

### Facade

> Provides a simplified interface to a complex subsystem.

**Problem:**
You need to work with a complex library or framework with many moving parts. Most clients only need a subset of functionality.

**Solution:**
Provide a simple interface that covers most common use cases while still allowing access to the full subsystem.

**Example:**
```python
from dataclasses import dataclass
from typing import Any

# Complex subsystem classes
@dataclass
class VideoFrames:
    frames: list[bytes]

@dataclass
class AudioSamples:
    samples: list[bytes]

@dataclass
class MediaStream:
    data: bytes

class VideoCodec:
    def decode(self, data: bytes) -> VideoFrames:
        return VideoFrames(frames=[])

    def encode(self, frames: VideoFrames, quality: int) -> bytes:
        return b""

class AudioCodec:
    def decode(self, data: bytes) -> AudioSamples:
        return AudioSamples(samples=[])

    def encode(self, samples: AudioSamples, bitrate: int) -> bytes:
        return b""

class VideoMixer:
    def mix(self, video: VideoFrames, audio: AudioSamples) -> MediaStream:
        return MediaStream(data=b"")

class FileReader:
    def read(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()

class FileWriter:
    def write(self, path: str, data: bytes) -> None:
        with open(path, "wb") as f:
            f.write(data)

# Facade - simple interface
class VideoConverter:
    """Simplified interface for video conversion."""

    def __init__(self) -> None:
        self._video_codec = VideoCodec()
        self._audio_codec = AudioCodec()
        self._mixer = VideoMixer()
        self._reader = FileReader()
        self._writer = FileWriter()

    def convert(
        self,
        input_path: str,
        output_path: str,
        format: str = "mp4",
    ) -> None:
        """Convert video file to specified format.

        This simple method hides all the complexity of:
        - Reading the file
        - Decoding video and audio
        - Re-encoding with appropriate codecs
        - Muxing streams
        - Writing output
        """
        data = self._reader.read(input_path)
        video = self._video_codec.decode(data)
        audio = self._audio_codec.decode(data)
        stream = self._mixer.mix(video, audio)
        self._writer.write(output_path, stream.data)

# Usage - client sees simple interface
converter = VideoConverter()
converter.convert("input.avi", "output.mp4")
```

**Applicability:**
- Provide simple interface to complex subsystem
- Structure subsystem into layers (facade per layer)
- Decouple clients from subsystem implementation

**Consequences:**

| Pros | Cons |
|------|------|
| Isolate clients from subsystem complexity | Facade can become god object |
| Promotes weak coupling | Can limit power users |
| Simplifies common use cases | |

---

### Flyweight

> Shares common state between multiple objects to save memory.

**Problem:**
You need to create a huge number of similar objects, consuming too much memory.

**Solution:**
Extract shared (intrinsic) state into shared flyweight objects. Pass unique (extrinsic) state to methods instead of storing it.

**Example:**
```python
from __future__ import annotations
from functools import lru_cache
from dataclasses import dataclass

class TextStyle:
    """Flyweight: shared text styling (intrinsic state)."""

    def __init__(self, font: str, size: int, color: str) -> None:
        self.font = font
        self.size = size
        self.color = color

class TextStyleFactory:
    """Creates and caches text styles."""

    @staticmethod
    @lru_cache(maxsize=100)
    def get_style(font: str, size: int, color: str) -> TextStyle:
        return TextStyle(font, size, color)

@dataclass
class Character:
    """Context: uses flyweight + extrinsic state."""
    char: str  # Extrinsic state
    x: int  # Extrinsic state
    y: int  # Extrinsic state
    style: TextStyle  # Flyweight (shared)

    def render(self) -> None:
        print(f"Render '{self.char}' at ({self.x}, {self.y}) "
              f"with {self.style.font} {self.style.size}px {self.style.color}")

# Usage
factory = TextStyleFactory()

# All 'a' characters share the same style object
doc_chars = [
    Character("H", 0, 0, factory.get_style("Arial", 12, "black")),
    Character("e", 10, 0, factory.get_style("Arial", 12, "black")),
    Character("l", 20, 0, factory.get_style("Arial", 12, "black")),
    Character("l", 30, 0, factory.get_style("Arial", 12, "black")),
    Character("o", 40, 0, factory.get_style("Arial", 12, "black")),
]

# All share the SAME TextStyle instance
assert doc_chars[0].style is doc_chars[1].style
```

**Applicability:**
- Program needs huge number of similar objects
- Objects contain duplicate state that can be extracted
- Many objects can be replaced by fewer shared objects
- Application doesn't depend on object identity

**Consequences:**

| Pros | Cons |
|------|------|
| Save lots of RAM | Trade RAM for CPU (calculating extrinsic state) |
| | Code becomes more complicated |
| | Objects lose their identity |

---

### Proxy

> Provides a surrogate or placeholder for another object.

**Problem:**
You need to perform something before or after the primary logic of an object (lazy loading, access control, logging, caching).

**Solution:**
Create a proxy class with the same interface that controls access to the original object.

**Example:**
```python
from __future__ import annotations
from typing import Protocol
import time
import logging

logger = logging.getLogger(__name__)

class Database(Protocol):
    def query(self, sql: str) -> list[dict]: ...
    def execute(self, sql: str) -> int: ...

class PostgresDatabase:
    """Real database connection."""

    def __init__(self, connection_string: str) -> None:
        self._connection_string = connection_string
        self._conn = None

    def _connect(self) -> None:
        if self._conn is None:
            print(f"Connecting to {self._connection_string}...")
            self._conn = True  # Simplified

    def query(self, sql: str) -> list[dict]:
        self._connect()
        return [{"id": 1, "name": "example"}]

    def execute(self, sql: str) -> int:
        self._connect()
        return 1

# Lazy loading proxy
class LazyDatabaseProxy:
    """Defers database connection until first use."""

    def __init__(self, connection_string: str) -> None:
        self._connection_string = connection_string
        self._database: PostgresDatabase | None = None

    def _get_database(self) -> PostgresDatabase:
        if self._database is None:
            print("Initializing database connection...")
            self._database = PostgresDatabase(self._connection_string)
        return self._database

    def query(self, sql: str) -> list[dict]:
        return self._get_database().query(sql)

    def execute(self, sql: str) -> int:
        return self._get_database().execute(sql)

# Logging proxy
class LoggingDatabaseProxy:
    """Logs all database operations."""

    def __init__(self, database: Database) -> None:
        self._database = database

    def query(self, sql: str) -> list[dict]:
        logger.debug(f"Query: {sql}")
        start = time.time()
        result = self._database.query(sql)
        logger.debug(f"Query completed in {time.time() - start:.3f}s")
        return result

    def execute(self, sql: str) -> int:
        logger.info(f"Execute: {sql}")
        return self._database.execute(sql)

# Caching proxy
class CachingDatabaseProxy:
    """Caches query results."""

    def __init__(self, database: Database) -> None:
        self._database = database
        self._cache: dict[str, list[dict]] = {}

    def query(self, sql: str) -> list[dict]:
        if sql in self._cache:
            return self._cache[sql]
        result = self._database.query(sql)
        self._cache[sql] = result
        return result

    def execute(self, sql: str) -> int:
        self._cache.clear()  # Invalidate cache on writes
        return self._database.execute(sql)
```

**Applicability:**
- **Virtual proxy**: Lazy initialization of heavy objects
- **Protection proxy**: Access control
- **Remote proxy**: Local representative for remote object
- **Logging proxy**: Keep history of requests
- **Caching proxy**: Cache results and manage cache lifecycle

**Consequences:**

| Pros | Cons |
|------|------|
| Control service without clients knowing | Code complexity increases |
| Manage lifecycle | Response might be delayed |
| Works even when service isn't ready | |

---

### Structural Patterns Summary

| Pattern | Intent | Use When |
|---------|--------|----------|
| Adapter | Convert interface to another | Interface doesn't match expected |
| Bridge | Separate abstraction from implementation | Two independent dimensions of change |
| Composite | Tree structures with uniform interface | Need part-whole hierarchies |
| Decorator | Add behavior dynamically | Extend without subclassing |
| Facade | Simplify complex subsystem | Hide complexity from clients |
| Flyweight | Share state to save memory | Many similar objects needed |
| Proxy | Control access or add behavior | Lazy loading, caching, access control |

---
