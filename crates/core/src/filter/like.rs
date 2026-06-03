//! SQL `LIKE` / `ILIKE` matching, ported from pypaginate's `filtering/like.py`.
//!
//! Patterns are classified once into a fast string-method path (`%x%`, `x%`,
//! `%x`) or a `*`/`?` glob for everything else (interior `%`, or `_`).
//!
//! The glob handles `%` -> `*` and `_` -> `?` with full-string semantics, like
//! `fnmatch` on POSIX. It deliberately treats `[` as a literal (SQL `LIKE` has
//! no character classes), which is the only intentional divergence from
//! Python's `fnmatch`.

/// A LIKE pattern compiled once for repeated matching.
pub struct LikeMatcher {
    kind: Kind,
    case_insensitive: bool,
}

enum Kind {
    Contains(String),
    StartsWith(String),
    EndsWith(String),
    Glob(Vec<char>),
}

impl LikeMatcher {
    /// Compile a SQL LIKE pattern. When `case_insensitive`, literal parts are
    /// lowercased now and the field is lowercased at match time.
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
        let lowered;
        let f: &str = if self.case_insensitive {
            lowered = field.to_lowercase();
            &lowered
        } else {
            field
        };
        match &self.kind {
            Kind::Contains(inner) => f.contains(inner.as_str()),
            Kind::StartsWith(inner) => f.starts_with(inner.as_str()),
            Kind::EndsWith(inner) => f.ends_with(inner.as_str()),
            Kind::Glob(glob) => glob_match(f, glob),
        }
    }
}

fn classify(pattern: &str, ci: bool) -> Kind {
    let lower = |s: &str| if ci { s.to_lowercase() } else { s.to_owned() };
    if pattern.contains('_') {
        return Kind::Glob(glob_chars(pattern, ci));
    }
    let starts = pattern.starts_with('%');
    let ends = pattern.ends_with('%');
    let inner = pattern.trim_matches('%');
    if inner.contains('%') {
        return Kind::Glob(glob_chars(pattern, ci));
    }
    if starts && ends {
        Kind::Contains(lower(inner))
    } else if ends {
        Kind::StartsWith(lower(inner))
    } else if starts {
        Kind::EndsWith(lower(inner))
    } else {
        Kind::Glob(glob_chars(pattern, ci))
    }
}

/// Translate a LIKE pattern to a `*`/`?` glob (`%` -> `*`, `_` -> `?`).
fn glob_chars(pattern: &str, ci: bool) -> Vec<char> {
    let translated: String = pattern
        .chars()
        .map(|c| match c {
            '%' => '*',
            '_' => '?',
            other => other,
        })
        .collect();
    let final_str = if ci {
        translated.to_lowercase()
    } else {
        translated
    };
    final_str.chars().collect()
}

/// Full-string glob match supporting `*` (any run) and `?` (single char).
fn glob_match(text: &str, pat: &[char]) -> bool {
    let t: Vec<char> = text.chars().collect();
    let (mut ti, mut pi) = (0usize, 0usize);
    let (mut star_pi, mut star_ti): (Option<usize>, usize) = (None, 0);
    while ti < t.len() {
        if pi < pat.len() && (pat[pi] == '?' || pat[pi] == t[ti]) {
            ti += 1;
            pi += 1;
        } else if pi < pat.len() && pat[pi] == '*' {
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
    while pi < pat.len() && pat[pi] == '*' {
        pi += 1;
    }
    pi == pat.len()
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
}
