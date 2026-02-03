# Examples

This section provides complete, runnable examples demonstrating pypaginate features in real-world scenarios.

## Quick Links

| Example | Description |
|---------|-------------|
| [Basic Pagination](basic-pagination.md) | Simple pagination with SQLAlchemy |
| [Filtering](filtering.md) | Query filtering with predicates |
| [FastAPI Integration](fastapi.md) | Complete FastAPI REST API |
| [Keyset Pagination](keyset.md) | Cursor-based pagination for large datasets |

## Prerequisites

All examples assume you have pypaginate installed:

```bash
uv add pypaginate[all]
```

## Database Setup

Most examples use SQLAlchemy with an async SQLite database:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Create async engine
DATABASE_URL = "sqlite+aiosqlite:///./example.db"
engine = create_async_engine(DATABASE_URL, echo=True)

# Session factory
async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Base class for models
class Base(DeclarativeBase):
    pass

# Example model
class User(Base):
    __tablename__ = "users"
    
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(100), nullable=False)
    email: str = Column(String(255), unique=True, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
```

## Running Examples

Each example can be run as a standalone script:

```bash
# Clone the repository
git clone https://github.com/CybLow/pypaginate.git
cd pypaginate

# Install dependencies
uv add -e ".[all]"

# Run an example
python examples/basic_pagination.py
```

## Example Categories

### Getting Started

- **Basic Pagination** - Learn the fundamentals
- **Simple Filtering** - Add filters to queries

### Intermediate

- **FastAPI Integration** - Build a REST API
- **Multi-column Sorting** - Complex ordering
- **Search with Fuzzy Matching** - Text search

### Advanced

- **Keyset Pagination** - Handle large datasets
- **Custom Response Formats** - Extend response models
- **Performance Optimization** - Tune for production

## Contributing Examples

We welcome example contributions! See [Contributing](../contributing/index.md) for guidelines.
