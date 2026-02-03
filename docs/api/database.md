# Database Types

The database module provides utilities for database-specific operations, including collation management and type aliases for SQLAlchemy statements.

## Overview

| Symbol | Type | Description |
|--------|------|-------------|
| `CollationPlan` | Class | Describes SQL statements for collation setup |
| `SelectStatement` | TypeAlias | Typed SQLAlchemy Select statement |
| `CountStatement` | TypeAlias | Select statement returning integer count |
| `ensure_database_collations` | Function | Apply collation plan to database |
| `recommend_collation_plan` | Function | Get recommended plan for dialect |

## Type Aliases

### SelectStatement

::: pypaginate.database.SelectStatement
    options:
      show_source: true

### CountStatement

::: pypaginate.database.CountStatement
    options:
      show_source: true

## CollationPlan

::: pypaginate.database.CollationPlan
    options:
      show_source: true
      members:
        - statements
        - notes

## ensure_database_collations

::: pypaginate.database.ensure_database_collations
    options:
      show_source: true

## recommend_collation_plan

::: pypaginate.database.recommend_collation_plan
    options:
      show_source: true

## Usage Examples

### Setting Up Database Collations

```python
from sqlalchemy.ext.asyncio import create_async_engine

from pypaginate.database import ensure_database_collations


async def setup_database() -> None:
    engine = create_async_engine("postgresql+asyncpg://...")
    
    # Automatically applies the correct collation plan
    plan = await ensure_database_collations(engine)
    
    if plan:
        print(f"Applied {len(plan.statements)} statements")
        for note in plan.notes:
            print(f"Note: {note}")
```

### Checking Available Plans

```python
from pypaginate.database import recommend_collation_plan

# Check what would be applied
postgres_plan = recommend_collation_plan("postgresql")
if postgres_plan:
    print("PostgreSQL statements:")
    for stmt in postgres_plan.statements:
        print(f"  {stmt}")

sqlite_plan = recommend_collation_plan("sqlite")
if sqlite_plan:
    print("SQLite notes:")
    for note in sqlite_plan.notes:
        print(f"  {note}")
```

### Using Type Aliases

```python
from sqlalchemy import func, select

from pypaginate.database import CountStatement, SelectStatement


def build_user_query() -> SelectStatement:
    """Build a typed select statement."""
    return select(User).where(User.active == True)


def build_count_query() -> CountStatement:
    """Build a typed count statement."""
    return select(func.count()).select_from(User)
```

## Supported Databases

### PostgreSQL

The PostgreSQL plan installs these extensions:

| Extension | Purpose |
|-----------|---------|
| `unaccent` | Remove diacritical marks for accent-insensitive search |
| `pg_trgm` | Trigram matching for fuzzy search and similarity |

**Notes:**

- Requires superuser rights for first-time extension installation
- Add GIN trigram indexes for optimal performance

```sql
-- Example index for trigram search
CREATE INDEX idx_users_name_trgm ON users USING GIN (name gin_trgm_ops);
```

### SQLite

SQLite has no statements but provides guidance:

**Notes:**

- Use FTS5 virtual tables with `tokenize=unicode61`
- Enable `remove_diacritics=2` for accent-insensitive search
- Set up triggers to mirror changes to FTS tables

```sql
-- Example FTS5 setup
CREATE VIRTUAL TABLE users_fts USING fts5(
    name, 
    email,
    tokenize='unicode61 remove_diacritics 2'
);
```

### Other Databases

Currently no plans for MySQL, MariaDB, or other databases. Use `recommend_collation_plan()` to check availability:

```python
plan = recommend_collation_plan("mysql")
if plan is None:
    print("No automatic collation plan for MySQL")
```
