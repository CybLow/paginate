# Filters Module

The filters module provides query filtering capabilities including predicates, JSON Logic evaluation, and field accessors.

## FilterEngine

Main filtering engine for building query conditions.

::: pypaginate.filters.predicates.engine.FilterEngine
    options:
      show_source: true

## Predicate Builder

::: pypaginate.filters.predicates.builder
    options:
      show_source: true

## Operators

### Comparison Operators

::: pypaginate.filters.predicates.operators.comparison
    options:
      show_source: true

### Text Operators

::: pypaginate.filters.predicates.operators.text
    options:
      show_source: true

### Range Operators

::: pypaginate.filters.predicates.operators.range
    options:
      show_source: true

### Pattern Operators

::: pypaginate.filters.predicates.operators.patterns
    options:
      show_source: true

## JSON Logic Evaluator

::: pypaginate.filters.predicates.jsonlogic_evaluator
    options:
      show_source: true

## Field Accessor

::: pypaginate.filters.predicates.field_accessor
    options:
      show_source: true

## Operator Registry

::: pypaginate.filters.predicates.registry
    options:
      show_source: true

## SQL Filter Adapter

::: pypaginate.filters.sql_adapter
    options:
      show_source: true

## Usage Examples

### Basic Filtering

```python
from pypaginate.filters.predicates import FilterEngine

engine = FilterEngine()

# Simple equality filter
filters = {"status": {"eq": "active"}}
conditions = engine.build_conditions(User, filters)

# Apply to query
stmt = select(User).where(*conditions)
```

### Multiple Conditions

```python
filters = {
    "age": {"gte": 18, "lte": 65},
    "status": {"eq": "active"},
    "country": {"in": ["US", "UK", "CA"]},
}

conditions = engine.build_conditions(User, filters)
stmt = select(User).where(*conditions)
```

### JSON Logic Filters

```python
from pypaginate.filters.predicates import FilterEngine

engine = FilterEngine()

# Complex filter with AND/OR logic
filters = {
    "and": [
        {"age": {"gte": 18}},
        {"or": [
            {"country": {"eq": "US"}},
            {"country": {"eq": "UK"}},
        ]},
    ]
}

conditions = engine.build_conditions(User, filters)
```

### Text Operators

```python
filters = {
    "name": {"ilike": "%john%"},      # Case-insensitive LIKE
    "email": {"endswith": "@example.com"},
    "bio": {"contains": "developer"},
}
```

### Available Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `eq` | Equals | `{"status": {"eq": "active"}}` |
| `ne` | Not equals | `{"status": {"ne": "deleted"}}` |
| `gt` | Greater than | `{"age": {"gt": 18}}` |
| `gte` | Greater than or equal | `{"age": {"gte": 18}}` |
| `lt` | Less than | `{"age": {"lt": 65}}` |
| `lte` | Less than or equal | `{"age": {"lte": 65}}` |
| `in` | In list | `{"status": {"in": ["a", "b"]}}` |
| `not_in` | Not in list | `{"status": {"not_in": ["x"]}}` |
| `like` | SQL LIKE | `{"name": {"like": "J%"}}` |
| `ilike` | Case-insensitive LIKE | `{"name": {"ilike": "%john%"}}` |
| `startswith` | Starts with | `{"name": {"startswith": "J"}}` |
| `endswith` | Ends with | `{"email": {"endswith": ".com"}}` |
| `contains` | Contains substring | `{"bio": {"contains": "dev"}}` |
| `is_null` | Is NULL | `{"deleted_at": {"is_null": true}}` |
