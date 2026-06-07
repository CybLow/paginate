//! PyO3 bindings for the one-shot in-memory engines (filter / search / sort).
//!
//! Each item is **projected** to only the fields a spec references (see
//! [`project`]), so the FFI marshalling cost scales with fields-referenced
//! rather than record width; the engine returns indices and the Python caller
//! selects from its original objects. Filter wire-form parsing lives in
//! [`filter`]. These exist primarily to **measure** whether the native path
//! beats the pure-Python engines once marshalling is included — for a resident
//! dataset use [`crate::dataset::Dataset`].

mod filter;
mod project;

use std::collections::{BTreeMap, HashMap};

use pyo3::prelude::*;
use pyo3::types::{PyList, PyTuple};

use crate::conv::core_err;
use crate::specs as wire;
use ::paginate_core as core;
use core::filter::{FilterInput, FilterNode};
use core::search::SearchSpec;
use core::sort::SortSpec;

/// Return the indices of `items` matching the flat `(field, op, value, logic)`
/// specs. Items may be dicts or attribute objects.
#[pyfunction]
pub fn filter_indices(
    items: &Bound<'_, PyList>,
    specs: &Bound<'_, PyList>,
) -> PyResult<Vec<usize>> {
    let (core_specs, plan) = filter::parse_filter(specs)?;
    let values = project::project_all(items, &plan)?;
    let input = FilterInput::Flat(core_specs);
    core::filter::filter_indices(&values, &input).map_err(|e| core_err(&e))
}

/// Return the indices of `items` matching a nested filter `group`.
///
/// `group` is the recursive tuple form: a leaf is `(field, op, value, logic)`
/// and a group is `(logic, [node, ...])`. Mirrors the pure-Python
/// `FilterEngine`, which the flat [`filter_indices`] cannot express (it takes
/// only a single AND/OR level).
#[pyfunction]
pub fn filter_group_indices(
    items: &Bound<'_, PyList>,
    group: &Bound<'_, PyAny>,
) -> PyResult<Vec<usize>> {
    let mut plan: project::ProjectionPlan = Vec::new();
    let mut key_for: HashMap<String, String> = HashMap::new();
    let input = match filter::parse_node(group, &mut plan, &mut key_for)? {
        FilterNode::Group(group) => FilterInput::Group(group),
        FilterNode::Spec(spec) => FilterInput::Flat(vec![spec]),
    };
    // Enforce the nesting-depth guard, matching the Node binding (symmetry).
    core::validate::validate_filter_input(&input).map_err(|e| core_err(&e))?;
    let values = project::project_all(items, &plan)?;
    core::filter::filter_indices(&values, &input).map_err(|e| core_err(&e))
}

/// Rank item indices by relevance of `query` over `fields`, with optional
/// per-field `weights` (keyed by the original field names).
#[pyfunction]
#[pyo3(signature = (items, query, fields, mode="contains", fuzzy="exact", threshold=30, min_length=1, max_results=None, weights=None))]
#[allow(clippy::too_many_arguments)]
pub fn search_indices(
    items: &Bound<'_, PyList>,
    query: String,
    fields: Vec<String>,
    mode: &str,
    fuzzy: &str,
    threshold: i64,
    min_length: usize,
    max_results: Option<usize>,
    weights: Option<HashMap<String, f64>>,
) -> PyResult<Vec<usize>> {
    let plan = project::field_plan(&fields);
    // Re-key weights from the original field names to the synthetic `f{i}` keys.
    let core_weights = weights.map(|by_name| {
        fields
            .iter()
            .enumerate()
            .filter_map(|(i, field)| by_name.get(field).map(|&w| (format!("f{i}"), w)))
            .collect::<BTreeMap<String, f64>>()
    });
    let spec = SearchSpec {
        query,
        fields: (0..fields.len()).map(|i| format!("f{i}")).collect(),
        weights: core_weights,
        mode: wire::mode(mode)?,
        fuzzy: wire::fuzzy(fuzzy)?,
        threshold,
        min_length,
        max_results,
    };
    let values = project::project_all(items, &plan)?;
    core::search::search_indices(&values, &spec).map_err(|e| core_err(&e))
}

/// Return a permutation of item indices for `(field, direction, nulls)` specs.
#[pyfunction]
pub fn sort_indices(items: &Bound<'_, PyList>, specs: &Bound<'_, PyList>) -> PyResult<Vec<usize>> {
    let mut plan: project::ProjectionPlan = Vec::new();
    let mut key_for: HashMap<String, String> = HashMap::new();
    let mut core_specs = Vec::new();
    for spec in specs.iter() {
        let tuple = spec.cast::<PyTuple>()?;
        let field: String = tuple.get_item(0)?.extract()?;
        let direction: String = tuple.get_item(1)?.extract()?;
        let nulls: String = tuple.get_item(2)?.extract()?;
        let key = project::intern_field(&field, &mut plan, &mut key_for);
        core_specs.push(SortSpec {
            field: key,
            direction: wire::direction(&direction)?,
            nulls: wire::nulls(&nulls)?,
        });
    }
    let values = project::project_all(items, &plan)?;
    core::sort::sort_indices(&values, &core_specs).map_err(|e| core_err(&e))
}

/// Indices of items where any field matches the whole query — by `mode`
/// (contains/prefix/exact) when `fuzzy="exact"`, else by trigram score >=
/// `threshold` (`fuzzy="fuzzy"` / `"token_sort"`). Original order, unranked.
#[pyfunction]
#[pyo3(signature = (items, query, fields, mode="contains", fuzzy="exact", threshold=30))]
pub fn match_indices(
    items: &Bound<'_, PyList>,
    query: &str,
    fields: Vec<String>,
    mode: &str,
    fuzzy: &str,
    threshold: i64,
) -> PyResult<Vec<usize>> {
    let plan = project::field_plan(&fields);
    let synthetic: Vec<String> = (0..fields.len()).map(|i| format!("f{i}")).collect();
    let values = project::project_all(items, &plan)?;
    core::search::match_indices(
        &values,
        query,
        &synthetic,
        wire::mode(mode)?,
        wire::fuzzy(fuzzy)?,
        threshold,
    )
    .map_err(|e| core_err(&e))
}
