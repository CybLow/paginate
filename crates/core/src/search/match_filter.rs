//! Match-filter search (pypaginate's `MemorySearchBackend` semantics): keep the
//! items where **any** field matches the whole query, in original order
//! (unranked). This is the search *stage* of the pipeline — a filter, not a
//! re-rank — so it composes with explicit filters and sorting.

use std::collections::HashSet;

use crate::accessor::{compile_path, resolve_opt};
use crate::coerce;
use crate::error::Result;
use crate::normalize::normalize_text;
use crate::value::Value;

use super::matching::matches_field;
use super::trigram::{self, Trigram};
use super::{trigram_metric, FuzzyMode, SearchFieldMode, TrigramIndex};

/// Keep items where **any** field matches the whole `query`, in original order
/// (unranked). `Exact` matches by `mode`; `Fuzzy`/`TokenSort` match when the
/// trigram similarity meets `threshold`. An empty normalized query returns every
/// item.
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

/// Match-filter an already-narrowed, ascending index subset (`candidates`, e.g.
/// the pipeline's filter-stage output) to those matching the whole `query` —
/// the search stage of [`crate::pipeline::offset_page_searched`]. Preserves the
/// candidates' order. An empty normalized query keeps them all; for fuzzy modes
/// a supplied `index` prunes the per-item predicate to trigram candidates.
///
/// # Errors
/// [`crate::CoreError::Filter`] if a field path segment starts with `_`.
#[allow(clippy::too_many_arguments)]
pub fn retain_matching(
    items: &[Value],
    candidates: &[usize],
    query: &str,
    fields: &[String],
    mode: SearchFieldMode,
    fuzzy: FuzzyMode,
    threshold: i64,
    index: Option<&TrigramIndex>,
) -> Result<Vec<usize>> {
    let normalized = normalize_text(query);
    if normalized.is_empty() {
        return Ok(candidates.to_vec());
    }
    let paths = compile_paths(fields)?;
    let mq = MatchQuery::new(&normalized, mode, fuzzy, threshold);
    if fuzzy != FuzzyMode::Exact {
        if let Some(idx) = index {
            let allowed: HashSet<u32> = idx.candidates(&mq.trigrams).into_iter().collect();
            return Ok(candidates
                .iter()
                .copied()
                .filter(|&i| allowed.contains(&(i as u32)) && mq.hits(&items[i], &paths))
                .collect());
        }
    }
    Ok(candidates
        .iter()
        .copied()
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
