# Concepts

This section explains the core concepts behind pypaginate v0.2, helping you understand
how the library works and make informed decisions about which features to use.

## Why Read This?

While you can use pypaginate by following the guides, understanding the concepts helps you:

- **Choose the right pagination strategy** for your use case
- **Design efficient filter and search queries** that scale
- **Debug issues** when things don't work as expected
- **Extend the library** with custom backends

## Topics

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} Architecture
:link: architecture
:link-type: doc

Hexagonal architecture, domain/engine/adapter layers, and protocol-based backends.
:::

:::{grid-item-card} Pagination Strategies
:link: pagination-strategies
:link-type: doc

Offset vs cursor pagination, their trade-offs, and when to use each.
:::

:::{grid-item-card} Cursor Encoding
:link: cursor-encoding
:link-type: doc

How cursor values work with sqlakeyset for keyset pagination.
:::

:::{grid-item-card} Filter Expressions
:link: filter-expressions
:link-type: doc

FilterSpec, And/Or groups, nested FilterGroup trees, and 20 operators.
:::

:::{grid-item-card} Search & Relevance
:link: search-relevance
:link-type: doc

Scoring, weights, fuzzy modes, threshold, and Unicode normalization.
:::

::::

## How pypaginate Works

```{mermaid}
graph TB
    subgraph "User Input"
        P["OffsetParams / CursorParams"]
        F["FilterSpec / FilterGroup"]
        S["SortSpec"]
        Q["SearchSpec"]
    end

    subgraph "Engine Layer"
        D["paginate() dispatch"]
        PL["Pipeline (filter→sort→search→paginate)"]
        PAG["Paginator (count→clamp→fetch→Page)"]
    end

    subgraph "Adapter Layer"
        MEM["Memory backends"]
        SA["SQLAlchemy backends"]
        FA["FastAPI dependencies"]
    end

    subgraph "Output"
        OP["OffsetPage[T]"]
        CP["CursorPage[T]"]
    end

    P --> D
    F --> PL
    S --> PL
    Q --> PL
    D --> PAG
    PL --> PAG
    PAG --> MEM
    PAG --> SA
    FA --> P
    MEM --> OP
    SA --> OP
    SA --> CP
```

## Key Decisions

| Decision | Options | When to Choose |
|----------|---------|----------------|
| **Pagination mode** | `OffsetParams`, `CursorParams` | Offset for page numbers, cursor for infinite scroll |
| **Data source** | In-memory list, SQLAlchemy query | SQLAlchemy for database-backed apps |
| **Filter format** | Flat `FilterSpec` list, nested `And`/`Or` groups | Groups for complex boolean logic |
| **Search mode** | `FuzzyMode.EXACT`, `FUZZY`, `TOKEN_SORT` | Fuzzy for typo tolerance, token sort for word-order agnostic |
| **Page construction** | Pydantic (default), msgspec (`pypaginate[fast]`) | msgspec for near-zero overhead in hot paths |
