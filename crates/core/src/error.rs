//! Error type for the core engine.
//!
//! Mirrors the relevant arms of pypaginate's Python exception hierarchy
//! (`ValidationError`, `FilterError`, `SortError`, `SearchError`). The binding
//! layer maps each variant onto the corresponding host exception.

use std::fmt;

/// A recoverable error raised by the core engine.
///
/// `#[non_exhaustive]`: the crate is published independently (`core-v*`), so new
/// variants must not be a breaking change — downstream `match`es need a `_` arm.
#[derive(Debug, Clone, PartialEq, Eq)]
#[non_exhaustive]
pub enum CoreError {
    /// A cursor string was malformed, truncated, or tampered with.
    InvalidCursor {
        /// Machine-readable reason (e.g. `"base64"`, `"unknown type tag: x"`).
        reason: String,
    },
    /// A field path could not be resolved on an item.
    FieldNotFound {
        /// The dotted field path that failed to resolve.
        field: String,
    },
    /// A filter operator could not be applied (bad regex, bad operand, ...).
    Filter {
        /// Human-readable description.
        message: String,
    },
    /// A sort operation failed (e.g. values were not comparable).
    Sort {
        /// Human-readable description.
        message: String,
    },
    /// A search query was invalid.
    Search {
        /// Human-readable description.
        message: String,
    },
    /// An input value failed validation (out of range, mutually exclusive, ...).
    Validation {
        /// Human-readable description (surfaced verbatim to the host).
        message: String,
    },
}

impl fmt::Display for CoreError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidCursor { reason } => write!(f, "invalid cursor: {reason}"),
            Self::FieldNotFound { field } => write!(f, "field not found: {field}"),
            Self::Filter { message } => write!(f, "filter error: {message}"),
            Self::Sort { message } => write!(f, "sort error: {message}"),
            Self::Search { message } => write!(f, "search error: {message}"),
            // Validation messages are user-facing input feedback — surfaced verbatim.
            Self::Validation { message } => write!(f, "{message}"),
        }
    }
}

impl std::error::Error for CoreError {}

/// Convenience alias used throughout the crate.
pub type Result<T> = std::result::Result<T, CoreError>;
