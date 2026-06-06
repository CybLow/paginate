//! Item projection: marshal only the fields a spec references into a
//! `Value::Map` under short synthetic keys, so the FFI cost scales with
//! fields-referenced rather than record width. Shared by every engine binding.

use std::collections::{BTreeMap, HashMap};

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

use crate::conv::py_to_value;
use ::paginate_core::Value;

/// (synthetic key, path segments) for each distinct referenced field.
pub(super) type ProjectionPlan = Vec<(String, Vec<String>)>;

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

/// Build a projected `Value::Map` holding only the referenced fields. An absent
/// field is omitted, so the core resolver errors on it (matching the Python
/// accessor, which raises on a missing field).
fn project_item(item: &Bound<'_, PyAny>, plan: &[(String, Vec<String>)]) -> PyResult<Value> {
    let mut map = BTreeMap::new();
    for (key, segments) in plan {
        if let Some(leaf) = resolve_py(item, segments) {
            map.insert(key.clone(), py_to_value(&leaf)?);
        }
    }
    Ok(Value::Map(map))
}

/// Project every item in `items` through `plan` into core `Value`s.
pub(super) fn project_all(
    items: &Bound<'_, PyList>,
    plan: &[(String, Vec<String>)],
) -> PyResult<Vec<Value>> {
    let mut values = Vec::with_capacity(items.len());
    for item in items.iter() {
        values.push(project_item(&item, plan)?);
    }
    Ok(values)
}

/// Intern a dotted field path to a short synthetic key (`f0`, `f1`, ...),
/// recording the path in `plan` the first time it is seen.
pub(super) fn intern_field(
    field: &str,
    plan: &mut ProjectionPlan,
    key_for: &mut HashMap<String, String>,
) -> String {
    key_for
        .entry(field.to_owned())
        .or_insert_with(|| {
            let synthetic = format!("f{}", plan.len());
            plan.push((
                synthetic.clone(),
                field.split('.').map(str::to_owned).collect(),
            ));
            synthetic
        })
        .clone()
}

/// A positional plan: field `i` → key `f{i}` (search / match, where the synthetic
/// keys line up with the spec's own field order).
pub(super) fn field_plan(fields: &[String]) -> ProjectionPlan {
    fields
        .iter()
        .enumerate()
        .map(|(i, field)| {
            (
                format!("f{i}"),
                field.split('.').map(str::to_owned).collect(),
            )
        })
        .collect()
}
