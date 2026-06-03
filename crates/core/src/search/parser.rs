//! Quote-aware query tokenizer, ported from pypaginate's `search/parser.py`.
//!
//! Python uses `shlex.split`, falling back to a plain whitespace split when the
//! quotes are unbalanced (`except ValueError`). The `shlex` crate mirrors POSIX
//! shell word-splitting and returns `None` on a parse error, which we map to the
//! same whitespace fallback.

/// Split a query into tokens, honouring quoted phrases.
#[must_use]
pub(crate) fn tokenize(query: &str) -> Vec<String> {
    let stripped = query.trim();
    if stripped.is_empty() {
        return Vec::new();
    }
    match shlex::split(stripped) {
        Some(tokens) => tokens.into_iter().filter(|t| !t.is_empty()).collect(),
        None => stripped.split_whitespace().map(str::to_owned).collect(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn quoted_phrases_stay_together() {
        assert_eq!(tokenize(r#""john doe" admin"#), vec!["john doe", "admin"]);
    }

    #[test]
    fn whitespace_collapses() {
        assert_eq!(tokenize("  hello   world  "), vec!["hello", "world"]);
    }

    #[test]
    fn empty_query_has_no_tokens() {
        assert!(tokenize("   ").is_empty());
    }

    #[test]
    fn unbalanced_quotes_fall_back_to_whitespace() {
        // shlex rejects the dangling quote; fallback splits on whitespace.
        assert_eq!(tokenize(r#"foo "bar"#), vec!["foo", r#""bar"#]);
    }
}
