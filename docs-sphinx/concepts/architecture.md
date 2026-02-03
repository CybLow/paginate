# Architecture

This page provides an overview of pypaginate's internal architecture, helping you
understand how components work together and where to extend the library.

## High-Level Architecture

```{mermaid}
graph TB
    subgraph "Public API"
        PA[paginate / search / filter]
    end
    
    subgraph "Engines"
        PE[Pagination Engines]
        FE[Filter Engine]
        SE[Search Engine]
        SO[Sort Engine]
    end
    
    subgraph "Adapters"
        SQL[SQLAlchemy Adapter]
        MEM[Memory Adapter]
    end
    
    subgraph "Core"
        Page[Page Models]
        Params[Parameters]
        Cursor[Cursor Encoding]
    end
    
    PA --> PE
    PA --> FE
    PA --> SE
    PA --> SO
    
    PE --> SQL
    PE --> MEM
    FE --> SQL
    FE --> MEM
    SE --> SQL
    SE --> MEM
    SO --> SQL
    SO --> MEM
    
    PE --> Page
    PE --> Cursor
    PA --> Params
```

## Layer Overview

| Layer | Purpose | Examples |
|-------|---------|----------|
| **Public API** | User-facing functions | `paginate()`, `search()` |
| **Engines** | Business logic | `OffsetPaginator`, `FilterEngine` |
| **Adapters** | Data source integration | `SQLAlchemyAdapter`, `MemoryAdapter` |
| **Core** | Shared models and utilities | `Page`, `PageParams`, `CursorEncoder` |

## Component Details

### Public API

The public API provides simple, unified functions:

```{mermaid}
classDiagram
    class paginate {
        +query: Any
        +params: PageParams
        +filters: dict
        +search: str
        +sort: list
        returns Page
    }
    
    class Page {
        +items: list
        +total: int
        +page: int
        +size: int
        +next_cursor: str
        +prev_cursor: str
    }
```

```python
from pypaginate import paginate, PageParams

# Simple, unified API
page = await paginate(
    query,
    params=PageParams(page=1, size=20),
    filters={"status": "active"},
    search="python",
    sort=["created_at:desc"]
)
```

### Pagination Engines

Three pagination engines handle different strategies:

```{mermaid}
classDiagram
    class PaginatorProtocol {
        <<protocol>>
        +paginate(query, params) Page
    }
    
    class OffsetPaginator {
        +paginate(query, params) Page
        -apply_offset(query, offset, limit)
        -count_total(query)
    }
    
    class KeysetPaginator {
        +paginate(query, params) Page
        -apply_cursor(query, cursor)
        -encode_cursor(item)
    }
    
    class MemoryPaginator {
        +paginate(items, params) Page
        -slice_items(items, offset, limit)
    }
    
    PaginatorProtocol <|.. OffsetPaginator
    PaginatorProtocol <|.. KeysetPaginator
    PaginatorProtocol <|.. MemoryPaginator
```

| Engine | Data Source | Strategy |
|--------|-------------|----------|
| `OffsetPaginator` | SQLAlchemy | LIMIT/OFFSET |
| `KeysetPaginator` | SQLAlchemy | WHERE + cursor |
| `MemoryPaginator` | Python lists | List slicing |

### Filter Engine

The filter engine converts expressions to queries or predicates:

```{mermaid}
classDiagram
    class FilterEngine {
        +registry: OperatorRegistry
        +apply(expression) Predicate
        +to_sql(expression) SQLClause
    }
    
    class OperatorRegistry {
        +operators: dict[str, Operator]
        +register(op: Operator)
        +get(name: str) Operator
    }
    
    class Operator {
        <<protocol>>
        +name: str
        +apply(field, value) bool
        +to_sql(column, value) Clause
    }
    
    FilterEngine --> OperatorRegistry
    OperatorRegistry --> Operator
```

### Search Engine

```{mermaid}
classDiagram
    class SearchEngine {
        +options: SearchOptions
        +search(query, term) Results
        +to_sql(term) SQLClause
    }
    
    class SearchOptions {
        +fields: dict[str, float]
        +mode: str
        +fuzzy: FuzzyOptions
    }
    
    class FuzzyMatcher {
        +threshold: float
        +match(query, text) float
    }
    
    SearchEngine --> SearchOptions
    SearchEngine --> FuzzyMatcher
```

### Sort Engine

```{mermaid}
classDiagram
    class SortEngine {
        +apply(query, specs) Query
        +parse(sort_string) list[SortSpec]
    }
    
    class SortSpec {
        +column: str
        +descending: bool
        +nulls: NullsPosition
    }
    
    SortEngine --> SortSpec
```

## Data Flow

### Paginate Request Flow

```{mermaid}
sequenceDiagram
    participant Client
    participant API as paginate()
    participant Engine as PaginatorEngine
    participant Adapter as SQLAlchemyAdapter
    participant DB as Database
    
    Client->>API: paginate(query, params)
    API->>Engine: select_engine(query)
    Engine->>Adapter: apply_filters(query, filters)
    Adapter->>Engine: filtered_query
    Engine->>Adapter: apply_sort(query, sort)
    Adapter->>Engine: sorted_query
    Engine->>Adapter: apply_pagination(query, params)
    Adapter->>DB: Execute SQL
    DB->>Adapter: Results
    Adapter->>Engine: Items + metadata
    Engine->>API: Page object
    API->>Client: Page
```

### Filter Processing Flow

```{mermaid}
sequenceDiagram
    participant Input as Expression
    participant Parser
    participant Validator
    participant Builder
    participant Output as SQL/Predicate
    
    Input->>Parser: Parse expression
    Parser->>Validator: Validate fields & operators
    Validator->>Builder: Build clauses
    Builder->>Output: SQL WHERE or Python predicate
```

## Extension Points

pypaginate is designed for extensibility at multiple levels:

### Custom Operators

```python
from pypaginate import Operator, FilterEngine

class GeolocationOperator(Operator):
    name = "near"
    
    def apply(self, field_value, params):
        lat, lng, radius = params
        return haversine_distance(field_value, (lat, lng)) <= radius
    
    def to_sql(self, column, params):
        lat, lng, radius = params
        return func.ST_DWithin(
            column, 
            func.ST_Point(lng, lat), 
            radius
        )

engine = FilterEngine()
engine.registry.register(GeolocationOperator())
```

### Custom Adapters

```python
from pypaginate import DataAdapter

class MongoAdapter(DataAdapter):
    """Adapter for MongoDB collections."""
    
    def apply_filter(self, collection, expression):
        return collection.find(self._to_mongo_query(expression))
    
    def apply_pagination(self, cursor, params):
        return cursor.skip(params.offset).limit(params.size)
    
    def count(self, collection, expression):
        return collection.count_documents(self._to_mongo_query(expression))
```

### Custom Paginators

```python
from pypaginate import PaginatorProtocol

class ElasticPaginator(PaginatorProtocol):
    """Paginator for Elasticsearch."""
    
    async def paginate(self, query, params):
        response = await self.client.search(
            body=query,
            from_=params.offset,
            size=params.size
        )
        return Page(
            items=response["hits"]["hits"],
            total=response["hits"]["total"]["value"],
            page=params.page,
            size=params.size
        )
```

## Dependency Injection

pypaginate uses dependency injection for flexibility:

```{mermaid}
graph TB
    subgraph "Injection Points"
        Config[Configuration]
        Engines[Engine Selection]
        Adapters[Adapter Selection]
        Operators[Operator Registry]
    end
    
    Config --> Engines
    Config --> Adapters
    Config --> Operators
```

### Configuration

```python
from pypaginate import configure, Configuration

configure(
    # Default pagination
    default_page_size=20,
    max_page_size=100,
    
    # Default engines
    pagination_engine="keyset",
    
    # Custom adapters
    adapters={
        "sqlalchemy": SQLAlchemyAdapter,
        "memory": MemoryAdapter,
        "mongo": MongoAdapter,  # Custom
    },
    
    # Operator registry
    operators=default_operators + [GeolocationOperator()]
)
```

## Protocol-Based Design

pypaginate uses Python Protocols for interface definitions:

```python
from typing import Protocol

class PaginatorProtocol(Protocol):
    """Interface for pagination engines."""
    
    async def paginate(
        self, 
        query: Any, 
        params: PageParams
    ) -> Page:
        """Paginate a query and return a Page."""
        ...

class DataAdapter(Protocol):
    """Interface for data source adapters."""
    
    def apply_filter(self, query: Any, expression: dict) -> Any:
        """Apply filter expression to query."""
        ...
    
    def apply_sort(self, query: Any, specs: list[SortSpec]) -> Any:
        """Apply sort specification to query."""
        ...
```

This enables static type checking while maintaining flexibility.

## Module Structure

```
pypaginate/
├── __init__.py          # Public API exports
├── core/                # Core models and utilities
│   ├── pages.py         # Page, PageParams
│   ├── context.py       # Request context
│   └── snapshots.py     # Query snapshots
├── engines/             # Pagination engines
│   ├── memory.py        # In-memory pagination
│   ├── sql.py           # SQLAlchemy offset
│   └── keyset.py        # Keyset/cursor pagination
├── filters/             # Filter system
│   ├── predicates/      # Filter operators
│   ├── search/          # Search functionality
│   └── sql_adapter.py   # SQL filter generation
├── sorting/             # Sort system
│   ├── engine.py        # Sort engine
│   └── sql_adapter.py   # SQL sort generation
├── integrations/        # Framework integrations
│   └── fastapi.py       # FastAPI dependencies
├── query/               # Query utilities
│   ├── async_api.py     # Async query functions
│   └── builders/        # Query builders
└── exceptions.py        # Exception hierarchy
```

## Error Handling

```{mermaid}
classDiagram
    class PaginateError {
        +message: str
    }
    
    class FilterError {
        +expression: dict
    }
    
    class UnknownFieldError {
        +field: str
    }
    
    class UnknownOperatorError {
        +operator: str
    }
    
    class CursorError {
        +cursor: str
    }
    
    class InvalidCursorError {
        +reason: str
    }
    
    PaginateError <|-- FilterError
    FilterError <|-- UnknownFieldError
    FilterError <|-- UnknownOperatorError
    PaginateError <|-- CursorError
    CursorError <|-- InvalidCursorError
```

## Performance Considerations

### Engine Selection

```{mermaid}
flowchart TD
    Q[Query Type?] --> SQL{SQLAlchemy?}
    SQL -->|Yes| Size{Dataset Size?}
    SQL -->|No| MEM[MemoryPaginator]
    
    Size -->|Large| KS[KeysetPaginator]
    Size -->|Small| OFF[OffsetPaginator]
```

### Lazy Evaluation

pypaginate uses lazy evaluation where possible:

```python
# Query is NOT executed yet
query = select(User).where(User.status == "active")

# Still not executed - just modified
filtered = engine.apply_filter(query, filters)

# NOW executed when items are accessed
page = await paginate(filtered, params)
```

### Connection Management

For async operations, connection management is critical:

```python
# Good: Uses connection pool
async with async_session() as session:
    page = await paginate(query, params)

# Bad: Creates new connection each time
page = await paginate(query, params)  # No session context
```

## Testing Architecture

```{mermaid}
graph TB
    subgraph "Test Layers"
        Unit[Unit Tests<br/>Individual components]
        Integration[Integration Tests<br/>Component interaction]
        E2E[E2E Tests<br/>Full request/response]
    end
    
    subgraph "Test Fixtures"
        Mock[Mock Adapters]
        Mem[In-Memory DB]
        Real[Real Database]
    end
    
    Unit --> Mock
    Integration --> Mem
    E2E --> Real
```

## Further Reading

- [Pagination Strategies](pagination-strategies.md) - Understanding pagination
- [Filter Expressions](filter-expressions.md) - Filter system details
- [Search & Relevance](search-relevance.md) - Search implementation
- [Contributing: Architecture](../contributing/architecture.md) - Development details
