---
sidebar_position: 5
title: Search
---

# Search

`search(items, spec)` runs an in-memory full-text query and returns matching items in
**ranked relevance order** (best match first). The default mode is token matching
(`fuzzy="exact"`). For the ranking algorithm, trigram metrics, and weights, see the
[shared reference](../general/search).

## Token search

By default the query is split into tokens and an item matches only when *every* token
is found in one of the searched fields:

```python
from pypaginate import search, SearchSpec

users = [
    {"name": "Alice Johnson", "email": "alice@example.com"},
    {"name": "Bob Alice",     "email": "bob@example.com"},
    {"name": "Carol Smith",   "email": "carol@work.io"},
]

hits = search(users, SearchSpec(query="alice", fields=["name", "email"]))
# -> both Alice rows, ranked; Carol excluded
```

### Match mode and result cap

```python
# prefix matching
search(users, SearchSpec(query="ali", fields=["name"], mode="prefix"))

# cap the number of ranked results
search(users, SearchSpec(query="alice", fields=["name", "email"], max_results=1))
```

`mode` is `"contains"` (default), `"prefix"`, or `"exact"`.

## Fuzzy (typo-tolerant) search

Set `fuzzy` to `"fuzzy"` or `"token_sort"` for trigram scoring, which tolerates typos
and partial matches:

```python
products = [
    {"title": "Apple iPhone 15 Pro Max"},
    {"title": "Samsung Galaxy S24"},
    {"title": "Apple iPad Air"},
]

# "iphon" still matches "iPhone"
search(products, SearchSpec(
    query="iphon",
    fields=["title"],
    fuzzy="fuzzy",
    threshold=30,
))
```

`token_sort` is word-order agnostic — `"johnson alice"` matches `"Alice Johnson"`.
`threshold` (default `30`, range `0–100`) is the minimum trigram similarity for a field
to count.

## Per-field weights

`weights` is a `dict[str, float]` of relevance multipliers (default `1.0`). A field's
score is multiplied by its weight before ranking, so you can rank a title hit above a
body hit:

```python
docs = [
    {"title": "Postgres tuning", "body": "general database notes"},
    {"title": "General notes",   "body": "postgres tuning deep dive"},
]

search(docs, SearchSpec(
    query="postgres tuning",
    fields=["title", "body"],
    fuzzy="fuzzy",
    weights={"title": 3.0, "body": 1.0},
))
# -> the title hit ranks first
```

## Short queries

A query shorter than `min_length` (default `1`) — or empty/whitespace — returns **all
items in original order**, unmodified. Raise it to defer searching until the user types
enough:

```python
search(users, SearchSpec(query="a", fields=["name"], min_length=2))
# -> all users, original order
```

## Next

- [Search & ranking reference](../general/search) — modes, trigram metrics, weights.
- [Filtering](./filtering) · [Sorting](./sorting) · [Pagination](./pagination)
