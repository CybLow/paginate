# Filter Expressions

pypaginate's filter engine provides a powerful way to filter data using a structured
expression format. This page explains how filter expressions work and how they're evaluated.

## Overview

```{mermaid}
graph LR
    subgraph "Filter Pipeline"
        E[Expression] --> P[Parser]
        P --> V[Validator]
        V --> B[Builder]
        B --> Q[Query/Predicate]
    end
```

Filter expressions are processed in stages:

1. **Parse** - Convert input format to internal representation
2. **Validate** - Check field names, operators, and value types
3. **Build** - Generate SQL WHERE clauses or Python predicates
4. **Apply** - Execute against the data source

## Expression Formats

pypaginate supports two filter expression formats:

### Dictionary Format

Simple, Pythonic format for basic filtering:

```python
filters = {
    "status": "active",
    "age__gte": 18,
    "name__icontains": "john"
}
```

### JSONLogic Format

Structured format for complex, nested logic:

```python
filters = {
    "and": [
        {"==": [{"var": "status"}, "active"]},
        {">=": [{"var": "age"}, 18]},
        {"or": [
            {"in": [{"var": "role"}, ["admin", "moderator"]]},
            {">=": [{"var": "experience"}, 5]}
        ]}
    ]
}
```

## Filter Engine Architecture

```{mermaid}
classDiagram
    class FilterEngine {
        +registry: OperatorRegistry
        +apply(data, expression) Result
        +to_sql(expression) SQLClause
    }
    
    class OperatorRegistry {
        +operators: dict
        +register(name, operator)
        +get(name) Operator
    }
    
    class Operator {
        <<interface>>
        +apply(field, value) bool
        +to_sql(column, value) Clause
    }
    
    class ComparisonOperator {
        +apply(field, value) bool
        +to_sql(column, value) Clause
    }
    
    class PatternOperator {
        +apply(field, value) bool
        +to_sql(column, value) Clause
    }
    
    FilterEngine --> OperatorRegistry
    OperatorRegistry --> Operator
    Operator <|-- ComparisonOperator
    Operator <|-- PatternOperator
```

## Operators

### Comparison Operators

| Operator | SQL Equivalent | Description |
|----------|---------------|-------------|
| `eq` / `==` | `=` | Equal |
| `ne` / `!=` | `!=` | Not equal |
| `gt` / `>` | `>` | Greater than |
| `gte` / `>=` | `>=` | Greater than or equal |
| `lt` / `<` | `<` | Less than |
| `lte` / `<=` | `<=` | Less than or equal |

### Membership Operators

| Operator | SQL Equivalent | Description |
|----------|---------------|-------------|
| `in` | `IN (...)` | Value in list |
| `not_in` | `NOT IN (...)` | Value not in list |
| `between` | `BETWEEN ... AND ...` | Value in range (inclusive) |

### Pattern Operators

| Operator | SQL Equivalent | Description |
|----------|---------------|-------------|
| `contains` | `LIKE '%...%'` | Contains substring (case-sensitive) |
| `icontains` | `ILIKE '%...%'` | Contains substring (case-insensitive) |
| `startswith` | `LIKE '...%'` | Starts with prefix |
| `endswith` | `LIKE '%...'` | Ends with suffix |
| `regex` | `~` / `REGEXP` | Matches regex pattern |

### Null Operators

| Operator | SQL Equivalent | Description |
|----------|---------------|-------------|
| `is_null` | `IS NULL` | Field is null |
| `is_not_null` | `IS NOT NULL` | Field is not null |

## Expression Evaluation

### Dictionary Format Parsing

```{mermaid}
flowchart TD
    D["{'status': 'active', 'age__gte': 18}"] --> P[Parse]
    P --> E1["field='status', op='eq', value='active'"]
    P --> E2["field='age', op='gte', value=18"]
    E1 --> AND[AND together]
    E2 --> AND
    AND --> R[Result]
```

The double-underscore (`__`) separates field names from operators:

| Expression | Field | Operator | Value |
|------------|-------|----------|-------|
| `status: 'active'` | status | eq (default) | 'active' |
| `age__gte: 18` | age | gte | 18 |
| `name__icontains: 'john'` | name | icontains | 'john' |

### JSONLogic Evaluation

```{mermaid}
flowchart TD
    J[JSONLogic Expression] --> R[Recursive Evaluator]
    R --> L{Logical Op?}
    L -->|and/or/not| C[Combine children]
    L -->|No| O{Comparison Op?}
    O -->|Yes| E[Evaluate operator]
    O -->|No| V[Get variable value]
    C --> Result
    E --> Result
    V --> Result
```

JSONLogic expressions are evaluated recursively:

1. **Logical operators** (`and`, `or`, `not`) combine child expressions
2. **Comparison operators** (`==`, `>`, `in`, etc.) compare values
3. **Variable references** (`{"var": "field"}`) extract field values

## SQL Generation

Filter expressions are converted to SQLAlchemy WHERE clauses:

```{mermaid}
flowchart LR
    subgraph "Filter to SQL"
        F["age__gte: 18"] --> B[Builder]
        B --> S["table.c.age >= 18"]
    end
```

### Example Transformations

| Filter | SQL |
|--------|-----|
| `{"status": "active"}` | `WHERE status = 'active'` |
| `{"age__gte": 18}` | `WHERE age >= 18` |
| `{"name__icontains": "john"}` | `WHERE LOWER(name) LIKE '%john%'` |
| `{"tags__in": ["a", "b"]}` | `WHERE tags IN ('a', 'b')` |

### Complex JSONLogic to SQL

```python
# JSONLogic
{
    "or": [
        {"==": [{"var": "status"}, "active"]},
        {"and": [
            {"==": [{"var": "role"}, "admin"]},
            {">=": [{"var": "level"}, 5]}
        ]}
    ]
}

# Generated SQL
# WHERE status = 'active' 
#    OR (role = 'admin' AND level >= 5)
```

## In-Memory Filtering

For in-memory data sources, expressions become Python predicates:

```{mermaid}
flowchart LR
    subgraph "Filter to Predicate"
        F["age__gte: 18"] --> B[Builder]
        B --> P["lambda item: item.age >= 18"]
    end
```

The same filter expression works for both SQL and in-memory:

```python
from pypaginate import FilterEngine

engine = FilterEngine()
filters = {"age__gte": 18, "status": "active"}

# SQL: Generates WHERE clause
sql_clause = engine.to_sql(filters, model=User)

# In-memory: Returns predicate function
predicate = engine.to_predicate(filters)
filtered = [item for item in items if predicate(item)]
```

## Field Access

The filter engine supports nested field access:

```{mermaid}
graph TB
    subgraph "Field Access Patterns"
        S["user.address.city"] --> N[Nested object access]
        A["tags[0]"] --> I[Array index access]
        J["metadata.key"] --> JA[JSON field access]
    end
```

### Access Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| `field` | Direct attribute | `status` |
| `field.nested` | Nested object | `address.city` |
| `field[0]` | Array index | `tags[0]` |
| `field.*.name` | Wildcard | `items.*.name` |

## Validation

Filter expressions are validated before execution:

```{mermaid}
flowchart TD
    F[Filter Expression] --> V1{Known fields?}
    V1 -->|No| E1[Error: Unknown field]
    V1 -->|Yes| V2{Valid operators?}
    V2 -->|No| E2[Error: Unknown operator]
    V2 -->|Yes| V3{Value types match?}
    V3 -->|No| E3[Error: Type mismatch]
    V3 -->|Yes| OK[Valid]
```

### Configuring Allowed Fields

```python
from pypaginate import FilterEngine

# Only allow specific fields
engine = FilterEngine(
    allowed_fields=["status", "age", "created_at"],
    strict=True  # Reject unknown fields
)
```

### Type Coercion

The engine can automatically coerce values:

| Field Type | Input | Coerced |
|------------|-------|---------|
| Integer | `"42"` | `42` |
| Date | `"2024-01-15"` | `date(2024, 1, 15)` |
| Boolean | `"true"` | `True` |
| UUID | `"550e8400-..."` | `UUID("550e8400-...")` |

## Performance Considerations

### Index Usage

Filter expressions should use indexed columns for best performance:

```{mermaid}
graph TB
    subgraph "Good: Uses Index"
        G1["status = 'active'"] --> GI[Index seek]
    end
    
    subgraph "Bad: Full Scan"
        B1["LOWER(name) LIKE '%john%'"] --> BS[Full table scan]
    end
```

### Optimization Tips

| Tip | Description |
|-----|-------------|
| Filter on indexed columns | Use primary keys, foreign keys, indexed fields |
| Avoid leading wildcards | `LIKE 'prefix%'` uses index, `LIKE '%suffix'` doesn't |
| Use equality before range | `status = 'active' AND age > 18` |
| Limit IN clause size | Large IN lists can be slow |

## Custom Operators

You can register custom operators:

```python
from pypaginate import FilterEngine, Operator

class FuzzyMatchOperator(Operator):
    name = "fuzzy"
    
    def apply(self, field_value: str, pattern: str) -> bool:
        # Custom fuzzy matching logic
        return fuzzy_match(field_value, pattern)
    
    def to_sql(self, column, pattern):
        # Custom SQL generation
        return func.similarity(column, pattern) > 0.3

engine = FilterEngine()
engine.registry.register(FuzzyMatchOperator())

# Now you can use: {"name__fuzzy": "john"}
```

## Error Handling

Filter errors are specific and actionable:

```python
from pypaginate.exceptions import FilterError, UnknownFieldError

try:
    result = engine.apply(data, filters)
except UnknownFieldError as e:
    print(f"Unknown field: {e.field}")
except FilterError as e:
    print(f"Filter error: {e}")
```

## Further Reading

- [User Guide: Filtering](../filtering/index.md) - Practical usage
- [User Guide: JSONLogic](../filtering/json-logic.md) - JSONLogic syntax
- [Operators Reference](../filtering/operators.md) - All operators
- [Architecture](architecture.md) - Overall library design
