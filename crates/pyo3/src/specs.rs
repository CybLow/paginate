//! Shared string -> core-enum parsing for the spec tuples crossing the FFI
//! boundary. One place maps the Python-side names (`"or"`, `"desc"`, `"first"`,
//! `"prefix"`, `"fuzzy"`, ...) onto the core enums so the one-shot engines
//! ([`crate::engines`]) and the resident dataset ([`crate::dataset`]) cannot
//! drift in how they interpret a spec.

use ::paginate_core as core;
use core::filter::FilterLogic;
use core::search::{FuzzyMode, SearchFieldMode};
use core::sort::{NullsPosition, SortDirection};

/// `"or"` -> `Or`, anything else -> `And` (the spec default).
pub(crate) fn logic(name: &str) -> FilterLogic {
    if name == "or" {
        FilterLogic::Or
    } else {
        FilterLogic::And
    }
}

/// `"desc"` -> `Desc`, anything else -> `Asc` (the spec default).
pub(crate) fn direction(name: &str) -> SortDirection {
    if name == "desc" {
        SortDirection::Desc
    } else {
        SortDirection::Asc
    }
}

/// `"first"` -> `First`, anything else -> `Last` (the spec default).
pub(crate) fn nulls(name: &str) -> NullsPosition {
    if name == "first" {
        NullsPosition::First
    } else {
        NullsPosition::Last
    }
}

/// `"prefix"`/`"exact"` -> the matching mode, anything else -> `Contains`.
pub(crate) fn mode(name: &str) -> SearchFieldMode {
    match name {
        "prefix" => SearchFieldMode::Prefix,
        "exact" => SearchFieldMode::Exact,
        _ => SearchFieldMode::Contains,
    }
}

/// `"fuzzy"`/`"token_sort"` -> the fuzzy strategy, anything else -> `Exact`.
pub(crate) fn fuzzy(name: &str) -> FuzzyMode {
    match name {
        "fuzzy" => FuzzyMode::Fuzzy,
        "token_sort" => FuzzyMode::TokenSort,
        _ => FuzzyMode::Exact,
    }
}
