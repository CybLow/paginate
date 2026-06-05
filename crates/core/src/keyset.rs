//! Portable keyset (cursor) predicate structure.
//!
//! Keyset pagination over `ORDER BY (k0, k1, ...)` needs the lexicographic
//! comparison
//!
//! ```text
//! (k0 OP0 v0)
//!   OR (k0 = v0 AND k1 OP1 v1)
//!   OR (k0 = v0 AND k1 = v1 AND k2 OP2 v2)
//!   ...
//! ```
//!
//! where `OPi` is `>` when key `i` is ascending and `<` when descending. That
//! *structure* is the same for every backend; only the rendering (to SQL, to an
//! ORM expression tree) differs. The core owns the structure — [`keyset_terms`]
//! returns it as OR-of-AND `(key_index, op)` terms — so each adapter
//! (SQLAlchemy, Django, Drizzle, Prisma, ...) only renders `key[i] OP value[i]`
//! and combines with its own AND/OR, never re-deriving the nesting.

/// A comparison operator in a keyset term.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum KeysetOp {
    /// Strict greater-than (`key > value`).
    Gt,
    /// Strict less-than (`key < value`).
    Lt,
    /// Equality (`key = value`), used for the tie-break prefix.
    Eq,
}

impl KeysetOp {
    /// Stable lowercase name for the FFI boundary (`"gt"` / `"lt"` / `"eq"`).
    #[must_use]
    pub fn as_str(self) -> &'static str {
        match self {
            KeysetOp::Gt => "gt",
            KeysetOp::Lt => "lt",
            KeysetOp::Eq => "eq",
        }
    }
}

/// One AND-term: `(key_index, op)` pairs, rendered as `key[i] OP value[i]` and
/// combined with AND.
pub type Term = Vec<(usize, KeysetOp)>;

/// Build the lexicographic keyset predicate as OR-of-AND terms for the given
/// effective key directions. `ascending[i]` is the direction of key `i` *after*
/// any backward-pagination flip the caller applies, so the strict comparison is
/// `Gt` when ascending and `Lt` when descending.
///
/// Term `i` equals key `j` for every `j < i`, then strictly compares key `i`:
/// `[(0,Eq), ..., (i-1,Eq), (i, Gt|Lt)]`. An empty `ascending` yields no terms.
#[must_use]
pub fn keyset_terms(ascending: &[bool]) -> Vec<Term> {
    (0..ascending.len())
        .map(|i| {
            let mut term: Term = (0..i).map(|j| (j, KeysetOp::Eq)).collect();
            let op = if ascending[i] {
                KeysetOp::Gt
            } else {
                KeysetOp::Lt
            };
            term.push((i, op));
            term
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn single_ascending_key() {
        assert_eq!(keyset_terms(&[true]), vec![vec![(0, KeysetOp::Gt)]]);
    }

    #[test]
    fn single_descending_key() {
        assert_eq!(keyset_terms(&[false]), vec![vec![(0, KeysetOp::Lt)]]);
    }

    #[test]
    fn two_keys_asc_desc() {
        // ORDER BY (k0 ASC, k1 DESC):
        //   (k0 > v0) OR (k0 = v0 AND k1 < v1)
        assert_eq!(
            keyset_terms(&[true, false]),
            vec![
                vec![(0, KeysetOp::Gt)],
                vec![(0, KeysetOp::Eq), (1, KeysetOp::Lt)],
            ]
        );
    }

    #[test]
    fn three_keys_build_equality_prefix() {
        let terms = keyset_terms(&[true, true, true]);
        assert_eq!(terms.len(), 3);
        assert_eq!(
            terms[2],
            vec![(0, KeysetOp::Eq), (1, KeysetOp::Eq), (2, KeysetOp::Gt)]
        );
    }

    #[test]
    fn empty_keys_yield_no_terms() {
        assert!(keyset_terms(&[]).is_empty());
    }
}
