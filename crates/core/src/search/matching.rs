//! Field matching and fuzzy scoring on pre-normalized strings, ported from
//! pypaginate's `search/matching.py`.
//!
//! Fuzzy scoring currently mirrors pypaginate's behaviour **when rapidfuzz is
//! not installed**: substring containment scores 100, otherwise 0 (gated by the
//! threshold). Wiring the `rapidfuzz` crate for `partial_ratio` /
//! `token_sort_ratio` score parity with the installed-rapidfuzz path is a
//! tracked follow-up.

use super::{FuzzyMode, SearchFieldMode};

/// Exact / prefix / contains match on pre-normalized strings.
pub(crate) fn matches_field(norm_value: &str, norm_token: &str, mode: SearchFieldMode) -> bool {
    match mode {
        SearchFieldMode::Exact => norm_value == norm_token,
        SearchFieldMode::Prefix => norm_value.starts_with(norm_token),
        SearchFieldMode::Contains => norm_value.contains(norm_token),
    }
}

/// Fuzzy score (0-100) on pre-normalized strings, gated by `threshold`.
pub(crate) fn fuzzy_score(
    norm_value: &str,
    norm_token: &str,
    threshold: i64,
    _fuzzy_mode: FuzzyMode,
) -> i64 {
    let score = if norm_value.contains(norm_token) {
        100
    } else {
        0
    };
    if score >= threshold {
        score
    } else {
        0
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn modes() {
        assert!(matches_field("hello", "hello", SearchFieldMode::Exact));
        assert!(!matches_field(
            "hello world",
            "hello",
            SearchFieldMode::Exact
        ));
        assert!(matches_field("hello", "hel", SearchFieldMode::Prefix));
        assert!(matches_field("hello", "ell", SearchFieldMode::Contains));
        assert!(!matches_field("hello", "xyz", SearchFieldMode::Contains));
    }

    #[test]
    fn fuzzy_threshold_gate() {
        assert_eq!(fuzzy_score("hello", "ell", 75, FuzzyMode::Fuzzy), 100);
        assert_eq!(fuzzy_score("hello", "xyz", 75, FuzzyMode::Fuzzy), 0);
    }
}
