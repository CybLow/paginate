---
sidebar_position: 2
title: Fuzzy search
---

# Fuzzy search

[Text search](./text.md) defaults to token matching (`fuzzy="exact"`), which
needs each token to appear verbatim. Setting `fuzzy` to `"fuzzy"` or
`"token_sort"` switches to **trigram scoring**, which tolerates typos,
transpositions, and partial matches — and like everything else in the engine it
returns identical results in Python and TypeScript, see
[cross-language parity](/concepts/parity).

## Trigram scoring

Each string is broken into overlapping 3-character grams (the PostgreSQL
`pg_trgm` model). `"cat"` becomes `{"  c", " ca", "cat", "at "}`. The query's
trigram set is scored against each field's set, producing a `0-100` similarity.

| `fuzzy` | Metric | Behavior |
|---------|--------|----------|
| `"exact"` (default) | — | Token matching only (no trigrams). See [text search](./text.md). |
| `"fuzzy"` | Containment | Fraction of the *query's* trigrams found in the field. A short query fully inside a long value still scores high. |
| `"token_sort"` | Jaccard | Symmetric and word-order agnostic: `"alice johnson"` and `"johnson alice"` score `100`. |

The metrics, where `Q` and `T` are the query and field trigram sets:

- **Containment** = `intersection(Q, T) / size(Q)` — not diluted by how long the
  field is, so a short query inside a long title still scores high (backs
  `"fuzzy"`).
- **Jaccard** = `intersection(Q, T) / union(Q, T)` — symmetric and set-based, so
  it is naturally word-order agnostic (backs `"token_sort"`).

A field counts as a match only when its similarity is **≥ `threshold`** (default
`30`, range `0-100`). An item's score is the **best** (highest weighted) score
among its fields; items with no qualifying field are dropped. Results are ranked
by score descending, ties stable in original order.

## `threshold`

`threshold` is the minimum trigram similarity for a field to count. Lower it to
catch looser matches, raise it to demand closer ones:

```python
from pypaginate import search, SearchSpec

products = [
    {"title": "Apple iPhone 15 Pro Max"},
    {"title": "Samsung Galaxy S24"},
    {"title": "Apple iPad Air"},
]

# typo-tolerant: "iphon" still matches "iPhone"
hits = search(products, SearchSpec(
    query="iphon",
    fields=["title"],
    fuzzy="fuzzy",
    threshold=30,
))
```

```ts
import { search } from "@cyblow/paginate";

const products = [
  { title: "Apple iPhone 15 Pro Max" },
  { title: "Samsung Galaxy S24" },
  { title: "Apple iPad Air" },
];

// typo-tolerant: "iphon" still matches "iPhone"
const hits = search(products, {
  query: "iphon",
  fields: ["title"],
  fuzzy: "fuzzy",
  threshold: 30,
});
```

### Word-order-insensitive matching

Use `token_sort` when the query words may be in any order — it scores on the set
of trigrams, so word order does not matter:

```python
search(people, SearchSpec(
    query="johnson alice",
    fields=["name"],          # matches "Alice Johnson"
    fuzzy="token_sort",
))
```

```ts
search(people, {
  query: "johnson alice",
  fields: ["name"],           // matches "Alice Johnson"
  fuzzy: "token_sort",
});
```

> Identical results in both languages — see [cross-language parity](/concepts/parity).

## Per-field weights

`weights` is a map from field name to a relevance multiplier (default `1.0` for
any field not listed). A field's score is multiplied by its weight before
ranking, so weights let you bias which field "wins" a match — for example,
ranking a title hit above a description hit.

The map keys are the exact field strings you put in `fields`. In Python it is a
`dict[str, float]`; in TypeScript a `Record<string, number>`.

```python
from pypaginate import search, SearchSpec

docs = [
    {"title": "Postgres tuning", "body": "general database notes"},
    {"title": "General notes",   "body": "postgres tuning deep dive"},
]

# A title match counts triple; a body match counts as written.
ranked = search(docs, SearchSpec(
    query="postgres tuning",
    fields=["title", "body"],
    fuzzy="fuzzy",
    weights={"title": 3.0, "body": 1.0},
))
# -> the title hit ranks first, even though both contain the phrase
```

```ts
import { search } from "@cyblow/paginate";

const docs = [
  { title: "Postgres tuning", body: "general database notes" },
  { title: "General notes",   body: "postgres tuning deep dive" },
];

// A title match counts triple; a body match counts as written.
const ranked = search(docs, {
  query: "postgres tuning",
  fields: ["title", "body"],
  fuzzy: "fuzzy",
  weights: { title: 3.0, body: 1.0 },
});
// -> the title hit ranks first, even though both contain the phrase
```

### How weights combine with each mode

- **Token mode** (`fuzzy="exact"`): each matched token contributes
  `100 × weight`, using the weight of the first field that matched the token.
- **Fuzzy modes** (`"fuzzy"` / `"token_sort"`): each field's `0-100` similarity
  is multiplied by its weight, and the item takes its single best weighted
  field. A weight above `1.0` boosts that field's ranking; below `1.0` demotes
  it.

Weights only re-rank items that already match (they never make a below-threshold
field qualify). Combine them with `threshold`, `min_length`, and `max_results`
from [text search](./text.md) to shape the result list.
