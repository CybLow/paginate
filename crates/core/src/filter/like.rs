//! SQL `LIKE` / `ILIKE` matching, ported from pypaginate's `filtering/like.py`.
//!
//! Patterns are classified once into a fast string-method path (`%x%`, `x%`,
//! `%x`) or a token glob for everything else (interior `%`, or `_`).
//!
//! Only the SQL wildcards `%` (any run) and `_` (single character) are special;
//! every other character — including `*`, `?`, and `[` — matches **literally**.
//! (Python's `fnmatch` treats `*`/`?`/`[` as wildcards; mirroring SQL `LIKE`
//! here, where they are ordinary text, is deliberate.)

use std::borrow::Cow;

/// A LIKE pattern compiled once for repeated matching.
pub struct LikeMatcher {
    kind: Kind,
    case_insensitive: bool,
}

enum Kind {
    Contains(String),
    StartsWith(String),
    EndsWith(String),
    Glob(Vec<GlobToken>),
}

/// One unit of a compiled glob: a wildcard or a single literal character.
#[derive(Clone, Copy)]
enum GlobToken {
    /// `%` — matches any run of characters (including empty).
    Star,
    /// `_` — matches exactly one character.
    AnyOne,
    /// Any other character, matched literally (case-folded when insensitive).
    Lit(char),
}

impl LikeMatcher {
    /// Compile a SQL LIKE pattern. When `case_insensitive`, the fast-path
    /// literals are lowercased now and the field is lowercased at match time;
    /// the glob path folds per character so a length-changing fold (e.g. `İ`)
    /// can't desync `_`'s single-character semantics.
    #[must_use]
    pub fn compile(pattern: &str, case_insensitive: bool) -> Self {
        Self {
            kind: classify(pattern, case_insensitive),
            case_insensitive,
        }
    }

    /// Test whether `field` matches the pattern.
    #[must_use]
    pub fn matches(&self, field: &str) -> bool {
        match &self.kind {
            Kind::Contains(inner) => self.casefold(field).contains(inner.as_str()),
            Kind::StartsWith(inner) => self.casefold(field).starts_with(inner.as_str()),
            Kind::EndsWith(inner) => self.casefold(field).ends_with(inner.as_str()),
            Kind::Glob(glob) => glob_match(field, glob, self.case_insensitive),
        }
    }

    /// Lowercase the field for the fast paths only when matching insensitively.
    fn casefold<'a>(&self, field: &'a str) -> Cow<'a, str> {
        if self.case_insensitive {
            Cow::Owned(field.to_lowercase())
        } else {
            Cow::Borrowed(field)
        }
    }
}

fn classify(pattern: &str, ci: bool) -> Kind {
    let lower = |s: &str| if ci { s.to_lowercase() } else { s.to_owned() };
    if pattern.contains('_') {
        return Kind::Glob(glob_tokens(pattern));
    }
    let starts = pattern.starts_with('%');
    let ends = pattern.ends_with('%');
    let inner = pattern.trim_matches('%');
    if inner.contains('%') {
        return Kind::Glob(glob_tokens(pattern));
    }
    if starts && ends {
        Kind::Contains(lower(inner))
    } else if ends {
        Kind::StartsWith(lower(inner))
    } else if starts {
        Kind::EndsWith(lower(inner))
    } else {
        Kind::Glob(glob_tokens(pattern))
    }
}

/// Translate a LIKE pattern to glob tokens (`%` -> `Star`, `_` -> `AnyOne`,
/// every other character a literal). Case folding is applied per character at
/// match time, never here, so token counts stay aligned with the input.
fn glob_tokens(pattern: &str) -> Vec<GlobToken> {
    pattern
        .chars()
        .map(|c| match c {
            '%' => GlobToken::Star,
            '_' => GlobToken::AnyOne,
            other => GlobToken::Lit(other),
        })
        .collect()
}

/// Full-string glob match supporting `Star` (any run) and `AnyOne` (single
/// char), with literals compared case-insensitively when `ci`.
fn glob_match(text: &str, pat: &[GlobToken], ci: bool) -> bool {
    let t: Vec<char> = text.chars().collect();
    let (mut ti, mut pi) = (0usize, 0usize);
    let (mut star_pi, mut star_ti): (Option<usize>, usize) = (None, 0);
    while ti < t.len() {
        if matches_here(pat.get(pi), t[ti], ci) {
            ti += 1;
            pi += 1;
        } else if matches!(pat.get(pi), Some(GlobToken::Star)) {
            star_pi = Some(pi);
            star_ti = ti;
            pi += 1;
        } else if let Some(sp) = star_pi {
            pi = sp + 1;
            star_ti += 1;
            ti = star_ti;
        } else {
            return false;
        }
    }
    while matches!(pat.get(pi), Some(GlobToken::Star)) {
        pi += 1;
    }
    pi == pat.len()
}

/// Whether `token` consumes the single character `c` (an `AnyOne`, or a literal
/// equal to `c`, case-folded when `ci`).
fn matches_here(token: Option<&GlobToken>, c: char, ci: bool) -> bool {
    match token {
        Some(GlobToken::AnyOne) => true,
        Some(GlobToken::Lit(lit)) => char_eq(c, *lit, ci),
        _ => false,
    }
}

/// Single-character equality, case-insensitive (Unicode simple fold) when `ci`.
fn char_eq(a: char, b: char, ci: bool) -> bool {
    a == b || (ci && a.to_lowercase().eq(b.to_lowercase()))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn fast_paths() {
        assert!(LikeMatcher::compile("%ell%", false).matches("hello"));
        assert!(LikeMatcher::compile("hel%", false).matches("hello"));
        assert!(LikeMatcher::compile("%llo", false).matches("hello"));
        assert!(!LikeMatcher::compile("hel%", false).matches("world"));
    }

    #[test]
    fn case_insensitive() {
        assert!(LikeMatcher::compile("%ELL%", true).matches("Hello"));
        assert!(LikeMatcher::compile("HEL%", true).matches("hello"));
    }

    #[test]
    fn glob_paths() {
        // `_` -> single char
        assert!(LikeMatcher::compile("h_llo", false).matches("hello"));
        assert!(!LikeMatcher::compile("h_llo", false).matches("heello"));
        // interior `%` -> `*`
        assert!(LikeMatcher::compile("h%o", false).matches("hello"));
        assert!(LikeMatcher::compile("a%b%c", false).matches("axxbyyc"));
    }

    #[test]
    fn empty_pattern_matches_only_empty() {
        assert!(LikeMatcher::compile("", false).matches(""));
        assert!(!LikeMatcher::compile("", false).matches("x"));
    }

    #[test]
    fn star_and_question_are_literals_not_wildcards() {
        // SQL LIKE: only `%` and `_` are special; `*`/`?` match literally.
        assert!(LikeMatcher::compile("a*b", false).matches("a*b"));
        assert!(!LikeMatcher::compile("a*b", false).matches("axyzb"));
        assert!(LikeMatcher::compile("h?llo", false).matches("h?llo"));
        assert!(!LikeMatcher::compile("h?llo", false).matches("hello"));
        // `[` is a literal too (no character classes in SQL LIKE).
        assert!(LikeMatcher::compile("a[b", false).matches("a[b"));
    }

    #[test]
    fn ci_glob_handles_length_changing_fold() {
        // `İ`.to_lowercase() expands to two chars; `_` must still match it as a
        // single character (the bug a pre-folded field re-introduced).
        assert!(LikeMatcher::compile("a_", true).matches("aİ"));
        // `%` still spans it, and a case-insensitive literal still matches.
        assert!(LikeMatcher::compile("A%", true).matches("aİx"));
    }
}
