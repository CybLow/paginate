# Concepts

This section explains the core concepts behind pypaginate, helping you understand
how the library works and make informed decisions about which features to use.

## Why Read This?

While you can use pypaginate effectively by following the documentation,
understanding the underlying concepts will help you:

- **Choose the right pagination strategy** for your use case
- **Optimize performance** for large datasets
- **Debug issues** when things don't work as expected
- **Extend the library** for custom requirements

## Topics

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} Pagination Strategies
:link: pagination-strategies
:link-type: doc

Understand offset vs keyset pagination, their trade-offs, and when to use each.
:::

:::{grid-item-card} Cursor Encoding
:link: cursor-encoding
:link-type: doc

How cursors work, what they contain, and how they enable stateless pagination.
:::

:::{grid-item-card} Filter Expressions
:link: filter-expressions
:link-type: doc

The filter engine architecture, operators, and how expressions are evaluated.
:::

:::{grid-item-card} Search & Relevance
:link: search-relevance
:link-type: doc

How text search works, relevance scoring, and fuzzy matching algorithms.
:::

:::{grid-item-card} Architecture
:link: architecture
:link-type: doc

Overall library design, component relationships, and extension points.
:::

::::

## Quick Concept Overview

```{mermaid}
graph TB
    subgraph "pypaginate Components"
        direction TB
        
        subgraph "Input Processing"
            Params[Page Parameters]
            Filters[Filter Expression]
            Search[Search Query]
            Sort[Sort Specification]
        end
        
        subgraph "Core Engines"
            PE[Pagination Engine]
            FE[Filter Engine]
            SE[Search Engine]
            SO[Sort Engine]
        end
        
        subgraph "Data Sources"
            SQL[(SQLAlchemy)]
            Mem[In-Memory]
        end
        
        subgraph "Output"
            Page[Page Result]
            Cursor[Next/Prev Cursors]
            Meta[Metadata]
        end
    end
    
    Params --> PE
    Filters --> FE
    Search --> SE
    Sort --> SO
    
    PE --> SQL
    PE --> Mem
    FE --> SQL
    FE --> Mem
    SE --> SQL
    SE --> Mem
    SO --> SQL
    SO --> Mem
    
    SQL --> Page
    Mem --> Page
    Page --> Cursor
    Page --> Meta
```

## Key Decisions

When using pypaginate, you'll need to make a few key decisions:

| Decision | Options | Recommendation |
|----------|---------|----------------|
| **Pagination Style** | Offset, Keyset | Use keyset for large datasets or infinite scroll |
| **Data Source** | SQLAlchemy, In-Memory | Use SQLAlchemy for database-backed apps |
| **Filter Format** | Dict predicates, JSONLogic | Use JSONLogic for complex client-defined filters |
| **Search Type** | Simple, Fuzzy | Use fuzzy for user-facing search with typo tolerance |
