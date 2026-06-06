//! Adapt the core's string→enum parsers to Python errors at the FFI boundary.
//!
//! The canonical token↔enum mapping lives in `paginate-core` (each enum's
//! `from_token`), so the one-shot engines ([`crate::engines`]) and the resident
//! dataset ([`crate::dataset`]) share **one** parser with the napi binding and
//! the core itself — they cannot drift, and an unknown token fails fast instead
//! of silently defaulting. This module only maps the resulting [`core::CoreError`]
//! onto the corresponding Python exception.

use pyo3::PyResult;

use ::paginate_core as core;
use core::filter::FilterLogic;
use core::search::{FuzzyMode, SearchFieldMode};
use core::sort::{NullsPosition, SortDirection};

use crate::conv::core_err;

/// Parse a filter-logic token (`"and"` / `"or"`).
pub(crate) fn logic(name: &str) -> PyResult<FilterLogic> {
    FilterLogic::from_token(name).map_err(|e| core_err(&e))
}

/// Parse a sort-direction token (`"asc"` / `"desc"`).
pub(crate) fn direction(name: &str) -> PyResult<SortDirection> {
    SortDirection::from_token(name).map_err(|e| core_err(&e))
}

/// Parse a nulls-position token (`"first"` / `"last"`).
pub(crate) fn nulls(name: &str) -> PyResult<NullsPosition> {
    NullsPosition::from_token(name).map_err(|e| core_err(&e))
}

/// Parse a search-mode token (`"prefix"` / `"contains"` / `"exact"`).
pub(crate) fn mode(name: &str) -> PyResult<SearchFieldMode> {
    SearchFieldMode::from_token(name).map_err(|e| core_err(&e))
}

/// Parse a fuzzy-mode token (`"exact"` / `"fuzzy"` / `"token_sort"`).
pub(crate) fn fuzzy(name: &str) -> PyResult<FuzzyMode> {
    FuzzyMode::from_token(name).map_err(|e| core_err(&e))
}
