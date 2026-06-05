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
    fn ascii_single_pass_matches_python_split_semantics() {
        // VT (\x0b) and FF (\x0c) count as whitespace (char::is_whitespace),
        // matching Python's str.split(); leading/trailing/runs collapse.
        assert_eq!(normalize_text("a\u{0b}b\u{0c}c"), "a b c");
        assert_eq!(normalize_text("\tTAB\tand  spaces\n"), "tab and spaces");
        assert_eq!(normalize_text("Multi   Word  Test"), "multi word test");
    }
}
