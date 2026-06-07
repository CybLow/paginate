//! Offset/limit pagination arithmetic.
//!
//! Direct, dependency-free port of the math in pypaginate's
//! `domain/params.py` and `domain/pages.py`:
//!
//! * `offset      = (page - 1) * limit`
//! * `pages       = ceil(total / limit)`   (0 when `total == 0`)
//! * `has_next    = page < pages`
//! * `has_prev    = page > 1`
//!
//! The page size crosses these functions as a [`Limit`] newtype rather than a
//! bare `u64`, so an out-of-range limit is unrepresentable here (parse, don't
//! validate) and `(page, limit)` can't be silently transposed at a call site.

use std::num::NonZeroU64;

use crate::error::{CoreError, Result};
use crate::validate::MAX_LIMIT;

/// A validated page size: `1 <= limit <= MAX_LIMIT`. Constructed via
/// [`Limit::new`], so the arithmetic below never sees zero (no div-by-zero
/// guard) or an out-of-range value.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Limit(NonZeroU64);

impl Limit {
    /// Parse a host-supplied page size into a validated [`Limit`].
    ///
    /// # Errors
    /// [`CoreError::Validation`] if `limit` is `0` or exceeds [`MAX_LIMIT`].
    pub fn new(limit: u64) -> Result<Self> {
        let value = NonZeroU64::new(limit).ok_or_else(|| CoreError::Validation {
            message: "limit must be >= 1".to_owned(),
        })?;
        if value.get() > MAX_LIMIT {
            return Err(CoreError::Validation {
                message: format!("limit must not exceed {MAX_LIMIT}"),
            });
        }
        Ok(Self(value))
    }

    /// The validated limit as a `u64`.
    #[must_use]
    pub fn get(self) -> u64 {
        self.0.get()
    }
}

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
pub fn offset(page: u64, limit: Limit) -> u64 {
    page.saturating_sub(1).saturating_mul(limit.get())
}

/// Total page count for `total` rows at `limit` per page (0 for an empty set).
#[must_use]
pub fn max_pages(total: u64, limit: Limit) -> u64 {
    if total == 0 {
        return 0;
    }
    total.div_ceil(limit.get())
}

/// Full [`OffsetMeta`] for `(page, limit, total)`.
#[must_use]
pub fn offset_meta(page: u64, limit: Limit, total: u64) -> OffsetMeta {
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
pub fn clamp_page(page: u64, limit: Limit, total: u64) -> u64 {
    if total == 0 {
        return 1;
    }
    let max_page = max_pages(total, limit).max(1);
    page.min(max_page).max(1)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn lim(n: u64) -> Limit {
        Limit::new(n).expect("valid limit")
    }

    #[test]
    fn limit_rejects_zero_and_over_max() {
        assert!(Limit::new(0).is_err());
        assert!(Limit::new(MAX_LIMIT + 1).is_err());
        assert_eq!(lim(20).get(), 20);
        assert_eq!(lim(MAX_LIMIT).get(), MAX_LIMIT);
    }

    #[test]
    fn offset_is_zero_based() {
        assert_eq!(offset(1, lim(20)), 0);
        assert_eq!(offset(3, lim(20)), 40);
    }

    #[test]
    fn max_pages_uses_ceiling() {
        assert_eq!(max_pages(0, lim(20)), 0);
        assert_eq!(max_pages(1, lim(20)), 1);
        assert_eq!(max_pages(100, lim(20)), 5);
        assert_eq!(max_pages(101, lim(20)), 6);
    }

    #[test]
    fn meta_flags_match_python() {
        let first = offset_meta(1, lim(20), 100);
        assert_eq!(first.pages, 5);
        assert!(first.has_next);
        assert!(!first.has_previous);

        let last = offset_meta(5, lim(20), 100);
        assert!(!last.has_next);
        assert!(last.has_previous);

        let empty = offset_meta(1, lim(20), 0);
        assert_eq!(empty.pages, 0);
        assert!(!empty.has_next);
        assert!(!empty.has_previous);
    }

    #[test]
    fn clamp_keeps_valid_pages_and_floors_at_one() {
        assert_eq!(clamp_page(3, lim(20), 100), 3);
        assert_eq!(clamp_page(10, lim(20), 100), 5);
        assert_eq!(clamp_page(7, lim(20), 0), 1);
        assert_eq!(clamp_page(0, lim(20), 100), 1);
    }
}
