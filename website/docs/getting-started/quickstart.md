---
sidebar_position: 2
---

# Quickstart

Paginate, filter, sort, and search an in-memory collection. Both packages return the
same results — see [cross-language parity](../concepts/parity).

## Python

```python
from pypaginate import (
    paginate, filter, sort, search,
    OffsetParams, FilterSpec, SortSpec, SearchSpec, And,
)

users = [...]  # any list of dicts or objects

page = paginate(users, OffsetParams(page=1, limit=20))
page.total      # int
page.has_next   # bool
list(page)      # the page's items (OffsetPage is iterable + indexable)

adults = filter(users, FilterSpec(field="age", operator="gte", value=18))
grouped = filter(users, And(
    FilterSpec(field="age", operator="gte", value=18),
    FilterSpec(field="name", operator="contains", value="a"),
))
newest = sort(users, SortSpec(field="created_at", direction="desc"))
hits   = search(users, SearchSpec(query="alice", fields=["name", "email"]))
```

For repeated queries over the same data, marshal once with a `Dataset`:

```python
from pypaginate import Dataset

ds = Dataset(users)
page = ds.page(OffsetParams(page=1, limit=20),
               filters=[FilterSpec(field="age", operator="gte", value=18)],
               sorting=[SortSpec(field="age", direction="desc")])
```

## TypeScript

```ts
import { paginate, filter, sort, search, And, OffsetParams } from "@cyblow/paginate";

const page = paginate(users, new OffsetParams({ page: 1, limit: 20 }));
page.total;     // number
page.hasNext;   // boolean

const adults = filter(users, { field: "age", operator: "gte", value: 18 });
const grouped = filter(users, And(
  { field: "age", operator: "gte", value: 18 },
  { field: "name", operator: "contains", value: "a" },
));
const hits = search(users, { query: "alice", fields: ["name", "email"] });
```
