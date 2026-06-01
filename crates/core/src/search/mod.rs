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

#[cfg(test)]
mod tests {
    use super::*;

    fn item(pairs: &[(&str, &str)]) -> Value {
        let mut map = BTreeMap::new();
        for (key, value) in pairs {
            map.insert((*key).to_owned(), Value::Str((*value).to_owned()));
        }
        Value::Map(map)
    }

    fn spec(query: &str, fields: &[&str]) -> SearchSpec {
        SearchSpec {
            query: query.to_owned(),
            fields: fields.iter().map(|s| (*s).to_owned()).collect(),
            weights: None,
            mode: SearchFieldMode::Contains,
            fuzzy: FuzzyMode::Exact,
            threshold: 75,
            min_length: 1,
            max_results: None,
        }
    }

    #[test]
    fn single_field_contains_and_ranks() {
        let items = vec![
            item(&[("name", "Alice")]),
            item(&[("name", "Bob")]),
            item(&[("name", "Alicia")]),
        ];
        let idx = search_indices(&items, &spec("ali", &["name"])).unwrap();
        // Both Alice and Alicia contain "ali"; equal score keeps original order.
        assert_eq!(idx, vec![0, 2]);
    }

    #[test]
    fn all_tokens_must_match() {
        let items = vec![
            item(&[("bio", "rust developer")]),
            item(&[("bio", "rust enthusiast")]),
        ];
        let idx = search_indices(&items, &spec("rust developer", &["bio"])).unwrap();
        assert_eq!(idx, vec![0]);
    }

    #[test]
    fn short_query_returns_all() {
        let items = vec![item(&[("name", "Alice")]), item(&[("name", "Bob")])];
        let mut s = spec("ab", &["name"]);
        s.min_length = 3;
        let idx = search_indices(&items, &s).unwrap();
        assert_eq!(idx, vec![0, 1]);
    }

    #[test]
    fn weighted_multi_field_ranks_by_weight() {
        let items = vec![
            item(&[("name", "zeta"), ("bio", "alpha")]),
            item(&[("name", "alpha"), ("bio", "zeta")]),
        ];
        let mut s = spec("alpha", &["name", "bio"]);
        s.weights = Some(BTreeMap::from([("name".to_owned(), 3.0)]));
        let idx = search_indices(&items, &s).unwrap();
        // Item 1 matches "alpha" in the weighted `name` field -> ranks first.
        assert_eq!(idx, vec![1, 0]);
    }

    #[test]
    fn max_results_caps_output() {
        let items = vec![
            item(&[("name", "aaa")]),
            item(&[("name", "aab")]),
            item(&[("name", "aac")]),
        ];
        let mut s = spec("aa", &["name"]);
        s.max_results = Some(2);
        let idx = search_indices(&items, &s).unwrap();
        assert_eq!(idx.len(), 2);
    }

    #[test]
    fn exact_mode_requires_full_value() {
        let items = vec![item(&[("tag", "rust")]), item(&[("tag", "rustacean")])];
        let mut s = spec("rust", &["tag"]);
        s.mode = SearchFieldMode::Exact;
        let idx = search_indices(&items, &s).unwrap();
        assert_eq!(idx, vec![0]);
    }
}
