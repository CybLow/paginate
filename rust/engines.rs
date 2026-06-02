//! PyO3 bindings for the in-memory engines (filter, ...).
//!
//! Each item is **projected** to only the fields a spec references, stored under
//! short synthetic keys, so the FFI marshalling cost scales with
//! fields-referenced rather than record width. The engine returns indices; the
//! Python caller selects from its original objects.
//!
//! This exists primarily to **measure** whether the native path beats the
//! already-optimized pure-Python engines once marshalling is included.

use std::collections::{BTreeMap, HashMap};

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyTuple};

use crate::conv::{core_err, py_to_value};
use ::paginate_core as core;
use core::filter::{FilterGroup, FilterInput, FilterLogic, FilterNode, FilterOp, FilterSpec};
use core::search::{FuzzyMode, SearchFieldMode, SearchSpec};
use core::sort::{NullsPosition, SortDirection, SortSpec};
use core::Value;

/// (synthetic key, path segments) for each distinct referenced field.
type ProjectionPlan = Vec<(String, Vec<String>)>;

/// Resolve a dotted path on a Python item (dict item access, else attribute).
fn resolve_py<'py>(item: &Bound<'py, PyAny>, segments: &[String]) -> Option<Bound<'py, PyAny>> {
    let mut current = item.clone();
    for segment in segments {
        let next = match current.cast::<PyDict>() {
            Ok(dict) => dict.get_item(segment.as_str()).ok().flatten(),
            Err(_) => current.getattr(segment.as_str()).ok(),
        };
        current = next?;
    }
    Some(current)
}

/// Build a projected `Value::Map` holding only the referenced fields.
fn project_item(item: &Bound<'_, PyAny>, plan: &[(String, Vec<String>)]) -> PyResult<Value> {
    let mut map = BTreeMap::new();
    for (key, segments) in plan {
        if let Some(leaf) = resolve_py(item, segments) {
            map.insert(key.clone(), py_to_value(&leaf)?);
        }
        // Absent: omit -> the core resolver errors (matching the Python filter
        // accessor, which raises on a missing field).
    }
    Ok(Value::Map(map))
}

/// Intern a dotted field path to a short synthetic projection key (`f0`, `f1`,
/// ...), recording the path in `plan` the first time it is seen.
fn intern_field(
    field: &str,
    plan: &mut ProjectionPlan,
    key_for: &mut HashMap<String, String>,
) -> String {
    key_for
        .entry(field.to_owned())
        .or_insert_with(|| {
            let synthetic = format!("f{}", plan.len());
            plan.push((synthetic.clone(), field.split('.').map(str::to_owned).collect()));
            synthetic
        })
        .clone()
}

fn parse_logic(name: &str) -> FilterLogic {
    if name == "or" {
        FilterLogic::Or
    } else {
        FilterLogic::And
    }
}

/// Parse one `(field, op, value, logic)` tuple into a core spec, interning its
/// field path into `plan`.
fn parse_leaf(
    tuple: &Bound<'_, PyTuple>,
    plan: &mut ProjectionPlan,
    key_for: &mut HashMap<String, String>,
) -> PyResult<FilterSpec> {
    let field: String = tuple.get_item(0)?.extract()?;
    let op_name: String = tuple.get_item(1)?.extract()?;
    let value = py_to_value(&tuple.get_item(2)?)?;
    let logic_name: String = tuple.get_item(3)?.extract()?;
    let op = FilterOp::from_name(&op_name)
        .ok_or_else(|| PyValueError::new_err(format!("unknown operator: {op_name}")))?;
    Ok(FilterSpec {
        field: intern_field(&field, plan, key_for),
        op,
        value,
        logic: parse_logic(&logic_name),
    })
}

/// Parse flat `(field, op, value, logic)` tuples into core specs + a projection
/// plan (each distinct field path mapped to a short synthetic key like `f0`).
fn parse_filter(specs: &Bound<'_, PyList>) -> PyResult<(Vec<FilterSpec>, ProjectionPlan)> {
    let mut plan: ProjectionPlan = Vec::new();
    let mut key_for: HashMap<String, String> = HashMap::new();
    let mut core_specs = Vec::new();
    for spec in specs.iter() {
        let tuple = spec.cast::<PyTuple>()?;
        core_specs.push(parse_leaf(tuple, &mut plan, &mut key_for)?);
    }
    Ok((core_specs, plan))
}

/// Parse a recursive filter node: a 4-tuple `(field, op, value, logic)` is a
/// leaf spec; a 2-tuple `(logic, [node, ...])` is a nested AND/OR group.
fn parse_node(
    node: &Bound<'_, PyAny>,
    plan: &mut ProjectionPlan,
    key_for: &mut HashMap<String, String>,
) -> PyResult<FilterNode> {
    let tuple = node.cast::<PyTuple>()?;
    match tuple.len() {
        4 => Ok(FilterNode::Spec(parse_leaf(tuple, plan, key_for)?)),
        2 => {
            let logic = parse_logic(&tuple.get_item(0)?.extract::<String>()?);
            let mut conditions = Vec::new();
            for child in tuple.get_item(1)?.try_iter()? {
                conditions.push(parse_node(&child?, plan, key_for)?);
            }
            Ok(FilterNode::Group(FilterGroup { logic, conditions }))
        }
        other => Err(PyValueError::new_err(format!(
            "filter node must be a 4-tuple (spec) or 2-tuple (group), got length {other}"
        ))),
    }
}

/// Return the indices of `items` matching the flat `(field, op, value, logic)`
/// specs. Items may be dicts or attribute objects.
#[pyfunction]
pub fn filter_indices(
    items: &Bound<'_, PyList>,
    specs: &Bound<'_, PyList>,
) -> PyResult<Vec<usize>> {
    let (core_specs, plan) = parse_filter(specs)?;
    let mut values = Vec::with_capacity(items.len());
    for item in items.iter() {
        values.push(project_item(&item, &plan)?);
    }
    let input = FilterInput::Flat(core_specs);
    core::filter::filter_indices(&values, &input).map_err(|e| core_err(&e))
}

/// Return the indices of `items` matching a nested filter `group`.
///
/// `group` is the recursive tuple form: a leaf is `(field, op, value, logic)`
/// and a group is `(logic, [node, ...])`. Mirrors the pure-Python
/// `FilterEngine`, which `_core` could not express before (the flat
/// [`filter_indices`] takes only a single AND/OR level).
#[pyfunction]
pub fn filter_group_indices(
    items: &Bound<'_, PyList>,
    group: &Bound<'_, PyAny>,
) -> PyResult<Vec<usize>> {
    let mut plan: ProjectionPlan = Vec::new();
    let mut key_for: HashMap<String, String> = HashMap::new();
    let input = match parse_node(group, &mut plan, &mut key_for)? {
        FilterNode::Group(group) => FilterInput::Group(group),
        FilterNode::Spec(spec) => FilterInput::Flat(vec![spec]),
    };
    let mut values = Vec::with_capacity(items.len());
    for item in items.iter() {
        values.push(project_item(&item, &plan)?);
    }
    core::filter::filter_indices(&values, &input).map_err(|e| core_err(&e))
}

// -- search ------------------------------------------------------------------

fn parse_mode(mode: &str) -> SearchFieldMode {
    match mode {
        "prefix" => SearchFieldMode::Prefix,
        "exact" => SearchFieldMode::Exact,
        _ => SearchFieldMode::Contains,
    }
}

fn parse_fuzzy(fuzzy: &str) -> FuzzyMode {
    match fuzzy {
        "fuzzy" => FuzzyMode::Fuzzy,
        "token_sort" => FuzzyMode::TokenSort,
        _ => FuzzyMode::Exact,
    }
}

/// Rank item indices by relevance of `query` over `fields` (equal weights).
#[pyfunction]
#[pyo3(signature = (items, query, fields, mode="contains", fuzzy="exact", threshold=75, min_length=1, max_results=None))]
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
) -> PyResult<Vec<usize>> {
    let plan: Vec<(String, Vec<String>)> = fields
        .iter()
        .enumerate()
        .map(|(i, field)| {
            (
                format!("f{i}"),
                field.split('.').map(str::to_owned).collect(),
            )
        })
        .collect();
    let spec = SearchSpec {
        query,
        fields: (0..fields.len()).map(|i| format!("f{i}")).collect(),
        weights: None,
        mode: parse_mode(mode),
        fuzzy: parse_fuzzy(fuzzy),
        threshold,
        min_length,
        max_results,
    };
    let mut values = Vec::with_capacity(items.len());
    for item in items.iter() {
        values.push(project_item(&item, &plan)?);
    }
    core::search::search_indices(&values, &spec).map_err(|e| core_err(&e))
}

// -- sort --------------------------------------------------------------------

/// Return a permutation of item indices for `(field, direction, nulls)` specs.
#[pyfunction]
pub fn sort_indices(items: &Bound<'_, PyList>, specs: &Bound<'_, PyList>) -> PyResult<Vec<usize>> {
    let mut plan: Vec<(String, Vec<String>)> = Vec::new();
    let mut key_for: HashMap<String, String> = HashMap::new();
    let mut core_specs = Vec::new();
    for spec in specs.iter() {
        let tuple = spec.cast::<PyTuple>()?;
        let field: String = tuple.get_item(0)?.extract()?;
        let direction: String = tuple.get_item(1)?.extract()?;
        let nulls: String = tuple.get_item(2)?.extract()?;
        let key = key_for
            .entry(field.clone())
            .or_insert_with(|| {
                let synthetic = format!("f{}", plan.len());
                plan.push((
                    synthetic.clone(),
                    field.split('.').map(str::to_owned).collect(),
                ));
                synthetic
            })
            .clone();
        core_specs.push(SortSpec {
            field: key,
            direction: if direction == "desc" {
                SortDirection::Desc
            } else {
                SortDirection::Asc
            },
            nulls: if nulls == "first" {
                NullsPosition::First
            } else {
                NullsPosition::Last
            },
        });
    }
    let mut values = Vec::with_capacity(items.len());
    for item in items.iter() {
        values.push(project_item(&item, &plan)?);
    }
    core::sort::sort_indices(&values, &core_specs).map_err(|e| core_err(&e))
}

// -- match-filter search (MemorySearchBackend semantics) ---------------------

/// Indices of items where any field contains/prefixes/equals the whole query.
#[pyfunction]
#[pyo3(signature = (items, query, fields, mode="contains"))]
pub fn match_indices(
    items: &Bound<'_, PyList>,
    query: &str,
    fields: Vec<String>,
    mode: &str,
) -> PyResult<Vec<usize>> {
    let plan: ProjectionPlan = fields
        .iter()
        .enumerate()
        .map(|(i, field)| {
            (
                format!("f{i}"),
                field.split('.').map(str::to_owned).collect(),
            )
        })
        .collect();
    let synthetic: Vec<String> = (0..fields.len()).map(|i| format!("f{i}")).collect();
    let mut values = Vec::with_capacity(items.len());
    for item in items.iter() {
        values.push(project_item(&item, &plan)?);
    }
    core::search::match_indices(&values, query, &synthetic, parse_mode(mode))
        .map_err(|e| core_err(&e))
}
