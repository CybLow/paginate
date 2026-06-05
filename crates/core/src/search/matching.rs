//! Exact field matching on pre-normalized strings (the `Exact` search mode).
//!
//! Fuzzy/token-sort scoring is no longer edit-distance based — it lives in
//! [`super::trigram`] (n-gram similarity, the pg_trgm model).

use super::SearchFieldMode;

/// Exact / prefix / contains match on pre-normalized strings.
pub(crate) fn matches_field(norm_value: &str, norm_token: &str, mode: SearchFieldMode) -> bool {
    match mode {
        SearchFieldMode::Exact => norm_value == norm_token,
        SearchFieldMode::Prefix => norm_value.starts_with(norm_token),
        SearchFieldMode::Contains => norm_value.contains(norm_token),
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
}
