# Pagination Strategies

pypaginate supports two fundamentally different pagination strategies: **offset-based** and
**keyset-based** (also called cursor-based). Understanding the differences is crucial for
choosing the right approach for your application.

## The Two Strategies

```{mermaid}
graph LR
    subgraph "Offset Pagination"
        O1[Page 1<br/>OFFSET 0] --> O2[Page 2<br/>OFFSET 10]
        O2 --> O3[Page 3<br/>OFFSET 20]
        O3 --> O4[Page 4<br/>OFFSET 30]
    end
```

```{mermaid}
graph LR
    subgraph "Keyset Pagination"
        K1[First Page<br/>No cursor] --> K2[Next Page<br/>after: id=10]
        K2 --> K3[Next Page<br/>after: id=20]
        K3 --> K4[Next Page<br/>after: id=30]
    end
```

## Offset Pagination

Offset pagination uses `LIMIT` and `OFFSET` clauses to skip a number of rows and return
a fixed page size.

### How It Works

```sql
-- Page 1: Get first 10 items
SELECT * FROM items ORDER BY id LIMIT 10 OFFSET 0;

-- Page 2: Skip 10, get next 10
SELECT * FROM items ORDER BY id LIMIT 10 OFFSET 10;

-- Page 3: Skip 20, get next 10
SELECT * FROM items ORDER BY id LIMIT 10 OFFSET 20;
```

### Advantages

| Advantage | Description |
|-----------|-------------|
| **Simple mental model** | "Page 5 of 10" is intuitive for users |
| **Random access** | Can jump directly to any page |
| **Exact total count** | Can show "Showing 41-50 of 347 results" |
| **Familiar UI patterns** | Works with traditional page number navigation |

### Disadvantages

| Disadvantage | Description |
|--------------|-------------|
| **Performance degrades** | Database must scan and discard OFFSET rows |
| **Inconsistent results** | Insertions/deletions cause items to shift between pages |
| **Memory pressure** | Large offsets require scanning many rows |

### Performance Characteristics

```{mermaid}
graph TB
    subgraph "Offset Performance"
        direction LR
        P1["Page 1<br/>⚡ Fast"] --> P10["Page 10<br/>🔶 Slower"]
        P10 --> P100["Page 100<br/>🔴 Much Slower"]
        P100 --> P1000["Page 1000<br/>💀 Very Slow"]
    end
```

The database must:

1. Execute the full query
2. Sort all matching rows
3. Skip OFFSET rows (reading but discarding)
4. Return LIMIT rows

For page 1000 with 10 items per page, the database scans 10,000 rows to return 10.

### When to Use Offset

✅ **Good for:**

- Small to medium datasets (< 10,000 rows)
- Admin interfaces with page number navigation
- Reports where users need random page access
- Situations where exact counts matter

❌ **Avoid for:**

- Large datasets (> 100,000 rows)
- Real-time data with frequent insertions
- Infinite scroll interfaces
- Mobile apps with limited bandwidth

## Keyset Pagination

Keyset pagination (also called cursor pagination or seek pagination) uses a "cursor" that
points to a specific row, then fetches rows after (or before) that position.

### How It Works

```sql
-- First page: No cursor
SELECT * FROM items ORDER BY id LIMIT 10;
-- Returns ids 1-10, cursor points to id=10

-- Next page: Use cursor
SELECT * FROM items WHERE id > 10 ORDER BY id LIMIT 10;
-- Returns ids 11-20, cursor points to id=20

-- Next page: Use new cursor
SELECT * FROM items WHERE id > 20 ORDER BY id LIMIT 10;
-- Returns ids 21-30, cursor points to id=30
```

### Advantages

| Advantage | Description |
|-----------|-------------|
| **Consistent performance** | Same speed for any "page" |
| **Stable results** | Insertions don't cause duplicates or gaps |
| **Index-friendly** | Uses efficient index seeks |
| **Lower memory** | No need to scan skipped rows |

### Disadvantages

| Disadvantage | Description |
|--------------|-------------|
| **No random access** | Can't jump to "page 50" directly |
| **No exact total count** | Can only say "has more" or estimate |
| **More complex cursors** | Multi-column sorts need compound cursors |
| **Forward/backward only** | Sequential navigation |

### Performance Characteristics

```{mermaid}
graph TB
    subgraph "Keyset Performance"
        direction LR
        K1["First batch<br/>⚡ Fast"] --> K10["10th batch<br/>⚡ Fast"]
        K10 --> K100["100th batch<br/>⚡ Fast"]
        K100 --> K1000["1000th batch<br/>⚡ Still Fast!"]
    end
```

With proper indexing, every "page" has the same performance because:

1. The WHERE clause uses an index seek (not scan)
2. Only LIMIT rows are read
3. No rows are skipped

### When to Use Keyset

✅ **Good for:**

- Large datasets (any size)
- Infinite scroll interfaces
- Real-time data with frequent changes
- APIs with high-volume clients
- Mobile apps (predictable performance)

❌ **Avoid for:**

- UIs requiring page numbers
- Reports needing random page access
- Situations where exact counts are required

## Side-by-Side Comparison

```{mermaid}
graph TB
    subgraph "Offset: Page 1000"
        direction TB
        OQ[Query] --> OS[Scan 10,000 rows]
        OS --> OD[Discard 9,990]
        OD --> OR[Return 10]
    end
    
    subgraph "Keyset: 1000th batch"
        direction TB
        KQ[Query] --> KS[Index seek to cursor]
        KS --> KR[Return 10]
    end
```

| Aspect | Offset | Keyset |
|--------|--------|--------|
| **Query complexity** | Simple | Moderate |
| **Performance at depth** | O(offset) | O(1) |
| **Random access** | ✅ Yes | ❌ No |
| **Consistent results** | ❌ Items can shift | ✅ Stable |
| **Total count** | ✅ Exact | ⚠️ Estimate only |
| **Index requirements** | Basic | Must cover sort columns |
| **Implementation** | Trivial | Requires cursor encoding |

## Multi-Column Sorting

Keyset pagination becomes more complex with multiple sort columns:

```{mermaid}
graph TD
    subgraph "Single Column Sort"
        S1["ORDER BY id"] --> S2["Cursor: id > 10"]
    end
    
    subgraph "Multi-Column Sort"
        M1["ORDER BY created_at, id"] --> M2["Cursor: created_at > X<br/>OR (created_at = X AND id > Y)"]
    end
```

pypaginate handles this automatically:

```python
# Single column - simple cursor
params = KeysetPageParams(size=10, sort=["id"])

# Multi-column - compound cursor handled automatically
params = KeysetPageParams(size=10, sort=["created_at", "id"])
```

:::{tip} Always include a unique column
When using keyset pagination with non-unique columns (like `created_at`),
always include a unique column (like `id`) as a tiebreaker to ensure
deterministic ordering.
:::

## Choosing a Strategy

```{mermaid}
flowchart TD
    Start([Need Pagination?]) --> Size{Dataset Size?}
    
    Size -->|"< 10K rows"| Random{Need random<br/>page access?}
    Size -->|"> 10K rows"| Keyset[Use Keyset]
    
    Random -->|Yes| Offset[Use Offset]
    Random -->|No| UI{UI Pattern?}
    
    UI -->|Page numbers| Offset
    UI -->|Infinite scroll| Keyset
    UI -->|Load more| Keyset
    
    Offset --> Done([Done])
    Keyset --> Done
```

### Decision Matrix

| Your Situation | Recommendation |
|----------------|----------------|
| Building an admin panel | Offset (users expect page numbers) |
| Building a social feed | Keyset (infinite scroll, real-time) |
| API for mobile app | Keyset (predictable performance) |
| Report with exports | Offset (need exact counts) |
| E-commerce product list | Keyset (large catalogs) |
| Search results | Either (depends on result size) |
| Dashboard tables | Offset (small, filtered datasets) |

## Implementation in pypaginate

::::{tab-set}

:::{tab-item} Offset Pagination
```python
from pypaginate import paginate, PageParams

# Create offset parameters
params = PageParams(page=1, size=20)

# Paginate
page = await paginate(query, params)

# Access results
print(f"Page {page.page} of {page.total_pages}")
print(f"Showing {len(page.items)} of {page.total} items")
```
:::

:::{tab-item} Keyset Pagination
```python
from pypaginate import paginate, KeysetPageParams

# First page - no cursor
params = KeysetPageParams(size=20)
page = await paginate(query, params)

# Next page - use cursor from previous response
if page.next_cursor:
    params = KeysetPageParams(size=20, after=page.next_cursor)
    next_page = await paginate(query, params)
```
:::

::::

## Further Reading

- [Cursor Encoding](cursor-encoding.md) - How cursors are encoded and decoded
- [User Guide: Offset Pagination](../pagination/offset.md) - Practical usage
- [User Guide: Keyset Pagination](../pagination/keyset.md) - Practical usage
- [Architecture](architecture.md) - How pagination engines work internally
