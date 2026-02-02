---
name: perf-core
description: >
  Core Python performance optimization. Covers lazy evaluation with generators, caching 
  strategies (lru_cache, application caching), database query optimization (N+1, indexing),
  async best practices, and memory management.
related:
  - perf-database
  - perf-profiling
  - perf-apm
  - perf-ops
---

## PERFORMANCE GUIDELINES

Optimize for readability first. Measure before optimizing. Premature optimization is the root of all evil.

---

### Lazy Evaluation

**Use generators for large datasets:**
```python
# BAD: Loads everything into memory
def get_all_users() -> list[User]:
    users = []
    for row in db.execute("SELECT * FROM users"):
        users.append(User.from_row(row))
    return users  # Could be millions of users!

# GOOD: Yields one at a time
def iter_users() -> Iterator[User]:
    for row in db.execute("SELECT * FROM users"):
        yield User.from_row(row)

# Usage
for user in iter_users():
    process(user)  # Memory: O(1) instead of O(n)
```

**Defer computation until needed:**
```python
# BAD: Computes everything upfront
class Report:
    def __init__(self, data: list[dict]) -> None:
        self.summary = self._compute_summary(data)  # Expensive!
        self.charts = self._generate_charts(data)  # Very expensive!
        self.tables = self._build_tables(data)  # Also expensive!

# GOOD: Compute on demand
class Report:
    def __init__(self, data: list[dict]) -> None:
        self._data = data
        self._summary: Summary | None = None

    @property
    def summary(self) -> Summary:
        if self._summary is None:
            self._summary = self._compute_summary(self._data)
        return self._summary

# Or use functools.cached_property (Python 3.8+)
from functools import cached_property

class Report:
    def __init__(self, data: list[dict]) -> None:
        self._data = data

    @cached_property
    def summary(self) -> Summary:
        return self._compute_summary(self._data)
```

---

### Caching Strategies

**Use functools.lru_cache for pure functions:**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(n: int) -> int:
    """Cache results of expensive computation."""
    return sum(i ** 2 for i in range(n))

# Clear cache if needed
expensive_calculation.cache_clear()

# Check cache stats
expensive_calculation.cache_info()
```

**Cache with expiration:**
```python
from functools import lru_cache
from time import time

def timed_cache(seconds: int):
    """LRU cache with time-based expiration."""
    def decorator(func):
        func = lru_cache(maxsize=128)(func)
        func.expiry = time() + seconds

        @wraps(func)
        def wrapper(*args, **kwargs):
            if time() > func.expiry:
                func.cache_clear()
                func.expiry = time() + seconds
            return func(*args, **kwargs)

        wrapper.cache_clear = func.cache_clear
        return wrapper

    return decorator

@timed_cache(seconds=300)
def fetch_config() -> dict:
    """Fetch config, cached for 5 minutes."""
    return requests.get(CONFIG_URL).json()
```

**Application-level caching:**
```python
class CachingRepository:
    def __init__(self, repository: Repository, cache: Cache) -> None:
        self._repository = repository
        self._cache = cache

    def get(self, id: int) -> Entity | None:
        # Check cache first
        cached = self._cache.get(f"entity:{id}")
        if cached is not None:
            return cached

        # Fetch from database
        entity = self._repository.get(id)
        if entity is not None:
            self._cache.set(f"entity:{id}", entity, ttl=300)

        return entity

    def save(self, entity: Entity) -> Entity:
        saved = self._repository.save(entity)
        # Invalidate cache on write
        self._cache.delete(f"entity:{saved.id}")
        return saved
```

---

### Database Query Optimization

**Select only needed columns:**
```python
# BAD: Selects all columns
users = session.query(User).all()
names = [u.name for u in users]

# GOOD: Select only what you need
names = session.query(User.name).all()

# GOOD: With SQLAlchemy 2.0
from sqlalchemy import select

stmt = select(User.id, User.name).where(User.status == "active")
results = session.execute(stmt).all()
```

**Avoid N+1 queries:**
```python
# BAD: N+1 queries (1 for orders + N for users)
orders = session.query(Order).all()
for order in orders:
    print(order.user.name)  # Lazy load triggers query for each order!

# GOOD: Eager loading with joinedload
from sqlalchemy.orm import joinedload

orders = session.query(Order).options(joinedload(Order.user)).all()
for order in orders:
    print(order.user.name)  # Already loaded, no extra queries

# GOOD: Or use selectinload for collections
orders = session.query(Order).options(selectinload(Order.items)).all()
```

**Use appropriate indexes:**
```python
# In SQLAlchemy model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)  # Indexed for lookups
    status = Column(String, index=True)  # Indexed for filtering
    created_at = Column(DateTime, index=True)  # Indexed for sorting

    # Composite index for common query patterns
    __table_args__ = (
        Index("ix_users_status_created", "status", "created_at"),
    )
```

**Pagination best practices:**
```python
# BAD: Offset pagination for large datasets
# Gets slower as offset increases
page_100 = session.query(User).offset(10000).limit(100).all()  # Slow!

# GOOD: Keyset pagination for large datasets
# Consistent performance regardless of page
last_id = 10000
next_page = (
    session.query(User)
    .where(User.id > last_id)
    .order_by(User.id)
    .limit(100)
    .all()
)
```

---

### Async Best Practices

**Concurrent I/O with gather:**
```python
# BAD: Sequential I/O
async def fetch_user_data(user_id: int) -> UserData:
    user = await user_service.get(user_id)  # Wait
    orders = await order_service.get_by_user(user_id)  # Then wait
    preferences = await preference_service.get(user_id)  # Then wait
    return UserData(user, orders, preferences)

# GOOD: Concurrent I/O
async def fetch_user_data(user_id: int) -> UserData:
    user, orders, preferences = await asyncio.gather(
        user_service.get(user_id),
        order_service.get_by_user(user_id),
        preference_service.get(user_id),
    )
    return UserData(user, orders, preferences)
```

**Connection pooling:**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Configure pool for async
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,  # Concurrent connections
    max_overflow=10,  # Additional connections when pool exhausted
    pool_pre_ping=True,  # Verify connections before use
)

# For HTTP clients
import httpx

async with httpx.AsyncClient(
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
) as client:
    responses = await asyncio.gather(
        client.get(url1),
        client.get(url2),
        client.get(url3),
    )
```

**Never block the event loop:**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# BAD: Blocks event loop
async def process_image(image_bytes: bytes) -> bytes:
    return heavy_cpu_work(image_bytes)  # Blocks all async tasks!

# GOOD: Run CPU work in thread pool
async def process_image(image_bytes: bytes) -> bytes:
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, heavy_cpu_work, image_bytes)

# GOOD: Or use dedicated process pool for CPU-bound work
from concurrent.futures import ProcessPoolExecutor

async def process_images(images: list[bytes]) -> list[bytes]:
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor() as pool:
        tasks = [loop.run_in_executor(pool, heavy_cpu_work, img) for img in images]
        return await asyncio.gather(*tasks)
```

---

### Memory Management

**Use __slots__ for data classes:**
```python
# Regular class: ~200 bytes per instance
class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

# With __slots__: ~56 bytes per instance
class Point:
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

# With dataclass
from dataclasses import dataclass

@dataclass(slots=True)  # Python 3.10+
class Point:
    x: float
    y: float
```

**Stream large files:**
```python
# BAD: Load entire file into memory
def process_large_file(path: str) -> None:
    content = Path(path).read_text()  # Could be gigabytes!
    for line in content.split("\n"):
        process(line)

# GOOD: Stream line by line
def process_large_file(path: str) -> None:
    with open(path) as f:
        for line in f:  # Memory: O(1)
            process(line)

# GOOD: For binary files, use chunks
def copy_large_file(src: str, dst: str, chunk_size: int = 8192) -> None:
    with open(src, "rb") as source, open(dst, "wb") as dest:
        while chunk := source.read(chunk_size):
            dest.write(chunk)
```

---

### Performance Checklist

**Before optimizing:**
- [ ] Is there actually a performance problem?
- [ ] Have you measured and profiled?
- [ ] Do you know which part is slow?
- [ ] Will the optimization make code harder to read?

**Common optimizations:**
- [ ] Use generators for large sequences
- [ ] Cache expensive computations
- [ ] Select only needed database columns
- [ ] Use eager loading to avoid N+1
- [ ] Add appropriate database indexes
- [ ] Use connection pooling
- [ ] Parallelize I/O operations
- [ ] Stream large files
- [ ] Use __slots__ for memory-heavy classes
