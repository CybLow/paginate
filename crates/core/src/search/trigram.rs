//! Trigram (3-gram) similarity for fuzzy ranked search — the pg_trgm model.
//!
//! A string's trigram set is built per word: lowercase (done upstream by
//! [`crate::normalize::normalize_text`]), split on non-alphanumeric boundaries,
//! pad each word with two leading and one trailing space, and slide a 3-char
//! window. `"cat"` → `{"  c", " ca", "cat", "at "}`.
//!
//! Two scores over the sorted, de-duplicated sets (both 0-100, the scale the
//! search engine already uses):
//!
//! * [`similarity`] — Jaccard `|Q ∩ T| / |Q ∪ T|`: symmetric, set-based, so it is
//!   naturally word-order agnostic (backs `FuzzyMode::TokenSort`).
//! * [`containment`] — `|Q ∩ T| / |Q|`: the fraction of the *query's* trigrams
//!   present in the target, undiluted by target length, so a short query still
//!   scores high inside a long title (backs `FuzzyMode::Fuzzy`).
//!
//! Both are O(len) (no edit-distance DP), and both are 0 exactly when the sets
//! share no trigram — which is what makes an inverted-index candidate prefilter
//! *exact* (an item with no shared query trigram cannot clear any threshold).

/// One trigram: three Unicode scalar values from a space-padded word, packed
/// into a `u64` (21 bits each, most-significant char first).
///
/// The packing is **order-preserving** — comparing the `u64`s is exactly the
/// lexicographic comparison of the three chars — so sorted-set intersection and
/// dedup are unchanged, while the footprint halves versus a `[char; 3]` (8 bytes
/// vs 12) for tighter posting lists and cheaper compares. A real newtype (not a
/// type alias) so the domain type can't be confused with a raw char array.
#[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Debug)]
pub struct Trigram(u64);

impl Trigram {
    /// Pack three chars into the order-preserving `u64` representation. Every
    /// Unicode scalar fits in 21 bits (max `U+10FFFF`), so the three never overlap.
    #[must_use]
    fn new(a: char, b: char, c: char) -> Self {
        Self((a as u64) << 42 | (b as u64) << 21 | c as u64)
    }
}

/// The sorted, de-duplicated trigram set of `text` (pg_trgm padding/boundaries).
#[must_use]
pub fn trigrams(text: &str) -> Vec<Trigram> {
    // Byte length is an over-estimate of the trigram count (≥ char count), so
    // one up-front allocation avoids regrowth on the hot path.
    let mut out: Vec<Trigram> = Vec::with_capacity(text.len() + 2);
    for word in text.split(|c: char| !c.is_alphanumeric()) {
        if word.is_empty() {
            continue;
        }
        // Slide a rolling 3-char window over `"  <word> "` without allocating a
        // padded buffer: `(a, b)` start as the two leading spaces, then each new
        // char `c` (the word's chars, then one trailing space) emits `[a, b, c]`.
        let (mut a, mut b) = (' ', ' ');
        for c in word.chars().chain(std::iter::once(' ')) {
            out.push(Trigram::new(a, b, c));
            a = b;
            b = c;
        }
    }
    out.sort_unstable();
    out.dedup();
    out
}

/// Number of shared trigrams between two **sorted** trigram sets.
fn intersection_count(a: &[Trigram], b: &[Trigram]) -> usize {
    let (mut i, mut j, mut count) = (0, 0, 0);
    while i < a.len() && j < b.len() {
        match a[i].cmp(&b[j]) {
            std::cmp::Ordering::Less => i += 1,
            std::cmp::Ordering::Greater => j += 1,
            std::cmp::Ordering::Equal => {
                count += 1;
                i += 1;
                j += 1;
            }
        }
    }
    count
}

/// Jaccard similarity `|Q ∩ T| / |Q ∪ T|` as a truncated 0-100 integer.
#[must_use]
pub fn similarity(query: &[Trigram], target: &[Trigram]) -> i64 {
    if query.is_empty() || target.is_empty() {
        return 0;
    }
    let inter = intersection_count(query, target);
    let union = query.len() + target.len() - inter;
    ((inter as f64 / union as f64) * 100.0) as i64
}

/// Containment `|Q ∩ T| / |Q|` as a truncated 0-100 integer (not diluted by
/// target length — a short query inside a long target still scores high).
#[must_use]
pub fn containment(query: &[Trigram], target: &[Trigram]) -> i64 {
    if query.is_empty() {
        return 0;
    }
    let inter = intersection_count(query, target);
    ((inter as f64 / query.len() as f64) * 100.0) as i64
}

#[cfg(test)]
mod tests {
    use super::*;

    fn tg(s: &str) -> Vec<Trigram> {
        trigrams(s)
    }

    #[test]
    fn cat_trigram_set_matches_pg_trgm() {
        // Sorted, deduped: `{"  c", " ca", "at ", "cat"}` (space < 'a' < 'c').
        assert_eq!(
            trigrams("cat"),
            vec![
                Trigram::new(' ', ' ', 'c'),
                Trigram::new(' ', 'c', 'a'),
                Trigram::new('a', 't', ' '),
                Trigram::new('c', 'a', 't'),
            ]
        );
    }

    #[test]
    fn split_on_non_alphanumeric_words() {
        // "foo bar" -> two padded words; underscores/punctuation are boundaries.
        assert_eq!(trigrams("foo_bar"), trigrams("foo bar"));
        assert_eq!(trigrams("a@b.c"), trigrams("a b c"));
    }

    #[test]
    fn identical_strings_score_100() {
        let t = tg("postgres");
        assert_eq!(similarity(&t, &t), 100);
        assert_eq!(containment(&t, &t), 100);
    }

    #[test]
    fn disjoint_strings_score_0() {
        assert_eq!(similarity(&tg("abc"), &tg("xyz")), 0);
        assert_eq!(containment(&tg("abc"), &tg("xyz")), 0);
    }

    #[test]
    fn transposition_keeps_high_similarity() {
        // "teh" vs "the": Levenshtein 2, but trigram sets overlap strongly.
        assert!(similarity(&tg("teh"), &tg("the")) > 0);
    }

    #[test]
    fn containment_beats_similarity_for_short_query_in_long_title() {
        // The query "iphone" is fully contained in the longer title; containment
        // stays high while Jaccard is diluted by the title's extra trigrams.
        let q = tg("iphone");
        let title = tg("apple iphone fifteen pro max");
        assert!(containment(&q, &title) > similarity(&q, &title));
        assert!(containment(&q, &title) >= 100); // every query trigram present
    }

    #[test]
    fn word_order_does_not_change_jaccard() {
        assert_eq!(similarity(&tg("alice johnson"), &tg("johnson alice")), 100);
    }
}
