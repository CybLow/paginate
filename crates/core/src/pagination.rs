//! Offset/limit pagination arithmetic.
//!
//! Direct, dependency-free port of the math in pypaginate's
//! `domain/params.py` and `domain/pages.py`:
//!
//! * `offset      = (page - 1) * limit`
//! * `pages       = ceil(total / limit)`   (0 when `total == 0`)
//! * `has_next    = page < pages`
//! * `has_prev    = page > 1`

/// Page-level metadata derived from `(page, limit, total)`.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct OffsetMeta {
    /// The (possibly clamped) 1-based page number.
    pub page: u64,
    /// Total number of pages.
    pub pages: u64,
    /// Whether a following page exists.
    pub has_next: bool,
    /// Whether a preceding page exists.
    pub has_previous: bool,
}

/// Zero-based row offset for `(page, limit)`.
#[must_use]
pub fn offset(page: u64, limit: u64) -> u64 {
    page.saturating_sub(1).saturating_mul(limit)
}

/// Total page count for `total` rows at `limit` per page.
///
/// Returns `0` for an empty result set and guards against a zero `limit`
/// (params validation already forbids it, but the core must never divide by 0).
#[must_use]
pub fn max_pages(total: u64, limit: u64) -> u64 {
    if limit == 0 || total == 0 {
        return 0;
    }
    total.div_ceil(limit)
}

/// Full [`OffsetMeta`] for `(page, limit, total)`.
#[must_use]
pub fn offset_meta(page: u64, limit: u64, total: u64) -> OffsetMeta {
    let pages = max_pages(total, limit);
    OffsetMeta {
        page,
        pages,
        has_next: page < pages,
        has_previous: page > 1,
    }
}

/// Clamp `page` to the valid `[1, max_page]` range (mirrors `OffsetParams.clamp`).
#[must_use]
pub fn clamp_page(page: u64, limit: u64, total: u64) -> u64 {
    if total == 0 {
        return 1;
    }
    let max_page = max_pages(total, limit).max(1);
    page.min(max_page).max(1)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn offset_is_zero_based() {
        assert_eq!(offset(1, 20), 0);
        assert_eq!(offset(3, 20), 40);
        assert_eq!(offset(1, 0), 0);
    }

    #[test]
    fn max_pages_uses_ceiling() {
        assert_eq!(max_pages(0, 20), 0);
        assert_eq!(max_pages(1, 20), 1);
        assert_eq!(max_pages(100, 20), 5);
        assert_eq!(max_pages(101, 20), 6);
        assert_eq!(max_pages(5, 0), 0); // div-by-zero guard
    }

    #[test]
    fn meta_flags_match_python() {
        let first = offset_meta(1, 20, 100);
        assert_eq!(first.pages, 5);
        assert!(first.has_next);
        assert!(!first.has_previous);

        let last = offset_meta(5, 20, 100);
        assert!(!last.has_next);
        assert!(last.has_previous);

        let empty = offset_meta(1, 20, 0);
        assert_eq!(empty.pages, 0);
        assert!(!empty.has_next);
        assert!(!empty.has_previous);
    }

    #[test]
    fn clamp_keeps_valid_pages_and_floors_at_one() {
        assert_eq!(clamp_page(3, 20, 100), 3);
        assert_eq!(clamp_page(10, 20, 100), 5);
        assert_eq!(clamp_page(7, 20, 0), 1);
        assert_eq!(clamp_page(0, 20, 100), 1);
    }
}
