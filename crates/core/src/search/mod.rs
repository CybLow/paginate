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

mod matching;
mod parser;
mod trigram;

use std::collections::{BTreeMap, HashMap};

use crate::accessor::{compile_path, resolve_opt};
use crate::coerce;
use crate::error::Result;
use crate::normalize::normalize_text;
use crate::value::Value;
use matching::matches_field;
use trigram::Trigram;

/// How a token matches a field value.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SearchFieldMode {
    Prefix,
    Contains,
    Exact,
}

/// Fuzzy matching strategy.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FuzzyMode {
    Exact,
    Fuzzy,
    TokenSort,
}

/// A search specification.
#[derive(Debug, Clone)]
pub struct SearchSpec {
    /// Raw query string.
    pub query: String,
    /// Fields to search (dotted paths).
    pub fields: Vec<String>,
    /// Optional per-field weights (default weight is 1.0).
    pub weights: Option<BTreeMap<String, f64>>,
    /// Exact/prefix/contains matching mode.
    pub mode: SearchFieldMode,
    /// Fuzzy strategy (Exact disables trigram scoring).
    pub fuzzy: FuzzyMode,
    /// Minimum trigram similarity (0-100) for a field to count as a match.
    pub threshold: i64,
    /// Minimum query length (in chars) before searching kicks in.
    pub min_length: usize,
    /// Optional cap on the number of ranked results.
    pub max_results: Option<usize>,
}

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
/// threshold). `query` is the precomputed query trigram set.
pub(crate) fn trigram_score(
    item: &Value,
    paths: &[Vec<String>],
    query: &[Trigram],
    spec: &SearchSpec,
) -> i64 {
    let mut best = 0;
    for (field_index, path) in paths.iter().enumerate() {
        let Some(Value::Str(raw)) = resolve_opt(item, path) else {
            continue;
        };
        let value = trigram::trigrams(&normalize_text(raw));
        let score = trigram_metric(query, &value, spec.fuzzy);
        if score >= spec.threshold {
            best = best.max((score as f64 * weight_for(spec, field_index)) as i64);
        }
    }
    best
}

// -- inverted index (resident Dataset: build once, query many) ----------------

/// A trigram → item-ids inverted index over **all** string content of each item.
///
/// It powers an *exact* candidate prefilter for fuzzy/token-sort search: an item
/// with no trigram in common with the query has similarity 0, so it can never
/// clear the threshold — meaning the candidate set (the union of the query
/// trigrams' posting lists) contains every item that could match. Building it
/// once amortizes across the many queries a resident [`crate::value::Value`]
/// dataset answers.
pub struct TrigramIndex {
    /// Trigram → ascending item indices that contain it (in any string field).
    postings: HashMap<Trigram, Vec<u32>>,
}

impl TrigramIndex {
    /// Build the index over every string reachable in each item.
    #[must_use]
    pub fn build(items: &[Value]) -> Self {
        let mut postings: HashMap<Trigram, Vec<u32>> = HashMap::new();
        let mut buf: Vec<Trigram> = Vec::new();
        for (index, item) in items.iter().enumerate() {
            buf.clear();
            collect_string_trigrams(item, &mut buf);
            buf.sort_unstable();
            buf.dedup();
            for tg in &buf {
                postings.entry(*tg).or_default().push(index as u32);
            }
        }
        Self { postings }
    }

    /// Ascending, de-duplicated item indices sharing at least one query trigram.
    fn candidates(&self, query: &[Trigram]) -> Vec<u32> {
        let mut out: Vec<u32> = Vec::new();
        for tg in query {
            if let Some(list) = self.postings.get(tg) {
                out.extend_from_slice(list);
            }
        }
        out.sort_unstable();
        out.dedup();
        out
    }
}

/// Accumulate the trigrams of every (normalized) string reachable in `value`.
fn collect_string_trigrams(value: &Value, out: &mut Vec<Trigram>) {
    match value {
        Value::Str(s) => out.extend(trigram::trigrams(&normalize_text(s))),
        Value::Map(map) => map.values().for_each(|v| collect_string_trigrams(v, out)),
        Value::List(items) => items.iter().for_each(|v| collect_string_trigrams(v, out)),
        _ => {}
    }
}

/// Like [`search_indices`], but for the fuzzy/token-sort modes it scores only the
/// `index` candidates (exact — see [`TrigramIndex`]) instead of every item. Exact
/// mode is unaffected (it does not use trigrams) and falls back to a full scan.
///
/// # Errors
/// [`crate::CoreError::Filter`] if a field path segment starts with `_`.
pub fn search_with_index(
    items: &[Value],
    spec: &SearchSpec,
    index: &TrigramIndex,
) -> Result<Vec<usize>> {
    if spec.query.trim().chars().count() < spec.min_length {
        return Ok((0..items.len()).collect());
    }
    let paths: Vec<Vec<String>> = spec
        .fields
        .iter()
        .map(|f| compile_path(f))
        .collect::<Result<_>>()?;
    if spec.fuzzy == FuzzyMode::Exact {
        return Ok(exact_search(items, &paths, spec));
    }
    let query = trigram::trigrams(&normalize_text(&spec.query));
    if query.is_empty() {
        return Ok((0..items.len()).collect());
    }
    let mut scored: Vec<(i64, usize)> = Vec::new();
    for candidate in index.candidates(&query) {
        let index = candidate as usize;
        let score = trigram_score(&items[index], &paths, &query, spec);
        if score > 0 {
            scored.push((score, index));
        }
    }
    Ok(rank(scored, spec.max_results))
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

/// Match-filter search (pypaginate's `MemorySearchBackend` semantics): keep items
/// where **any** field matches the whole `query`, in original order (unranked).
/// `Exact` matches by `mode`; `Fuzzy`/`TokenSort` match when the trigram
/// similarity meets `threshold`. An empty normalized query returns every item.
///
/// # Errors
/// [`crate::CoreError::Filter`] if a field path segment starts with `_`.
pub fn match_indices(
    items: &[Value],
    query: &str,
    fields: &[String],
    mode: SearchFieldMode,
    fuzzy: FuzzyMode,
    threshold: i64,
) -> Result<Vec<usize>> {
    let normalized = normalize_text(query);
    if normalized.is_empty() {
        return Ok((0..items.len()).collect());
    }
    let paths = compile_paths(fields)?;
    let mq = MatchQuery::new(&normalized, mode, fuzzy, threshold);
    Ok((0..items.len())
        .filter(|&i| mq.hits(&items[i], &paths))
        .collect())
}

/// Like [`match_indices`], but for the fuzzy/token-sort modes it tests only the
/// `index` candidates (exact — see [`TrigramIndex`]). Candidates come back in
/// ascending order, so matched items stay in original order. Exact mode is a
/// full scan (substring matching is not trigram-prunable).
///
/// # Errors
/// [`crate::CoreError::Filter`] if a field path segment starts with `_`.
pub fn match_indices_with_index(
    items: &[Value],
    query: &str,
    fields: &[String],
    mode: SearchFieldMode,
    fuzzy: FuzzyMode,
    threshold: i64,
    index: &TrigramIndex,
) -> Result<Vec<usize>> {
    let normalized = normalize_text(query);
    if normalized.is_empty() {
        return Ok((0..items.len()).collect());
    }
    let paths = compile_paths(fields)?;
    let mq = MatchQuery::new(&normalized, mode, fuzzy, threshold);
    if fuzzy == FuzzyMode::Exact {
        return Ok((0..items.len())
            .filter(|&i| mq.hits(&items[i], &paths))
            .collect());
    }
    Ok(index
        .candidates(&mq.trigrams)
        .into_iter()
        .map(|c| c as usize)
        .filter(|&i| mq.hits(&items[i], &paths))
        .collect())
}

/// A prepared match-filter query (the per-item predicate, shared by the scanning
/// and index-backed [`match_indices`] variants).
struct MatchQuery {
    normalized: String,
    trigrams: Vec<Trigram>,
    mode: SearchFieldMode,
    fuzzy: FuzzyMode,
    threshold: i64,
}

impl MatchQuery {
    fn new(normalized: &str, mode: SearchFieldMode, fuzzy: FuzzyMode, threshold: i64) -> Self {
        let trigrams = if fuzzy == FuzzyMode::Exact {
            Vec::new()
        } else {
            trigram::trigrams(normalized)
        };
        Self {
            normalized: normalized.to_owned(),
            trigrams,
            mode,
            fuzzy,
            threshold,
        }
    }

    /// True if **any** of `item`'s fields matches this query.
    fn hits(&self, item: &Value, paths: &[Vec<String>]) -> bool {
        paths.iter().any(|path| {
            resolve_opt(item, path).is_some_and(|value| {
                let norm = normalize_value(value);
                if self.fuzzy == FuzzyMode::Exact {
                    matches_field(&norm, &self.normalized, self.mode)
                } else {
                    trigram_metric(&self.trigrams, &trigram::trigrams(&norm), self.fuzzy)
                        >= self.threshold
                }
            })
        })
    }
}

/// Compile the search field paths.
fn compile_paths(fields: &[String]) -> Result<Vec<Vec<String>>> {
    fields.iter().map(|f| compile_path(f)).collect()
}

/// Normalize a value's string form (mirrors `normalize_text(str(v))`).
fn normalize_value(value: &Value) -> String {
    match value {
        Value::Str(s) => normalize_text(s),
        other => normalize_text(&coerce::to_py_str(other)),
    }
}

#[cfg(test)]
mod tests;
