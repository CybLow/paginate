---
name: perf-database
description: >
  Database performance optimization. Covers query analysis with EXPLAIN, connection pool
  tuning, batch operations, streaming results, and SQLAlchemy optimization patterns.
related:
  - perf-core
  - perf-apm
  - api-rest
---

## DATABASE OPTIMIZATION

Advanced database performance techniques.

---

### Query Analysis with EXPLAIN

```python
from sqlalchemy import text


async def analyze_query(session, query) -> dict:
    """Analyze query execution plan."""
    # Get the compiled SQL
    compiled = query.compile(
        compile_kwargs={"literal_binds": True}
    )
    sql = str(compiled)
    
    # Run EXPLAIN ANALYZE (PostgreSQL)
    explain_result = await session.execute(
        text(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {sql}")
    )
    plan = explain_result.scalar_one()
    
    return {
        "sql": sql,
        "plan": plan,
        "execution_time_ms": plan[0]["Execution Time"],
        "planning_time_ms": plan[0]["Planning Time"],
    }


# Automatic slow query logging
class SlowQueryMiddleware:
    SLOW_QUERY_THRESHOLD_MS = 100
    
    async def __call__(self, query, args, context):
        start = time.perf_counter()
        result = await context.execute(query, args)
        duration_ms = (time.perf_counter() - start) * 1000
        
        if duration_ms > self.SLOW_QUERY_THRESHOLD_MS:
            logger.warning(
                "slow_query",
                query=str(query),
                duration_ms=duration_ms,
            )
        
        return result
```

### Connection Pool Optimization

```python
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import QueuePool


def create_optimized_engine(database_url: str, pool_config: dict = None):
    """Create database engine with optimized pool settings."""
    default_config = {
        # Core pool settings
        "pool_size": 10,           # Base connections
        "max_overflow": 20,        # Extra connections when busy
        "pool_timeout": 30,        # Seconds to wait for connection
        "pool_recycle": 1800,      # Recycle connections after 30 min
        "pool_pre_ping": True,     # Verify connection before use
        
        # Performance settings
        "echo": False,             # Don't log all queries
        "echo_pool": False,        # Don't log pool events
        
        # Connection args
        "connect_args": {
            "prepared_statement_cache_size": 500,  # asyncpg
            "statement_cache_size": 500,
        },
    }
    
    config = {**default_config, **(pool_config or {})}
    
    return create_async_engine(
        database_url,
        poolclass=QueuePool,
        **config,
    )


# Monitor pool health
async def get_pool_stats(engine) -> dict:
    """Get connection pool statistics."""
    pool = engine.pool
    return {
        "size": pool.size(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "checked_in": pool.checkedin(),
    }
```

### Query Optimization Patterns

```python
# Batch operations
async def bulk_insert(session, items: list[Item]) -> None:
    """Efficient bulk insert."""
    # BAD: Individual inserts
    for item in items:
        session.add(item)
        await session.commit()  # N commits!
    
    # GOOD: Batch insert
    session.add_all(items)
    await session.commit()  # 1 commit
    
    # BETTER: Use executemany for large batches
    await session.execute(
        insert(Item),
        [item.model_dump() for item in items]
    )
    await session.commit()


# Streaming large results
async def stream_large_result(session):
    """Stream results without loading all into memory."""
    # BAD: Load all into memory
    results = await session.execute(select(LargeTable))
    all_rows = results.scalars().all()  # Memory explosion!
    
    # GOOD: Stream with server-side cursor
    async with session.stream(select(LargeTable)) as stream:
        async for row in stream:
            yield row


# Avoid SELECT N+1 with proper loading
from sqlalchemy.orm import selectinload, joinedload


async def get_orders_with_items(session) -> list[Order]:
    """Fetch orders with items efficiently."""
    stmt = (
        select(Order)
        .options(
            joinedload(Order.user),           # 1:1 relationship
            selectinload(Order.items),        # 1:N relationship
            selectinload(Order.items).joinedload(OrderItem.product),
        )
        .where(Order.status == "active")
    )
    result = await session.execute(stmt)
    return result.scalars().unique().all()
```

---

## INDEX OPTIMIZATION

### Index Types

```python
from sqlalchemy import Index, Column, String, Integer

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)  # B-tree index
    category = Column(String)
    price = Column(Integer)
    tags = Column(ARRAY(String))
    
    __table_args__ = (
        # Composite index
        Index("ix_category_price", "category", "price"),
        
        # Partial index
        Index(
            "ix_active_products",
            "category",
            postgresql_where=text("status = 'active'"),
        ),
        
        # GIN index for array/JSONB
        Index(
            "ix_tags_gin",
            "tags",
            postgresql_using="gin",
        ),
    )
```

### Index Selection Guidelines

| Query Pattern | Index Type |
|---------------|------------|
| Equality lookup | B-tree |
| Range queries | B-tree |
| Full-text search | GIN/GiST |
| Array contains | GIN |
| JSONB queries | GIN |
| Geospatial | GiST |
| Pattern matching (LIKE) | B-tree (prefix only) |

---

## TRANSACTION MANAGEMENT

### Connection Context

```python
from contextlib import asynccontextmanager


@asynccontextmanager
async def transaction(session):
    """Automatic transaction management."""
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise


async def transfer_funds(from_id: int, to_id: int, amount: float):
    async with get_session() as session:
        async with transaction(session):
            from_account = await session.get(Account, from_id)
            to_account = await session.get(Account, to_id)
            
            from_account.balance -= amount
            to_account.balance += amount
            # Commits on exit, rolls back on exception
```

### Isolation Levels

```python
from sqlalchemy.orm import Session

# Read committed (default)
async with session.begin():
    ...

# Serializable (strongest)
async with session.begin():
    await session.execute(
        text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    )
    ...
```

---

## QUICK REFERENCE

### Performance Metrics to Track

| Metric | Description | Target |
|--------|-------------|--------|
| P50 latency | Median response time | < 50ms |
| P95 latency | 95th percentile | < 200ms |
| P99 latency | 99th percentile | < 500ms |
| DB pool usage | Connection pool | < 70% |
| Queries per request | N+1 detection | 1-5 |

### Database Optimization Checklist

```
[ ] Indexes on frequently queried columns
[ ] Composite indexes for common query patterns
[ ] Avoid SELECT * - select only needed columns
[ ] Use eager loading to prevent N+1
[ ] Batch writes instead of individual inserts
[ ] Use keyset pagination for large datasets
[ ] Monitor and log slow queries
[ ] Tune connection pool size
[ ] Enable query plan caching
[ ] Regular VACUUM/ANALYZE (PostgreSQL)
```

### SQLAlchemy Loading Strategies

| Strategy | Use Case | SQL Queries |
|----------|----------|-------------|
| `lazy` (default) | Rarely accessed | N+1 risk |
| `joinedload` | 1:1 relationships | 1 (JOIN) |
| `selectinload` | 1:N relationships | 2 (IN clause) |
| `subqueryload` | Large result sets | 2 (subquery) |
| `raiseload` | Prevent lazy loads | Error if accessed |
