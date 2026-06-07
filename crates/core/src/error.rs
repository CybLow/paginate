//! Error type for the core engine.
//!
//! Mirrors the relevant arms of pypaginate's Python exception hierarchy
//! (`ValidationError`, `FilterError`, `SortError`, `SearchError`). Each variant
//! carries a stable [`ErrorKind`] (see [`CoreError::kind`]) so **both** binding
//! layers map onto their host exception hierarchy from one classification and
//! cannot drift apart — Python raises typed subclasses, Node sets matching error
//! codes, all driven by the same `kind`.

use thiserror::Error;

/// Stable, message-independent classification of a [`CoreError`].
///
/// The binding layer dispatches on this — never on the human-readable message —
/// so Python and Node stay symmetric. `#[non_exhaustive]`: the crate is
/// published independently (`core-v*`), so a new kind must not be a breaking
/// change; downstream `match`es need a `_` arm.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[non_exhaustive]
pub enum ErrorKind {
    /// A cursor string was malformed, truncated, or tampered with.
    InvalidCursor,
    /// A field path could not be resolved on an item.
    FieldNotFound,
    /// A filter operator could not be applied.
    Filter,
    /// A sort operation failed.
    Sort,
    /// A search query was invalid.
    Search,
    /// An input value failed validation.
    Validation,
}

/// A recoverable error raised by the core engine.
///
/// It is a flat, `Clone`/`Eq` value type by design: it crosses the FFI boundary
/// into Python / JS exceptions, so it carries owned messages rather than a
/// borrowed `source()` chain. Match on [`CoreError::kind`] for behaviour.
///
/// `#[non_exhaustive]`: the crate is published independently (`core-v*`), so new
/// variants must not be a breaking change — downstream `match`es need a `_` arm.
#[derive(Debug, Clone, PartialEq, Eq, Error)]
#[non_exhaustive]
pub enum CoreError {
    /// A cursor string was malformed, truncated, or tampered with.
    #[error("invalid cursor: {reason}")]
    InvalidCursor {
        /// Machine-readable reason (e.g. `"base64"`, `"unknown type tag: x"`).
        reason: String,
    },
    /// A field path could not be resolved on an item.
    #[error("field not found: {field}")]
    FieldNotFound {
        /// The dotted field path that failed to resolve.
        field: String,
    },
    /// A filter operator could not be applied (bad regex, bad operand, ...).
    #[error("filter error: {message}")]
    Filter {
        /// Human-readable description.
        message: String,
    },
    /// A sort operation failed (e.g. values were not comparable).
    #[error("sort error: {message}")]
    Sort {
        /// Human-readable description.
        message: String,
    },
    /// A search query was invalid.
    #[error("search error: {message}")]
    Search {
        /// Human-readable description.
        message: String,
    },
    /// An input value failed validation (out of range, mutually exclusive, ...).
    // Validation messages are user-facing input feedback — surfaced verbatim.
    #[error("{message}")]
    Validation {
        /// Human-readable description (surfaced verbatim to the host).
        message: String,
    },
}

impl CoreError {
    /// The stable [`ErrorKind`] of this error.
    ///
    /// Binding layers map this onto their host exception hierarchy, keeping the
    /// Python and Node error surfaces symmetric from a single source of truth.
    #[must_use]
    pub fn kind(&self) -> ErrorKind {
        match self {
            Self::InvalidCursor { .. } => ErrorKind::InvalidCursor,
            Self::FieldNotFound { .. } => ErrorKind::FieldNotFound,
            Self::Filter { .. } => ErrorKind::Filter,
            Self::Sort { .. } => ErrorKind::Sort,
            Self::Search { .. } => ErrorKind::Search,
            Self::Validation { .. } => ErrorKind::Validation,
        }
    }
}

/// Convenience alias used throughout the crate.
pub type Result<T> = std::result::Result<T, CoreError>;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn display_strings_are_stable() {
        let e = CoreError::InvalidCursor {
            reason: "base64".into(),
        };
        assert_eq!(e.to_string(), "invalid cursor: base64");
        let v = CoreError::Validation {
            message: "limit must be >= 1".into(),
        };
        assert_eq!(v.to_string(), "limit must be >= 1");
    }

    #[test]
    fn kind_is_stable_per_variant() {
        assert_eq!(
            CoreError::Filter {
                message: String::new()
            }
            .kind(),
            ErrorKind::Filter
        );
        assert_eq!(
            CoreError::FieldNotFound {
                field: String::new()
            }
            .kind(),
            ErrorKind::FieldNotFound
        );
    }
}
