//! Canonical validation of pagination inputs.
//!
//! The single source of truth for the limits and rules **every** binding
//! enforces — so the Python and TS packages can't drift, and neither has to
//! embed a validator (Pydantic, zod, …) to get them. The host types stay thin
//! data holders that delegate here; an app can layer its own validator on top,
//! but these invariants always hold. Each check returns
//! [`CoreError::Validation`] with a host-facing message.

use crate::error::{CoreError, Result};
use crate::filter::{FilterInput, FilterNode};

/// Maximum page size (DoS mitigation) — one definition for every language.
pub const MAX_LIMIT: u64 = 1000;

/// Maximum search query length, in characters (DoS mitigation).
pub const MAX_QUERY_LEN: usize = 500;

/// Maximum `FilterGroup` nesting depth.
pub const MAX_FILTER_DEPTH: usize = 5;

fn invalid(message: impl Into<String>) -> CoreError {
    CoreError::Validation {
        message: message.into(),
    }
}

/// Validate a page limit: `1 <= limit <= MAX_LIMIT`.
///
/// # Errors
/// [`CoreError::Validation`] if the limit is below 1 or above [`MAX_LIMIT`].
pub fn validate_limit(limit: i64) -> Result<()> {
    // Parse-don't-validate: the single source of truth is `Limit::new`; a
    // negative host value can't fit `u64`, so it fails the same `>= 1` check.
    let value = u64::try_from(limit).map_err(|_| invalid("limit must be >= 1"))?;
    crate::pagination::Limit::new(value).map(|_| ())
}

/// Validate offset params: a 1-based `page` and a valid `limit`.
///
/// # Errors
/// [`CoreError::Validation`] if `page < 1` or the limit is out of range.
pub fn validate_offset(page: i64, limit: i64) -> Result<()> {
    if page < 1 {
        return Err(invalid("page must be >= 1"));
    }
    validate_limit(limit)
}

/// Validate cursor params: a valid `limit`, and `after`/`before` not both set.
///
/// # Errors
/// [`CoreError::Validation`] if the limit is out of range or both cursors are set.
pub fn validate_cursor(limit: i64, has_after: bool, has_before: bool) -> Result<()> {
    validate_limit(limit)?;
    if has_after && has_before {
        return Err(invalid("after and before are mutually exclusive"));
    }
    Ok(())
}

/// Validate a search query: at most [`MAX_QUERY_LEN`] characters.
///
/// # Errors
/// [`CoreError::Validation`] if the query is too long.
pub fn validate_search_query(query: &str) -> Result<()> {
    // Stop counting once the limit is exceeded — a multi-megabyte hostile query
    // is rejected after MAX_QUERY_LEN+1 chars, not after a full O(n) walk.
    if query.chars().take(MAX_QUERY_LEN + 1).count() > MAX_QUERY_LEN {
        return Err(invalid(format!(
            "Query must not exceed {MAX_QUERY_LEN} characters"
        )));
    }
    Ok(())
}

/// Validate a precomputed filter-nesting `depth`: at most [`MAX_FILTER_DEPTH`].
///
/// # Errors
/// [`CoreError::Validation`] if the depth is too great.
pub fn validate_filter_depth(depth: usize) -> Result<()> {
    if depth > MAX_FILTER_DEPTH {
        return Err(invalid(format!(
            "FilterGroup nesting must not exceed {MAX_FILTER_DEPTH} levels"
        )));
    }
    Ok(())
}

/// Validate a parsed filter tree's nesting depth (computed from `input`). The
/// bindings call this so every language enforces the limit at the engine
/// boundary, however the group was built.
///
/// # Errors
/// [`CoreError::Validation`] if the nesting exceeds [`MAX_FILTER_DEPTH`].
pub fn validate_filter_input(input: &FilterInput) -> Result<()> {
    let depth = match input {
        FilterInput::Flat(_) => 1,
        FilterInput::Group(group) => group_depth(&group.conditions),
    };
    validate_filter_depth(depth)
}

/// Depth of a group's condition list: `1 + max nested-group depth` (mirrors
/// pypaginate's `_measure_depth`; a group of only leaves is depth 1).
fn group_depth(conditions: &[FilterNode]) -> usize {
    let deepest_child = conditions
        .iter()
        .map(|node| match node {
            FilterNode::Group(sub) => group_depth(&sub.conditions),
            FilterNode::Spec(_) => 0,
        })
        .max()
        .unwrap_or(0);
    1 + deepest_child
}

#[cfg(test)]
mod tests {
    use super::*;

    fn msg(result: Result<()>) -> String {
        match result {
            Err(CoreError::Validation { message }) => message,
            other => panic!("expected a validation error, got {other:?}"),
        }
    }

    #[test]
    fn limit_bounds() {
        assert!(validate_limit(1).is_ok());
        assert!(validate_limit(MAX_LIMIT as i64).is_ok());
        assert_eq!(msg(validate_limit(0)), "limit must be >= 1");
        assert!(msg(validate_limit(MAX_LIMIT as i64 + 1)).starts_with("limit must not exceed"));
    }

    #[test]
    fn offset_requires_positive_page() {
        assert!(validate_offset(1, 20).is_ok());
        assert_eq!(msg(validate_offset(0, 20)), "page must be >= 1");
        // A bad limit still surfaces even when the page is fine.
        assert_eq!(msg(validate_offset(1, 0)), "limit must be >= 1");
    }

    #[test]
    fn cursor_after_before_mutually_exclusive() {
        assert!(validate_cursor(20, true, false).is_ok());
        assert!(validate_cursor(20, false, false).is_ok());
        assert_eq!(
            msg(validate_cursor(20, true, true)),
            "after and before are mutually exclusive"
        );
    }

    #[test]
    fn query_length_bound() {
        assert!(validate_search_query(&"a".repeat(MAX_QUERY_LEN)).is_ok());
        assert!(
            msg(validate_search_query(&"a".repeat(MAX_QUERY_LEN + 1))).contains("500 characters")
        );
    }

    #[test]
    fn filter_depth_bound() {
        assert!(validate_filter_depth(MAX_FILTER_DEPTH).is_ok());
        assert!(msg(validate_filter_depth(MAX_FILTER_DEPTH + 1)).contains("5 levels"));
    }

    #[test]
    fn filter_input_depth_is_measured_and_capped() {
        use crate::filter::{FilterGroup, FilterLogic, FilterOp, FilterSpec};
        use crate::value::Value;

        fn leaf() -> FilterNode {
            FilterNode::Spec(FilterSpec {
                field: "a".into(),
                op: FilterOp::Eq,
                value: Value::Int(1),
                logic: FilterLogic::And,
            })
        }
        // Wrap a leaf in `n` nested AND groups, yielding nesting depth `n`.
        fn nest(n: usize) -> FilterInput {
            let mut node = leaf();
            for _ in 0..n {
                node = FilterNode::Group(FilterGroup {
                    logic: FilterLogic::And,
                    conditions: vec![node],
                });
            }
            match node {
                FilterNode::Group(group) => FilterInput::Group(group),
                FilterNode::Spec(spec) => FilterInput::Flat(vec![spec]),
            }
        }

        assert!(validate_filter_input(&nest(MAX_FILTER_DEPTH)).is_ok()); // depth 5 ok
        assert!(validate_filter_input(&nest(MAX_FILTER_DEPTH + 1)).is_err()); // depth 6 rejected
        assert!(validate_filter_input(&FilterInput::Flat(vec![])).is_ok()); // flat list = depth 1
    }
}
