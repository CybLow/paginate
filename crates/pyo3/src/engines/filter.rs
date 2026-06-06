//! Parse the Python filter wire-forms — flat `(field, op, value, logic)` tuples
//! and the recursive nested-group form — into core filter specs, interning each
//! distinct field path into the shared [`ProjectionPlan`].

use std::collections::HashMap;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyList, PyTuple};

use crate::conv::py_to_value;
use crate::specs as wire;
use ::paginate_core::filter::{FilterGroup, FilterNode, FilterOp, FilterSpec};

use super::project::{intern_field, ProjectionPlan};

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
        logic: wire::logic(&logic_name)?,
    })
}

/// Parse flat `(field, op, value, logic)` tuples into core specs + a projection
/// plan (each distinct field path mapped to a short synthetic key like `f0`).
pub(super) fn parse_filter(
    specs: &Bound<'_, PyList>,
) -> PyResult<(Vec<FilterSpec>, ProjectionPlan)> {
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
pub(super) fn parse_node(
    node: &Bound<'_, PyAny>,
    plan: &mut ProjectionPlan,
    key_for: &mut HashMap<String, String>,
) -> PyResult<FilterNode> {
    let tuple = node.cast::<PyTuple>()?;
    match tuple.len() {
        4 => Ok(FilterNode::Spec(parse_leaf(tuple, plan, key_for)?)),
        2 => {
            let logic = wire::logic(&tuple.get_item(0)?.extract::<String>()?)?;
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
