# Cursor Encoding

Cursors in pypaginate are opaque strings that encode a position in a result set.
For SQL-backed cursor pagination, pypaginate delegates cursor encoding entirely to
[sqlakeyset](https://github.com/djrobstep/sqlakeyset).

---

## How Cursors Work

A cursor is a serialized "bookmark" that contains the sort-column values of the last
(or first) item on a page. When requesting the next page, the cursor is deserialized
and used to construct a WHERE clause that seeks directly to the correct position.

```{mermaid}
graph LR
    subgraph "Page 1"
        R1["items 1-20"]
        C1["next_cursor = serialize(last_item_values)"]
    end

    subgraph "Page 2 Request"
        D["deserialize(cursor)"]
        W["WHERE (cols) > (values)"]
        R2["items 21-40"]
    end

    C1 -->|"send cursor to client"| D
    D --> W
    W --> R2
```

---

## sqlakeyset Integration

pypaginate uses sqlakeyset for all cursor operations:

- **`sqlakeyset.select_page()`** -- executes a keyset-paginated query.
- **`sqlakeyset.serialize_bookmark()` / `unserialize_bookmark()`** -- encodes/decodes cursor strings.

The `SQLAlchemyCursorBackend` (async) and `SyncSQLAlchemyCursorBackend` (sync) wrap
these calls:

```python
from pypaginate.adapters.sqlalchemy.cursor import SQLAlchemyCursorBackend

backend = SQLAlchemyCursorBackend(session)

# fetch_page returns (items, next_cursor, prev_cursor)
items, next_cursor, prev_cursor = await backend.fetch_page(
    query,
    limit=20,
    after="eyJ2YWx1ZXMi...",  # cursor from previous page
)
```

Internally, `fetch_page` does:

1. Deserializes `after`/`before` strings into sqlakeyset bookmark objects via `unserialize_bookmark()`.
2. Calls `sqlakeyset.asyncio.select_page()` (or `sqlakeyset.select_page()` for sync).
3. Extracts items and bookmark strings from the returned `Page` object.

---

## Cursor Contents

A sqlakeyset cursor encodes the **sort-column values** of the boundary row. For a
query `ORDER BY created_at DESC, id ASC`, the cursor contains both values:

```
(created_at='2024-01-15T10:30:00', id=42)
    → serialized to opaque string: "eyJ2YWx1ZXMi..."
```

The cursor does NOT contain:

- Page numbers (those are an offset concept).
- Filter or search parameters (the client must resend those).
- Raw SQL (the cursor is data, not code).

---

## Multi-Column Sort

When sorting by multiple columns, the cursor must contain all sort-column values to
generate the correct compound WHERE clause:

```sql
-- Single column: simple comparison
WHERE id > 42

-- Multi-column: compound comparison (sqlakeyset handles this)
WHERE (created_at, id) > ('2024-01-15', 42)
```

:::{tip}
Always include a unique column (like `id`) as the last sort column. This guarantees
deterministic ordering even when other columns have duplicate values.
:::

---

## Bidirectional Navigation

sqlakeyset supports both forward (`after`) and backward (`before`) navigation.
Each `CursorPage` provides two cursors:

```python
page = await paginate(query, CursorParams(limit=20), backend=backend)

page.next_cursor       # str | None -- cursor for the next page
page.previous_cursor   # str | None -- cursor for the previous page
page.has_next          # True if next_cursor is not None
page.has_previous      # True if previous_cursor is not None
```

**Forward** (`after`): fetches items that come after the cursor position.
**Backward** (`before`): fetches items that come before the cursor position.

`after` and `before` are mutually exclusive on `CursorParams`.

---

## Security Considerations

Cursors contain actual column values from your database. If you sort by a sensitive
column (email, name), those values are embedded in the cursor string.

**Mitigations:**

- Sort by non-sensitive columns (`id`, `created_at`) when possible.
- Treat cursors as opaque on the client side.
- Invalid or tampered cursors cause sqlakeyset to raise an error -- pypaginate does not
  silently accept them.

---

## Best Practices

- Treat cursors as opaque strings -- never parse or construct them client-side.
- Include a unique tiebreaker column in your ORDER BY clause.
- Use consistent sort order across requests -- changing the sort invalidates existing cursors.
- Handle invalid cursors gracefully (catch the error, redirect to the first page).
- Do not assume cursor format stability across library versions.
