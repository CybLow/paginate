---
sidebar_position: 2
title: Django
---

# Django

Translate pypaginate specs into Django `Q` objects and `order_by` arguments, then
offset- or keyset-paginate a `QuerySet`. Django is imported **lazily** inside the
helpers, so importing the adapter module does not require Django — only calling a
helper does. Keyset cursors are byte-compatible with the other adapters; see
[cross-language parity](../concepts/parity).

## Install

```bash
pip install "pypaginate[django]"
```

This pulls in `Django>=4.2`. The native engine ships inside the `pypaginate`
wheel.

## Public API

```python
from pypaginate.adapters.django import (
    build_filter_q,    # FilterSpec list | FilterGroup -> Q
    apply_filters,     # queryset + filters -> filtered queryset
    build_order_by,    # SortSpec list -> order_by() args
    apply_sorting,     # queryset + sorting -> ordered queryset
    build_search_q,    # SearchSpec -> case-insensitive OR-of-fields Q (or None)
    apply_search,      # queryset + SearchSpec -> filtered queryset
    paginate_offset,   # queryset + OffsetParams -> OffsetPage
    paginate_keyset,   # queryset + CursorParams -> CursorPage
)
```

## Filtering

Each operator maps to a Django field lookup. `build_filter_q` accepts either a
flat `FilterSpec` list (each spec's `logic` selects AND/OR) or a nested `And` /
`Or` group; `apply_filters` calls `.filter()` for you (a no-op on an empty list).

```python
from pypaginate import FilterSpec, And
from pypaginate.adapters.django import apply_filters

qs = apply_filters(User.objects.all(), [
    FilterSpec(field="age", operator="gte", value=18),
    FilterSpec(field="status", operator="eq", value="active"),
])

qs = apply_filters(User.objects.all(), And(
    FilterSpec(field="age", operator="gte", value=18),
    FilterSpec(field="name", operator="contains", value="a"),
))
```

Operator notes specific to the SQL backend:

- `ne` / `not_in` render as a negated `Q` (`~Q(...)`).
- `like` maps to `__contains` and `ilike` to `__icontains` — SQL `LIKE`
  wildcards are **not** interpreted; the value is matched as a substring.
- `between` uses `__range`; `is_null` / `is_not_null` use `__isnull`.
- The in-memory-only operators `empty`, `not_empty`, and `exists` have no SQL
  equivalent and raise `FilterError`.

## Sorting

Without `nulls`, a key renders to a plain `"field"` / `"-field"` string; with
`nulls` set it renders to an `F(...).asc(nulls_last=...)` / `.desc(nulls_first=...)`
expression so Django emulates `NULLS FIRST/LAST` on backends lacking native
support.

```python
from pypaginate import SortSpec
from pypaginate.adapters.django import apply_sorting

qs = apply_sorting(User.objects.all(), [
    SortSpec(field="age", direction="desc"),
    SortSpec(field="name", direction="asc", nulls="last"),
])
```

## Search

`apply_search` keeps rows where *any* field matches the query via a
case-insensitive lookup per `spec.mode` (`contains` -> `__icontains`,
`prefix` -> `__istartswith`, `exact` -> `__iexact`). This is an unranked
match-filter — relevance ranking lives in the in-memory engine, not the database.

```python
from pypaginate import SearchSpec
from pypaginate.adapters.django import apply_search

qs = apply_search(User.objects.all(), SearchSpec(query="alice", fields=["name", "email"]))
```

## Offset pagination

`paginate_offset` counts via `QuerySet.count()` then slices
`qs[offset:offset + limit]`, which Django renders to `LIMIT`/`OFFSET`.

```python
from pypaginate import OffsetParams
from pypaginate.adapters.django import apply_filters, apply_sorting, paginate_offset

qs = apply_filters(User.objects.all(), [FilterSpec(field="age", operator="gte", value=18)])
qs = apply_sorting(qs, [SortSpec(field="age", direction="desc")])

page = paginate_offset(qs, OffsetParams(page=1, limit=20))
page.total      # int
page.pages      # int
list(page)      # the page's model instances
```

## Keyset (cursor) pagination

`paginate_keyset` reuses the cross-language cursor codec and the core's portable
keyset predicate, so cursors stay byte-compatible with the SQLAlchemy and TS
adapters. The QuerySet must carry an explicit `order_by` over **simple string
field names** (or a model `Meta.ordering`).

```python
from pypaginate import CursorParams
from pypaginate.adapters.django import paginate_keyset

qs = Post.objects.order_by("-created_at", "-id")

first = paginate_keyset(qs, CursorParams(limit=20))
nxt   = paginate_keyset(qs, CursorParams(limit=20, after=first.next_cursor))
prev  = paginate_keyset(qs, CursorParams(limit=20, before=nxt.previous_cursor))
```

The page exposes `next_cursor`, `previous_cursor`, `has_next`, and `has_previous`.
A non-string `order_by` entry (e.g. an `F` expression) raises `ConfigurationError`.
