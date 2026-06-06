//! A resident trigram inverted index for the fuzzy/token-sort search paths.
//!
//! Building the index once amortizes across the many queries a resident
//! [`crate::value::Value`] dataset answers: an item with no trigram in common
//! with the query has similarity 0, so the candidate set (the union of the query
//! trigrams' posting lists) is an *exact* prefilter — it contains every item
//! that could clear any threshold.

use std::collections::HashMap;

use crate::accessor::compile_path;
use crate::error::Result;
use crate::normalize::{normalize_text, normalize_text_cow};
use crate::value::Value;

use super::trigram::{self, Trigram};
use super::{rank, trigram_score, FuzzyMode, SearchSpec};

/// A trigram → item-ids inverted index over **all** string content of each item.
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
    pub(super) fn candidates(&self, query: &[Trigram]) -> Vec<u32> {
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
        Value::Str(s) => out.extend(trigram::trigrams(&normalize_text_cow(s))),
        Value::Map(map) => map.values().for_each(|v| collect_string_trigrams(v, out)),
        Value::List(items) => items.iter().for_each(|v| collect_string_trigrams(v, out)),
        _ => {}
    }
}

/// Like [`super::search_indices`], but for the fuzzy/token-sort modes it scores
/// only the `index` candidates (exact — see [`TrigramIndex`]) instead of every
/// item. Exact mode is unaffected (it does not use trigrams) and falls back to a
/// full scan.
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
        return Ok(super::exact_search(items, &paths, spec));
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
