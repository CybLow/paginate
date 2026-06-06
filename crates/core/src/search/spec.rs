//! The search request types shared by every search path in this module.
//!
//! Kept separate from the algorithms ([`super`] ranked scoring, [`super::index`]
//! inverted-index search, [`super::match_filter`] match-filtering) so each path
//! consumes one canonical [`SearchSpec`] and the enums have a single home.

use std::collections::BTreeMap;

use crate::error::{CoreError, Result};

/// How a token matches a field value.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[non_exhaustive]
pub enum SearchFieldMode {
    /// Token is a prefix of the value.
    Prefix,
    /// Token appears anywhere in the value.
    Contains,
    /// Token equals the value.
    Exact,
}

impl SearchFieldMode {
    /// Parse the wire token (`"prefix"` / `"contains"` / `"exact"`).
    ///
    /// # Errors
    /// [`CoreError::Search`] for any other token.
    pub fn from_token(token: &str) -> Result<Self> {
        match token {
            "prefix" => Ok(Self::Prefix),
            "contains" => Ok(Self::Contains),
            "exact" => Ok(Self::Exact),
            other => Err(CoreError::Search {
                message: format!("unknown search mode: {other}"),
            }),
        }
    }
}

/// Fuzzy matching strategy.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[non_exhaustive]
pub enum FuzzyMode {
    /// No fuzzing — mode-based matching only.
    Exact,
    /// Trigram similarity scoring.
    Fuzzy,
    /// Token-sorted trigram scoring (order-insensitive).
    TokenSort,
}

impl FuzzyMode {
    /// Parse the wire token (`"exact"` / `"fuzzy"` / `"token_sort"`).
    ///
    /// # Errors
    /// [`CoreError::Search`] for any other token.
    pub fn from_token(token: &str) -> Result<Self> {
        match token {
            "exact" => Ok(Self::Exact),
            "fuzzy" => Ok(Self::Fuzzy),
            "token_sort" => Ok(Self::TokenSort),
            other => Err(CoreError::Search {
                message: format!("unknown fuzzy mode: {other}"),
            }),
        }
    }
}

/// A search specification.
#[derive(Debug, Clone)]
pub struct SearchSpec {
    /// Raw query string.
    pub query: String,
    /// Fields to search (dotted paths).
    pub fields: Vec<String>,
    /// Optional per-field weights (default weight is 1.0).
    pub weights: Option<BTreeMap<String, f64>>,
    /// Exact/prefix/contains matching mode.
    pub mode: SearchFieldMode,
    /// Fuzzy strategy (Exact disables trigram scoring).
    pub fuzzy: FuzzyMode,
    /// Minimum trigram similarity (0-100) for a field to count as a match.
    pub threshold: i64,
    /// Minimum query length (in chars) before searching kicks in.
    pub min_length: usize,
    /// Optional cap on the number of ranked results.
    pub max_results: Option<usize>,
}
