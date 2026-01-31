# Filtering Example

This example demonstrates query filtering with predicates and JSON Logic.

## Complete Example

```python
"""Filtering example with pypaginate."""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import Column, DateTime, Float, Integer, String, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from pypaginate.core import PageParams
from pypaginate.query import paginate_entities_to_page
from pypaginate.filters.predicates import FilterEngine


# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./products.db"
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Product({self.name}, ${self.price}, stock={self.stock})"


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_data():
    async with async_session() as session:
        result = await session.execute(select(Product).limit(1))
        if result.scalar():
            return
        
        products = [
            Product(name="iPhone 15", category="Electronics", price=999.99, stock=50),
            Product(name="MacBook Pro", category="Electronics", price=2499.99, stock=25),
            Product(name="AirPods Pro", category="Electronics", price=249.99, stock=100),
            Product(name="Python Book", category="Books", price=49.99, stock=200),
            Product(name="JavaScript Guide", category="Books", price=39.99, stock=150),
            Product(name="Office Chair", category="Furniture", price=299.99, stock=30),
            Product(name="Standing Desk", category="Furniture", price=599.99, stock=15),
            Product(name="Coffee Maker", category="Appliances", price=79.99, stock=80),
            Product(name="Blender", category="Appliances", price=49.99, stock=60),
            Product(name="Headphones", category="Electronics", price=199.99, stock=0),
        ]
        session.add_all(products)
        await session.commit()
        print(f"Created {len(products)} products")


async def filter_products(filters: dict, page: int = 1, limit: int = 10):
    """Filter and paginate products."""
    async with async_session() as session:
        stmt = select(Product).order_by(Product.id)
        
        # Apply filters
        if filters:
            engine = FilterEngine()
            conditions = engine.build_conditions(Product, filters)
            stmt = stmt.where(*conditions)
        
        params = PageParams(page=page, limit=limit)
        return await paginate_entities_to_page(session, stmt, params)


async def main():
    await create_tables()
    await seed_data()
    
    # Example 1: Filter by category
    print("\n=== Electronics ===")
    page = await filter_products({"category": {"eq": "Electronics"}})
    for p in page.items:
        print(f"  {p}")
    
    # Example 2: Price range
    print("\n=== Products $50-$300 ===")
    page = await filter_products({
        "price": {"gte": 50, "lte": 300}
    })
    for p in page.items:
        print(f"  {p}")
    
    # Example 3: In stock only
    print("\n=== In Stock (stock > 0) ===")
    page = await filter_products({
        "stock": {"gt": 0}
    })
    print(f"  Found {page.total} products in stock")
    
    # Example 4: Multiple conditions
    print("\n=== Electronics under $500 with stock ===")
    page = await filter_products({
        "category": {"eq": "Electronics"},
        "price": {"lt": 500},
        "stock": {"gt": 0},
    })
    for p in page.items:
        print(f"  {p}")
    
    # Example 5: Text search with LIKE
    print("\n=== Products with 'Pro' in name ===")
    page = await filter_products({
        "name": {"ilike": "%Pro%"}
    })
    for p in page.items:
        print(f"  {p}")
    
    # Example 6: Category in list
    print("\n=== Books or Furniture ===")
    page = await filter_products({
        "category": {"in": ["Books", "Furniture"]}
    })
    for p in page.items:
        print(f"  {p}")


if __name__ == "__main__":
    asyncio.run(main())
```

## Output

```
Created 10 products

=== Electronics ===
  Product(iPhone 15, $999.99, stock=50)
  Product(MacBook Pro, $2499.99, stock=25)
  Product(AirPods Pro, $249.99, stock=100)
  Product(Headphones, $199.99, stock=0)

=== Products $50-$300 ===
  Product(AirPods Pro, $249.99, stock=100)
  Product(Office Chair, $299.99, stock=30)
  Product(Coffee Maker, $79.99, stock=80)
  Product(Headphones, $199.99, stock=0)

=== In Stock (stock > 0) ===
  Found 9 products in stock

=== Electronics under $500 with stock ===
  Product(AirPods Pro, $249.99, stock=100)

=== Products with 'Pro' in name ===
  Product(MacBook Pro, $2499.99, stock=25)
  Product(AirPods Pro, $249.99, stock=100)

=== Books or Furniture ===
  Product(Python Book, $49.99, stock=200)
  Product(JavaScript Guide, $39.99, stock=150)
  Product(Office Chair, $299.99, stock=30)
  Product(Standing Desk, $599.99, stock=15)
```

## Available Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `eq` | Equals | `{"status": {"eq": "active"}}` |
| `ne` | Not equals | `{"status": {"ne": "deleted"}}` |
| `gt` | Greater than | `{"price": {"gt": 100}}` |
| `gte` | Greater or equal | `{"price": {"gte": 100}}` |
| `lt` | Less than | `{"price": {"lt": 100}}` |
| `lte` | Less or equal | `{"price": {"lte": 100}}` |
| `in` | In list | `{"category": {"in": ["A", "B"]}}` |
| `not_in` | Not in list | `{"status": {"not_in": ["x"]}}` |
| `like` | SQL LIKE | `{"name": {"like": "A%"}}` |
| `ilike` | Case-insensitive LIKE | `{"name": {"ilike": "%test%"}}` |
| `is_null` | Is NULL | `{"deleted_at": {"is_null": true}}` |

## JSON Logic Example

For complex OR conditions:

```python
filters = {
    "or": [
        {"category": {"eq": "Electronics"}},
        {"price": {"lt": 50}},
    ]
}
page = await filter_products(filters)
```

## Next Steps

- [FastAPI Example](fastapi.md) - Expose filters via API
- [Search Example](../user-guide/search/text-search.md) - Full-text search
