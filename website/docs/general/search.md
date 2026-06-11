---
sidebar_position: 9
title: Search & ranking
---

# Search & ranking

Search runs an in-memory full-text query and returns matching items in **ranked
relevance order** (best match first). It runs entirely in the native engine, so Python
and TypeScript return identical results. This page is the canonical reference; for
runnable code see the [Python](../python/search) and [TypeScript](../typescript/search)
search guides.

## The `SearchSpec`

| Field | Type | Default | Meaning |
|---|---|---|---|
| `query` | string | — | The raw query string. |
| `fields` | string[] | — | Field paths to search (dotted, e.g. `"profile.name"`). |
| `mode` | `"contains"` \| `"prefix"` \| `"exact"` | `"contains"` | How each token matches a field value. |
| `fuzzy` | `"exact"` \| `"fuzzy"` \| `"token_sort"` | `"exact"` | Scoring strategy (see [fuzzy](#fuzzy-trigram-scoring)). |
| `min_length` | int | `1` | Minimum query length before search runs. |
| `max_results` | int | none | Optional cap on the number of ranked results. |
| `threshold` | int | `30` | Trigram similarity threshold, `0–100` (fuzzy modes only). |
| `weights` | map | none | Per-field relevance multipliers (default `1.0`). |

Only **string** fields participate; non-string and missing fields are skipped. (In
TypeScript the count/length fields are `minLength` / `maxResults`.)

## Match modes (token matching)

The default `fuzzy="exact"` mode does **token matching**: the query is split into
tokens and an item matches only when *every* token is found in one of the searched
fields. `mode` controls how a token is compared against a field value (matching is
case-insensitive — values and tokens are normalized first):

| Mode | A token matches when the value… |
|---|---|
| `contains` (default) | contains the token as a substring |
| `prefix` | starts with the token |
| `exact` | equals the token |

### How token ranking works

1. The query is tokenized, honoring quoted phrases: `'"john doe" admin'` →
   `["john doe", "admin"]`. (Unbalanced quotes fall back to a whitespace split.)
2. For each item, **every** token must match at least one field by `mode`. A token
   that matches no field disqualifies the whole item.
3. Each matched token contributes `100` to the item's score (scaled by the matching
   field's [weight](#per-field-weights)), summed across tokens.
4. Items are ordered by score **descending**; ties keep their original input order
   (the sort is stable). `max_results` then truncates the list.

More matching tokens means a higher score, so multi-token matches rank above partial
ones.

## Fuzzy (trigram) scoring

Setting `fuzzy` to `"fuzzy"` or `"token_sort"` switches to **trigram scoring**, which
tolerates typos, transpositions, and partial matches. Each string is broken into
overlapping 3-character grams (the PostgreSQL `pg_trgm` model): `"cat"` becomes
`{"  c", " ca", "cat", "at "}`. The query's trigram set is scored against each field's
set, producing a `0–100` similarity.

| `fuzzy` | Metric | Behavior |
|---|---|---|
| `"exact"` (default) | — | Token matching only (no trigrams). |
| `"fuzzy"` | Containment = `size(Q ∩ T) / size(Q)` | Fraction of the *query's* trigrams found in the field — not diluted by field length, so a short query inside a long value still scores high. |
| `"token_sort"` | Jaccard = `size(Q ∩ T) / size(Q ∪ T)` | Symmetric and set-based, so it is word-order agnostic: `"alice johnson"` and `"johnson alice"` score `100`. |

A field counts as a match only when its similarity is **≥ `threshold`** (default `30`).
An item's score is the **best** (highest weighted) score among its fields; items with
no qualifying field are dropped. Results are ranked by score descending, ties stable.

## Per-field weights

`weights` maps a field name to a relevance multiplier (default `1.0` for any field not
listed). A field's score is multiplied by its weight before ranking, so weights bias
which field "wins" a match — e.g. ranking a title hit above a description hit.

- **Token mode** (`fuzzy="exact"`): each matched token contributes `100 × weight`,
  using the weight of the first field that matched the token.
- **Fuzzy modes**: each field's `0–100` similarity is multiplied by its weight, and the
  item takes its single best weighted field.

Weights only re-rank items that already match — they never make a below-threshold
field qualify.

## Short queries

A query shorter than `min_length` characters — or that tokenizes to nothing (empty /
whitespace-only) — short-circuits and returns **every item in original order**,
unmodified. Raise `min_length` to suppress searching until the user has typed enough.

## Next

- [Python search](../python/search) · [TypeScript search](../typescript/search)
- [Filtering & operators](./filtering) · [Sorting semantics](./sorting)
