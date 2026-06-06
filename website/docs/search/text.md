---
sidebar_position: 1
title: Text search
---

# Text search

`search(items, spec)` runs an in-memory full-text query and returns the matching
items in **ranked relevance order** (best match first). It is the search
counterpart to `filter` and `sort`, and like them it runs entirely inside the
native engine — Python and TypeScript return identical results, see
[cross-language parity](/concepts/parity).

The default mode is **token matching** (`fuzzy="exact"`): the query is split into
tokens and an item matches only when *every* token is found in one of the
searched fields. For typo-tolerant trigram scoring, see
[fuzzy search](./fuzzy.md).

## The `SearchSpec`

A search is described by a single spec. Python specs are dataclasses; TypeScript
specs are plain objects.

| Field | Type | Default | Meaning |
|-------|------|---------|---------|
| `query` | string | — | The raw query string. |
| `fields` | string[] | — | Field paths to search (dotted, e.g. `"profile.name"`). |
| `mode` | `"contains"` \| `"prefix"` \| `"exact"` | `"contains"` | How each token matches a field value. |
| `fuzzy` | `"exact"` \| `"fuzzy"` \| `"token_sort"` | `"exact"` | Scoring strategy — see [fuzzy search](./fuzzy.md). |
| `min_length` / `minLength` | int | `1` | Minimum query length (chars) before search runs. |
| `max_results` / `maxResults` | int | none | Optional cap on the number of ranked results. |
| `threshold` | int | `30` | Trigram threshold (fuzzy modes only). |
| `weights` | map | none | Per-field relevance multipliers — see [fuzzy search](./fuzzy.md). |

Only **string** fields participate; non-string and missing fields are skipped.

## Match modes

`mode` controls how a token is compared against a field value (matching is
case-insensitive — values and tokens are normalized first):

| Mode | A token matches when the value… |
|------|---------------------------------|
| `contains` (default) | contains the token as a substring |
| `prefix` | starts with the token |
| `exact` | equals the token |

## Python

```python
from pypaginate import search, SearchSpec

users = [
    {"name": "Alice Johnson", "email": "alice@example.com"},
    {"name": "Bob Alice",     "email": "bob@example.com"},
    {"name": "Carol Smith",   "email": "carol@work.io"},
]

# contains (default): every token must appear in some field
hits = search(users, SearchSpec(query="alice", fields=["name", "email"]))
# -> both Alice rows, ranked; Carol excluded

# prefix matching
starts = search(users, SearchSpec(
    query="ali",
    fields=["name"],
    mode="prefix",
))

# cap the number of results
top = search(users, SearchSpec(
    query="alice",
    fields=["name", "email"],
    max_results=1,
))
```

## TypeScript

```ts
import { search, type SearchSpec } from "@cyblow/paginate";

const users = [
  { name: "Alice Johnson", email: "alice@example.com" },
  { name: "Bob Alice",     email: "bob@example.com" },
  { name: "Carol Smith",   email: "carol@work.io" },
];

// contains (default): every token must appear in some field
const hits = search(users, { query: "alice", fields: ["name", "email"] });

// prefix matching
const starts = search(users, { query: "ali", fields: ["name"], mode: "prefix" });

// cap the number of results (camelCase in TS)
const top = search(users, {
  query: "alice",
  fields: ["name", "email"],
  maxResults: 1,
});
```

> Identical results in both languages — see [cross-language parity](/concepts/parity).

## How ranking works (token mode)

1. The query is tokenized, honoring quoted phrases: `'"john doe" admin'` →
   `["john doe", "admin"]`. (Unbalanced quotes fall back to a plain whitespace
   split.)
2. For each item, **every** token must match at least one field by `mode`. A
   token that matches no field disqualifies the whole item.
3. Each matched token contributes `100` to the item's score (scaled by the
   field's [weight](./fuzzy.md), default `1.0`), summed across tokens.
4. Items are ordered by score **descending**; ties keep their original input
   order (the sort is stable). `max_results` then truncates the list.

More query tokens that match means a higher score, so multi-token matches rank
above partial ones.

## Short queries and `min_length`

A query whose trimmed length is shorter than `min_length` characters — or that
tokenizes to nothing (empty / whitespace-only) — short-circuits and returns
**every item in original order**, unmodified. Raise `min_length` to suppress
searching until the user has typed enough:

```python
search(users, SearchSpec(query="a", fields=["name"], min_length=2))
# query too short -> returns all users in original order
```

```ts
search(users, { query: "a", fields: ["name"], minLength: 2 });
// query too short -> returns all users in original order
```

## Next

- [Fuzzy search](./fuzzy.md) — typo-tolerant trigram scoring, `threshold`, and
  per-field `weights`.
