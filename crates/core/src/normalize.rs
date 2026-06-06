//! Text normalization for search and filtering.
//!
//! Port of pypaginate's `text/normalize.py`:
//!
//! * **ASCII fast path** — lowercase then collapse whitespace. On ASCII,
//!   `str.casefold()` equals lowercasing, so this is byte-identical to Python.
//! * **Non-ASCII path** — NFKD-decompose, drop combining marks, lowercase,
//!   collapse whitespace.
//!
//! The bounded result cache stays in the binding layer (exactly where the
//! Python module keeps it), so this function is referentially transparent and
//! trivially portable.
//!
//! Known minor divergences from `str.casefold()` on the non-ASCII path: full
//! case folds such as `ß → ss` are not applied (we lowercase instead), and
//! spacing/enclosing marks (Mc/Me) are also dropped, not just nonspacing (Mn).
//! These affect a tiny fraction of inputs and never the ASCII fast path.

use std::borrow::Cow;

use unicode_normalization::char::is_combining_mark;
use unicode_normalization::UnicodeNormalization;

/// Normalize `value` for case- and accent-insensitive matching.
#[must_use]
pub fn normalize_text(value: &str) -> String {
    if value.is_ascii() {
        return normalize_ascii(value);
    }
    let stripped: String = value.nfkd().filter(|c| !is_combining_mark(*c)).collect();
    collapse_whitespace(&stripped.to_lowercase())
}

/// Like [`normalize_text`], but **borrows** `value` unchanged when it is already
/// normalized (the common case for search fields like emails, ids, and slugs),
/// so the per-item search hot path allocates nothing for already-clean text.
#[must_use]
pub fn normalize_text_cow(value: &str) -> Cow<'_, str> {
    if value.is_ascii() && is_ascii_normalized(value) {
        return Cow::Borrowed(value);
    }
    Cow::Owned(normalize_text(value))
}

/// True iff [`normalize_ascii`] would return `s` unchanged: pure ASCII, no
/// uppercase, and whitespace only as single `' '` separators (none leading,
/// trailing, repeated, or non-space like `\t`/`\n`). When this holds,
/// `normalize_text(s) == s`, so the caller can borrow instead of reallocate.
fn is_ascii_normalized(s: &str) -> bool {
    let mut prev_space = true; // start "after a space" so a leading space is rejected
    for &b in s.as_bytes() {
        if b.is_ascii_uppercase() {
            return false;
        }
        if is_ascii_ws(b) {
            if b != b' ' || prev_space {
                return false; // non-space whitespace, or a leading/repeated space
            }
            prev_space = true;
        } else {
            prev_space = false;
        }
    }
    !prev_space // reject a trailing space (and the empty string, which is cheap to own)
}

/// ASCII whitespace per `char::is_whitespace` (so `split_whitespace` parity is
/// preserved): note `\x0b` (VT) and `\x0c` (FF), which `is_ascii_whitespace`
/// omits, count here.
fn is_ascii_ws(b: u8) -> bool {
    matches!(b, b' ' | b'\t' | b'\n' | 0x0b | 0x0c | b'\r')
}

/// Single-pass ASCII normalize — lowercase + collapse whitespace runs to single
/// spaces + trim ends, in ONE allocation. Byte-identical to
/// `" ".join(value.lower().split())` on ASCII (the common case).
fn normalize_ascii(value: &str) -> String {
    let mut out = String::with_capacity(value.len());
    let mut pending_space = false;
    for &b in value.as_bytes() {
        if is_ascii_ws(b) {
            pending_space = !out.is_empty();
            continue;
        }
        if pending_space {
            out.push(' ');
            pending_space = false;
        }
        out.push(b.to_ascii_lowercase() as char);
    }
    out
}

/// Collapse whitespace runs to single spaces and trim the ends —
/// equivalent to Python's `" ".join(s.split())` — without the intermediate Vec.
fn collapse_whitespace(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for word in s.split_whitespace() {
        if !out.is_empty() {
            out.push(' ');
        }
        out.push_str(word);
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ascii_lowercases_and_collapses() {
        assert_eq!(normalize_text("Hello World"), "hello world");
        assert_eq!(normalize_text("  Foo   Bar  "), "foo bar");
        assert_eq!(normalize_text("UPPER"), "upper");
        assert_eq!(normalize_text(""), "");
        assert_eq!(normalize_text("   "), "");
    }

    #[test]
    fn strips_accents_on_latin_text() {
        assert_eq!(normalize_text("Café"), "cafe");
        assert_eq!(normalize_text("JOSÉ"), "jose");
        assert_eq!(normalize_text("naïve"), "naive");
        assert_eq!(normalize_text("Crème Brûlée"), "creme brulee");
    }

    #[test]
    fn idempotent() {
        let once = normalize_text("Héllo   WÖRLD");
        assert_eq!(normalize_text(&once), once);
    }

    #[test]
    fn cow_always_equals_owned_and_borrows_when_already_normalized() {
        use std::borrow::Cow;
        // The borrowing variant must produce byte-identical output to the owned
        // one for every input — borrowing is only an allocation optimization.
        let cases = [
            "user42@test.com",
            "hello world",
            "abc",
            "already_normalized-slug.v2",
            "Hello",
            "  lead",
            "trail ",
            "a  b",
            "a\tb",
            "Café",
            "MiXeD Case",
            "",
            "x",
            "a b c",
            "UPPER",
            "with\nnewline",
        ];
        for s in cases {
            assert_eq!(
                normalize_text_cow(s).as_ref(),
                normalize_text(s),
                "value={s:?}"
            );
        }
        // Already-normalized text borrows (zero allocation)...
        assert!(matches!(
            normalize_text_cow("user42@test.com"),
            Cow::Borrowed(_)
        ));
        assert!(matches!(
            normalize_text_cow("hello world"),
            Cow::Borrowed(_)
        ));
        // ...everything needing work (case, accents, whitespace) is owned.
        assert!(matches!(normalize_text_cow("Hello"), Cow::Owned(_)));
        assert!(matches!(normalize_text_cow("a  b"), Cow::Owned(_)));
        assert!(matches!(normalize_text_cow(" x"), Cow::Owned(_)));
        assert!(matches!(normalize_text_cow("x "), Cow::Owned(_)));
        assert!(matches!(normalize_text_cow("a\tb"), Cow::Owned(_)));
        assert!(matches!(normalize_text_cow("Café"), Cow::Owned(_)));
    }

    #[test]
    fn ascii_single_pass_matches_python_split_semantics() {
        // VT (\x0b) and FF (\x0c) count as whitespace (char::is_whitespace),
        // matching Python's str.split(); leading/trailing/runs collapse.
        assert_eq!(normalize_text("a\u{0b}b\u{0c}c"), "a b c");
        assert_eq!(normalize_text("\tTAB\tand  spaces\n"), "tab and spaces");
        assert_eq!(normalize_text("Multi   Word  Test"), "multi word test");
    }
}
