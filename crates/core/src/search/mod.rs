//! Full-text in-memory search with ranking, ported from pypaginate's `search/`.
//!
//! Two regimes, chosen by [`FuzzyMode`]:
//!
//! * **Exact** — tokenize the query; an item scores when **every** token matches
//!   some field by `mode` (contains / prefix / equals), summing 100 per token.
//! * **Fuzzy / TokenSort** — score the whole query's trigram set against each
//!   field's (see [`trigram`]): `Fuzzy` uses containment (query-in-target),
//!   `TokenSort` uses Jaccard (word-order agnostic). A field counts when its
//!   0-100 similarity meets `threshold`; the item takes its best weighted field.
//!
//! Results are ranked by score descending, ties kept in original order (stable).
//! [`search_indices`] returns ranked indices so the binding selects the host's
//! own objects. A query shorter than `min_length`, or one that tokenizes to
//! nothing, returns every item in original order.
//!
//! The two alternative query paths live in sibling modules: [`index`] adds a
//! resident trigram inverted index (build once, query many) and [`match_filter`]
//! provides the unranked match-filter used by the pipeline's search stage.

mod index;
mod match_filter;
mod matching;
mod parser;
mod spec;
mod trigram;

use std::sync::Arc;

use crate::accessor::{compile_path, resolve_opt};
use crate::error::Result;
use crate::normalize::{normalize_text, normalize_text_cow};
use crate::value::Value;

use matching::matches_field;
use trigram::Trigram;

pub use index::{search_with_index, TrigramIndex};
pub use match_filter::{match_indices, retain_matching};
pub use spec::{FuzzyMode, SearchFieldMode, SearchSpec};

/// Return item indices ranked by relevance to `spec`.
///
/// # Errors
/// [`crate::CoreError::Filter`] if a field path segment starts with `_`.
pub fn search_indices(items: &[Value], spec: &SearchSpec) -> Result<Vec<usize>> {
    if spec.query.trim().chars().count() < spec.min_length {
        return Ok((0..items.len()).collect());
    }
    let paths: Vec<Vec<String>> = spec
        .fields
        .iter()
        .map(|f| compile_path(f))
        .collect::<Result<_>>()?;
    if spec.fuzzy == FuzzyMode::Exact {
        Ok(exact_search(items, &paths, spec))
    } else {
        Ok(trigram_search(items, &paths, spec))
    }
}

/// Convenience wrapper around [`search_indices`] that clones ranked items.
///
/// # Errors
/// See [`search_indices`].
pub fn apply(items: &[Value], spec: &SearchSpec) -> Result<Vec<Value>> {
    let ranked = search_indices(items, spec)?;
    Ok(ranked.into_iter().map(|i| items[i].clone()).collect())
}

/// Sort scored `(score, index)` pairs by score desc (stable) into ranked indices.
fn rank(mut scored: Vec<(i64, usize)>, max_results: Option<usize>) -> Vec<usize> {
    scored.sort_by_key(|entry| std::cmp::Reverse(entry.0));
    let mut result: Vec<usize> = scored.into_iter().map(|(_, index)| index).collect();
    if let Some(max) = max_results {
        result.truncate(max);
    }
    result
}

// -- Exact mode (tokenized match-filter, all tokens must match) ---------------

fn exact_search(items: &[Value], paths: &[Vec<String>], spec: &SearchSpec) -> Vec<usize> {
    let tokens = parser::tokenize(&spec.query);
    if tokens.is_empty() {
        return (0..items.len()).collect();
    }
    let norm_tokens: Vec<String> = tokens.iter().map(|t| normalize_text(t)).collect();
    let mut scored: Vec<(i64, usize)> = Vec::new();
    for (index, item) in items.iter().enumerate() {
        let score = exact_score(item, paths, &norm_tokens, spec);
        if score > 0 {
            scored.push((score, index));
        }
    }
    rank(scored, spec.max_results)
}

/// Every token must match some field; the first matching field's weighted 100
/// wins for that token, summed across tokens. (`MemorySearchBackend` semantics.)
fn exact_score(item: &Value, paths: &[Vec<String>], tokens: &[String], spec: &SearchSpec) -> i64 {
    let pairs = extract(item, paths);
    if pairs.is_empty() {
        return 0;
    }
    let mut total = 0;
    for token in tokens {
        let mut hit = 0;
        for (field_index, value) in &pairs {
            if matches_field(value, token, spec.mode) {
                hit = (100.0 * weight_for(spec, *field_index)) as i64;
                break;
            }
        }
        if hit == 0 {
            return 0;
        }
        total += hit;
    }
    total
}

// -- Fuzzy / TokenSort mode (whole-query trigram scoring) ---------------------

fn trigram_search(items: &[Value], paths: &[Vec<String>], spec: &SearchSpec) -> Vec<usize> {
    let query = trigram::trigrams(&normalize_text(&spec.query));
    if query.is_empty() {
        return (0..items.len()).collect();
    }
    let mut scored: Vec<(i64, usize)> = Vec::new();
    for (index, item) in items.iter().enumerate() {
        let score = trigram_score(item, paths, &query, spec);
        if score > 0 {
            scored.push((score, index));
        }
    }
    rank(scored, spec.max_results)
}

/// One field's trigram similarity to the query: containment for `Fuzzy`, Jaccard
/// for `TokenSort`.
fn trigram_metric(query: &[Trigram], value: &[Trigram], fuzzy: FuzzyMode) -> i64 {
    match fuzzy {
        FuzzyMode::TokenSort => trigram::similarity(query, value),
        _ => trigram::containment(query, value),
    }
}

/// Best weighted trigram score over `item`'s fields (0 if no field meets the
/// threshold). `query` is the precomputed query trigram set. Used by the
/// stateless full scan, which has no resident cache to reuse.
fn trigram_score(item: &Value, paths: &[Vec<String>], query: &[Trigram], spec: &SearchSpec) -> i64 {
    let mut best = 0;
    for (field_index, path) in paths.iter().enumerate() {
        let Some(Value::Str(raw)) = resolve_opt(item, path) else {
            continue;
        };
        let value = trigram::trigrams(&normalize_text_cow(raw));
        let score = trigram_metric(query, &value, spec.fuzzy);
        if score >= spec.threshold {
            best = best.max((score as f64 * weight_for(spec, field_index)) as i64);
        }
    }
    best
}

/// Score item `i` against the query for the resident index path, reusing a
/// prebuilt per-field trigram set where present (top-level fields), else
/// re-trigramming a nested field. Produces the identical score to
/// [`trigram_score`] — the cache stores exactly `trigrams(normalize(field))`.
pub(super) fn score_item(
    items: &[Value],
    i: usize,
    paths: &[Vec<String>],
    caches: &[Option<Arc<Vec<Vec<Trigram>>>>],
    query: &[Trigram],
    spec: &SearchSpec,
) -> i64 {
    let mut best = 0;
    for (field_index, path) in paths.iter().enumerate() {
        let score = match &caches[field_index] {
            Some(cache) => trigram_metric(query, &cache[i], spec.fuzzy),
            None => match resolve_opt(&items[i], path) {
                Some(Value::Str(raw)) => trigram_metric(
                    query,
                    &trigram::trigrams(&normalize_text_cow(raw)),
                    spec.fuzzy,
                ),
                _ => 0,
            },
        };
        if score >= spec.threshold {
            best = best.max((score as f64 * weight_for(spec, field_index)) as i64);
        }
    }
    best
}

// -- shared helpers -----------------------------------------------------------

/// Extract `(field_index, normalized_value)` for each string field present.
fn extract(item: &Value, paths: &[Vec<String>]) -> Vec<(usize, String)> {
    let mut pairs = Vec::with_capacity(paths.len());
    for (field_index, path) in paths.iter().enumerate() {
        if let Some(Value::Str(raw)) = resolve_opt(item, path) {
            pairs.push((field_index, normalize_text(raw)));
        }
    }
    pairs
}

fn weight_for(spec: &SearchSpec, field_index: usize) -> f64 {
    match &spec.weights {
        Some(weights) => weights
            .get(&spec.fields[field_index])
            .copied()
            .unwrap_or(1.0),
        None => 1.0,
    }
}

#[cfg(test)]
mod tests;
