# Filters Module

The filters module provides query filtering capabilities including predicates, JSON Logic evaluation, and field accessors.

## FilterEngine

Main filtering engine for building SQLAlchemy query conditions from filter dictionaries.

```{eval-rst}
.. autoclass:: pypaginate.filters.predicates.FilterEngine
   :members:
   :show-inheritance:
```

## CompiledFilter

Compiled filter object for efficient repeated filtering operations.

```{eval-rst}
.. autoclass:: pypaginate.filters.predicates.CompiledFilter
   :members:
   :show-inheritance:
```

## Helper Functions

```{eval-rst}
.. autofunction:: pypaginate.filters.predicates.filter_items
```

## Predicate Builder

Builds predicates from JSON Logic expressions.

```{eval-rst}
.. autoclass:: pypaginate.filters.predicates.JsonLogicPredicateBuilder
   :members:
   :show-inheritance:
```

## Field Accessor

Provides attribute access for filter evaluation on objects and dictionaries.

```{eval-rst}
.. autoclass:: pypaginate.filters.predicates.FieldAccessor
   :members:
   :show-inheritance:
```

## Operator Registry

Registry for filter operators and their implementations.

```{eval-rst}
.. autoclass:: pypaginate.filters.predicates.OperatorRegistry
   :members:
   :show-inheritance:
```

```{eval-rst}
.. autoclass:: pypaginate.filters.predicates.FilterPredicate
   :members:
   :show-inheritance:
```

```{eval-rst}
.. autoclass:: pypaginate.filters.predicates.OperatorFactory
   :members:
   :show-inheritance:
```

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

## Available Operators

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
