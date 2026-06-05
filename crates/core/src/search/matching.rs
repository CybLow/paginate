//! Field matching and fuzzy scoring on pre-normalized strings, ported from
//! pypaginate's `search/matching.py`.
//!
//! Fuzzy scoring mirrors Python's rapidfuzz:
//! * `FuzzyMode::Fuzzy` → `partial_ratio`: the best alignment of the shorter
//!   string within the longer (a substring window of the shorter's length).
//! * `FuzzyMode::TokenSort` → `token_sort_ratio`: whitespace-split, sort, and
//!   rejoin tokens on both sides, then `ratio` (word-order agnostic).
//!
//! Both build on the rapidfuzz crate's normalized-Indel [`fuzz::ratio`], which
//! returns `0.0..=1.0`; we scale to the 0-100 integer scores pypaginate uses
//! (`int(...)`-style truncation) and gate by `threshold`.

use rapidfuzz::fuzz;

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
    fuzzy_mode: FuzzyMode,
) -> i64 {
    let score = match fuzzy_mode {
        FuzzyMode::TokenSort => token_sort_ratio(norm_value, norm_token),
        _ => partial_ratio(norm_value, norm_token),
    };
    if score >= threshold {
        score
    } else {
        0
    }
}

/// rapidfuzz normalized-Indel `ratio` scaled to a truncated 0-100 integer
/// (matching pypaginate's `int(fuzz.ratio(...))`).
fn ratio(a: &str, b: &str) -> i64 {
    if a.is_empty() && b.is_empty() {
        return 100;
    }
    (fuzz::ratio(a.chars(), b.chars()) * 100.0) as i64
}

/// Partial-ratio over pre-collected `char` slices with an early-exit cutoff.
///
/// `cutoff` (0.0..=1.0) lets rapidfuzz abandon a window's edit-distance DP as
/// soon as it cannot reach the score — the common case for the non-matching
/// bulk of a dataset. Below-cutoff windows contribute nothing, so the result is
/// the best **at-or-above-cutoff** windowed ratio (truncated 0-100), else 0.
/// Callers gate by the same threshold, so this is identical to taking the max
/// over all windows and gating afterwards — just far less work.
pub(crate) fn partial_ratio_chars(value: &[char], token: &[char], cutoff: f64) -> i64 {
    let (short, long) = if value.len() <= token.len() {
        (value, token)
    } else {
        (token, value)
    };
    if short.is_empty() {
        return i64::from(long.is_empty()) * 100;
    }
    let args = fuzz::Args::default().score_cutoff(cutoff);
    let mut best = 0;
    for window in long.windows(short.len()) {
        let scored = fuzz::ratio_with_args(short.iter().copied(), window.iter().copied(), &args);
        if let Some(s) = scored {
            let scaled = (s * 100.0) as i64;
            if scaled > best {
                best = scaled;
                if best == 100 {
                    break;
                }
            }
        }
    }
    best
}

/// Best `ratio` of the shorter string aligned within the longer — a substring
/// window of the shorter's length — matching `fuzz.partial_ratio`'s intent.
/// String form for the match-filter path; `cutoff = 0.0` computes every window
/// (the true max), so it is the single source for [`partial_ratio_chars`].
fn partial_ratio(a: &str, b: &str) -> i64 {
    let a_chars: Vec<char> = a.chars().collect();
    let b_chars: Vec<char> = b.chars().collect();
    partial_ratio_chars(&a_chars, &b_chars, 0.0)
}

/// `ratio` after whitespace-splitting, sorting, and rejoining tokens on both
/// sides (word-order agnostic), matching `fuzz.token_sort_ratio`.
fn token_sort_ratio(a: &str, b: &str) -> i64 {
    ratio(&sorted_tokens(a), &sorted_tokens(b))
}

fn sorted_tokens(s: &str) -> String {
    let mut tokens: Vec<&str> = s.split_whitespace().collect();
    tokens.sort_unstable();
    tokens.join(" ")
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
        // exact substring alignment -> 100; dissimilar -> below threshold -> 0.
        assert_eq!(fuzzy_score("hello", "ell", 75, FuzzyMode::Fuzzy), 100);
        assert_eq!(fuzzy_score("hello", "xyz", 75, FuzzyMode::Fuzzy), 0);
    }

    #[test]
    fn partial_ratio_finds_substring() {
        assert_eq!(partial_ratio("alice johnson", "alice"), 100);
        assert_eq!(partial_ratio("alice", "alice johnson"), 100);
    }

    #[test]
    fn token_sort_is_word_order_agnostic() {
        assert_eq!(token_sort_ratio("johnson alice", "alice johnson"), 100);
        assert_eq!(
            fuzzy_score("johnson alice", "alice johnson", 90, FuzzyMode::TokenSort),
            100
        );
    }

    #[test]
    fn dissimilar_scores_below_threshold() {
        assert_eq!(fuzzy_score("zebra", "alice", 75, FuzzyMode::Fuzzy), 0);
    }
}
