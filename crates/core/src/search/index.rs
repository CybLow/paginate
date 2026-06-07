//! A resident trigram inverted index for the fuzzy/token-sort search paths.
//!
//! Building the index once amortizes across the many queries a resident
//! [`crate::value::Value`] dataset answers: an item with no trigram in common
//! with the query has similarity 0, so the candidate set (the union of the query
//! trigrams' posting lists) is a sound prefilter — it contains every item that
//! could clear any threshold, and is then rescored only against the spec's
//! declared `fields`. The index covers **all** string content of each item, so
//! the candidate set is a *superset* of the items that match in the searched
//! fields (never a miss); the per-field rescoring in [`search_with_index`]
//! produces the final, exact result.

use std::collections::HashMap;
use std::sync::{Arc, Mutex};

use crate::accessor::compile_path;
use crate::error::Result;
use crate::normalize::{normalize_text, normalize_text_cow};
use crate::value::Value;

use super::trigram::{self, Trigram};
use super::{rank, score_item, FuzzyMode, SearchSpec};

/// A trigram → item-ids inverted index over **all** string content of each item.
pub struct TrigramIndex {
    /// Trigram → ascending item indices that contain it (in any string field).
    postings: HashMap<Trigram, Vec<u32>>,
    /// Item count — the candidate bitset's width.
    len: usize,
    /// Lazy per-field trigram cache: a top-level field name → its normalized
    /// trigram set for every item, built on first search of the field and reused
    /// across queries. This is the resident model's payoff: repeat queries skip
    /// re-trigramming the corpus (profiling showed ~50% of search time was the
    /// per-row `trigrams()` + its sort). Behind a `Mutex` so the index stays
    /// `Sync` for the frozen PyO3 / napi datasets.
    field_cache: Mutex<HashMap<String, Arc<Vec<Vec<Trigram>>>>>,
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
        Self {
            postings,
            len: items.len(),
            field_cache: Mutex::new(HashMap::new()),
        }
    }

    /// The per-item trigram set for a top-level string `field`, built once and
    /// cached (items lacking it, or non-string, get an empty set → score 0).
    fn field_trigrams(&self, items: &[Value], field: &str) -> Arc<Vec<Vec<Trigram>>> {
        let mut cache = self.field_cache.lock().expect("field cache poisoned");
        if let Some(cached) = cache.get(field) {
            return Arc::clone(cached);
        }
        let built: Vec<Vec<Trigram>> = items
            .iter()
            .map(|item| match item {
                Value::Map(map) => match map.get(field) {
                    Some(Value::Str(s)) => trigram::trigrams(&normalize_text_cow(s)),
                    _ => Vec::new(),
                },
                _ => Vec::new(),
            })
            .collect();
        let arc = Arc::new(built);
        cache.insert(field.to_owned(), Arc::clone(&arc));
        arc
    }

    /// Ascending, de-duplicated item indices sharing at least one query trigram.
    ///
    /// Union-via-bitset: mark each posting in a `len`-wide bool vector, then scan
    /// it once. `O(m + n)` (m = total postings, n = items) with no sort — the
    /// posting union can be several times `n`, so this beats concatenate-then-
    /// `sort_unstable` (`O(m log m)`), which profiling showed dominated search
    /// once corpus re-trigramming was cached. The scan yields ascending order, so
    /// score-tie ordering (and results) are unchanged.
    pub(super) fn candidates(&self, query: &[Trigram]) -> Vec<u32> {
        let mut seen = vec![false; self.len];
        let mut count = 0usize;
        for tg in query {
            if let Some(list) = self.postings.get(tg) {
                for &i in list {
                    let slot = &mut seen[i as usize];
                    if !*slot {
                        *slot = true;
                        count += 1;
                    }
                }
            }
        }
        let mut out = Vec::with_capacity(count);
        for (i, &hit) in seen.iter().enumerate() {
            if hit {
                out.push(i as u32);
            }
        }
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
    // Fetch (build once, then reuse) each top-level field's trigram cache; nested
    // paths fall back to per-item re-trigramming inside `score_item`.
    let caches: Vec<Option<Arc<Vec<Vec<Trigram>>>>> = paths
        .iter()
        .map(|path| (path.len() == 1).then(|| index.field_trigrams(items, &path[0])))
        .collect();
    let mut scored: Vec<(i64, usize)> = Vec::new();
    for candidate in index.candidates(&query) {
        let i = candidate as usize;
        let score = score_item(items, i, &paths, &caches, &query, spec);
        if score > 0 {
            scored.push((score, i));
        }
    }
    Ok(rank(scored, spec.max_results))
}
