//! Filter data model — operators, the single-condition spec, and the
//! flat-list / nested-group input tree. Pure type definitions; the evaluation
//! engine that consumes them lives in [`super`].

use crate::error::{CoreError, Result};
use crate::value::Value;

/// Logical combinator for filter conditions.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[non_exhaustive]
pub enum FilterLogic {
    /// All conditions must match.
    And,
    /// Any condition may match.
    Or,
}

impl FilterLogic {
    /// Parse the wire token (`"and"` / `"or"`) shared by every binding.
    ///
    /// # Errors
    /// [`CoreError::Filter`] for any other token (fail fast on a typo at the
    /// boundary rather than silently defaulting).
    pub fn from_token(token: &str) -> Result<Self> {
        match token {
            "and" => Ok(Self::And),
            "or" => Ok(Self::Or),
            other => Err(CoreError::Filter {
                message: format!("unknown filter logic: {other}"),
            }),
        }
    }
}

/// One of the 20 supported filter operators.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[non_exhaustive]
pub enum FilterOp {
    /// Equal (`==`).
    Eq,
    /// Not equal (`!=`).
    Ne,
    /// Greater than (`>`).
    Gt,
    /// Greater than or equal (`>=`).
    Gte,
    /// Less than (`<`).
    Lt,
    /// Less than or equal (`<=`).
    Lte,
    /// Membership in a list.
    In,
    /// Non-membership in a list.
    NotIn,
    /// Substring containment.
    Contains,
    /// String prefix.
    StartsWith,
    /// String suffix.
    EndsWith,
    /// SQL-style LIKE (case-sensitive).
    Like,
    /// SQL-style LIKE (case-insensitive).
    ILike,
    /// Inclusive range `[lo, hi]`.
    Between,
    /// Value is null/absent.
    IsNull,
    /// Value is present.
    IsNotNull,
    /// Regular-expression match.
    Regex,
    /// Empty string/collection.
    Empty,
    /// Non-empty string/collection.
    NotEmpty,
    /// Field/key exists.
    Exists,
}

impl FilterOp {
    /// Parse the Python operator name (e.g. `"not_in"`, `"starts_with"`).
    #[must_use]
    pub fn from_name(name: &str) -> Option<Self> {
        Some(match name {
            "eq" => Self::Eq,
            "ne" => Self::Ne,
            "gt" => Self::Gt,
            "gte" => Self::Gte,
            "lt" => Self::Lt,
            "lte" => Self::Lte,
            "in" => Self::In,
            "not_in" => Self::NotIn,
            "contains" => Self::Contains,
            "starts_with" => Self::StartsWith,
            "ends_with" => Self::EndsWith,
            "like" => Self::Like,
            "ilike" => Self::ILike,
            "between" => Self::Between,
            "is_null" => Self::IsNull,
            "is_not_null" => Self::IsNotNull,
            "regex" => Self::Regex,
            "empty" => Self::Empty,
            "not_empty" => Self::NotEmpty,
            "exists" => Self::Exists,
            _ => return None,
        })
    }
}

/// A single filter condition.
#[derive(Debug, Clone)]
pub struct FilterSpec {
    /// Dotted field path (e.g. `"user.age"`).
    pub field: String,
    /// Operator to apply.
    pub op: FilterOp,
    /// Comparison value (meaning depends on the operator).
    pub value: Value,
    /// Whether this spec joins others with AND or OR (flat-list mode).
    pub logic: FilterLogic,
}

/// A node in a nested filter tree.
#[derive(Debug, Clone)]
pub enum FilterNode {
    /// A leaf condition.
    Spec(FilterSpec),
    /// A nested group.
    Group(FilterGroup),
}

/// A composite AND/OR group of conditions.
#[derive(Debug, Clone)]
pub struct FilterGroup {
    /// How the child conditions combine.
    pub logic: FilterLogic,
    /// Child conditions (specs or nested groups).
    pub conditions: Vec<FilterNode>,
}

/// Filter input: either a flat spec list or a nested group.
#[derive(Debug, Clone)]
pub enum FilterInput {
    /// Flat list combined via each spec's `logic`.
    Flat(Vec<FilterSpec>),
    /// Nested AND/OR tree.
    Group(FilterGroup),
}
