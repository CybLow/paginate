//! Full-text in-memory search with ranking, ported from pypaginate's `search/`.
//!
//! All tokens must match (AND) for an item to score; the score is the summed
//! per-token contribution (100 per exact/prefix/contains hit, or the fuzzy
//! score), weighted per field in multi-field mode. Results are ranked by score
//! descending with ties kept in original order (stable).
//!
//! [`search_indices`] returns ranked indices so the binding can select the
//! original host objects without cloning them through the core. A query shorter
//! than `min_length`, or one that tokenizes to nothing, returns every item in
//! original order (unfiltered) — matching the Python engine.

mod matching;
mod parser;

use std::collections::BTreeMap;

use crate::accessor::{compile_path, resolve_opt};
use crate::coerce;
use crate::error::Result;
use crate::normalize::normalize_text;
use crate::value::Value;
use matching::{fuzzy_score, matches_field};

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
    /// Fuzzy strategy (Exact disables fuzzy scoring).
    pub fuzzy: FuzzyMode,
    /// Minimum fuzzy score (0-100) to count as a match.
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
    let norm_tokens: Vec<String> = if spec.fuzzy == FuzzyMode::TokenSort {
        vec![normalize_text(&spec.query)]
    } else {
        let tokens = parser::tokenize(&spec.query);
        if tokens.is_empty() {
            return Ok((0..items.len()).collect());
        }
        tokens.iter().map(|t| normalize_text(t)).collect()
    };
    let paths: Vec<Vec<String>> = spec
        .fields
        .iter()
        .map(|f| compile_path(f))
        .collect::<Result<_>>()?;
    let is_fuzzy = spec.fuzzy != FuzzyMode::Exact;

    let mut scored: Vec<(i64, usize)> = Vec::new();
    for (index, item) in items.iter().enumerate() {
        let score = if paths.len() == 1 {
            score_single(item, &norm_tokens, &paths[0], is_fuzzy, spec)
        } else {
            score_multi(item, &norm_tokens, &paths, spec, is_fuzzy)
        };
        if score > 0 {
            scored.push((score, index));
        }
    }
    // Rank by score descending; stable so ties keep original order.
    scored.sort_by_key(|entry| std::cmp::Reverse(entry.0));
    let mut result: Vec<usize> = scored.into_iter().map(|(_, index)| index).collect();
    if let Some(max) = spec.max_results {
        result.truncate(max);
    }
    Ok(result)
}

/// Convenience wrapper around [`search_indices`] that clones ranked items.
///
/// # Errors
/// See [`search_indices`].
pub fn apply(items: &[Value], spec: &SearchSpec) -> Result<Vec<Value>> {
    let ranked = search_indices(items, spec)?;
    Ok(ranked.into_iter().map(|i| items[i].clone()).collect())
}

fn score_single(
    item: &Value,
    norm_tokens: &[String],
    path: &[String],
    is_fuzzy: bool,
    spec: &SearchSpec,
) -> i64 {
    let Some(Value::Str(raw)) = resolve_opt(item, path) else {
        return 0;
    };
    let value = normalize_text(raw);
    let mut total = 0;
    for token in norm_tokens {
        if is_fuzzy {
            let score = fuzzy_score(&value, token, spec.threshold, spec.fuzzy);
            if score == 0 {
                return 0;
            }
            total += score;
        } else if matches_field(&value, token, spec.mode) {
            total += 100;
        } else {
            return 0;
        }
    }
    total
}

fn score_multi(
    item: &Value,
    norm_tokens: &[String],
    paths: &[Vec<String>],
    spec: &SearchSpec,
    is_fuzzy: bool,
) -> i64 {
    let pairs = extract(item, paths);
    if pairs.is_empty() {
        return 0;
    }
    let mut total = 0;
    for token in norm_tokens {
        let best = best_weighted(&pairs, token, spec, is_fuzzy);
        if best == 0 {
            return 0;
        }
        total += best;
    }
    total
}

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

fn best_weighted(
    pairs: &[(usize, String)],
    norm_token: &str,
    spec: &SearchSpec,
    is_fuzzy: bool,
) -> i64 {
    let mut best = 0;
    for (field_index, value) in pairs {
        let weight = weight_for(spec, *field_index);
        if is_fuzzy {
            let raw = fuzzy_score(value, norm_token, spec.threshold, spec.fuzzy);
            best = best.max((raw as f64 * weight) as i64);
        } else if matches_field(value, norm_token, spec.mode) {
            // Exact-mode parity: first matching field wins (not the max).
            return (100.0 * weight) as i64;
        }
    }
    best
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

/// Match-filter search (pypaginate's `MemorySearchBackend` semantics): normalize
/// the **whole** query, then keep items where **any** field contains / prefixes
/// / equals it, in original order (unranked, non-fuzzy). An empty normalized
/// query returns every item.
///
/// # Errors
/// [`crate::CoreError::Filter`] if a field path segment starts with `_`.
pub fn match_indices(
    items: &[Value],
    query: &str,
    fields: &[String],
    mode: SearchFieldMode,
) -> Result<Vec<usize>> {
    let normalized_query = normalize_text(query);
    if normalized_query.is_empty() {
        return Ok((0..items.len()).collect());
    }
    let paths: Vec<Vec<String>> = fields
        .iter()
        .map(|f| compile_path(f))
        .collect::<Result<_>>()?;
    let mut matched = Vec::new();
    for (index, item) in items.iter().enumerate() {
        for path in &paths {
            if let Some(value) = resolve_opt(item, path) {
                if matches_field(&normalize_value(value), &normalized_query, mode) {
                    matched.push(index);
                    break;
                }
            }
        }
    }
    Ok(matched)
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
