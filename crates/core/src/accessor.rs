//! Dotted field-path resolution on [`Value`] maps — shared by filter, sort,
//! and search. Mirrors pypaginate's `filtering/accessor.py`: path segments must
//! not start with `_`, and lookups resolve through map items.

use crate::error::{CoreError, Result};
use crate::value::Value;

/// Split and validate a dotted path, rejecting segments that start with `_`.
///
/// # Errors
/// [`CoreError::Filter`] if any segment starts with `_` (the Python accessor
/// raises `FilterError` in that case, in all three engines).
pub(crate) fn compile_path(field: &str) -> Result<Vec<String>> {
    let segments: Vec<String> = field.split('.').map(str::to_owned).collect();
    for segment in &segments {
        if segment.starts_with('_') {
            return Err(CoreError::Filter {
                message: format!("Field path segment '{segment}' must not start with '_'"),
            });
        }
    }
    Ok(segments)
}

/// Strict resolution used by filtering: a missing segment or a non-map
/// container is an error.
///
/// # Errors
/// [`CoreError::FieldNotFound`] when a segment cannot be resolved.
pub(crate) fn resolve<'a>(item: &'a Value, path: &[String]) -> Result<&'a Value> {
    let mut current = item;
    for segment in path {
        current = match current {
            Value::Map(map) => map.get(segment).ok_or_else(|| CoreError::FieldNotFound {
                field: segment.clone(),
            })?,
            _ => {
                return Err(CoreError::FieldNotFound {
                    field: segment.clone(),
                })
            }
        };
    }
    Ok(current)
}

/// Lenient resolution used by sort/search: a missing segment, a non-map
/// container, or an explicit null all resolve to `None`. This mirrors the
/// Python engines, which catch the accessor error and treat the value as
/// absent (and which already treat `None` as a null for placement/skipping).
#[must_use]
pub(crate) fn resolve_opt<'a>(item: &'a Value, path: &[String]) -> Option<&'a Value> {
    let mut current = item;
    for segment in path {
        match current {
            Value::Map(map) => current = map.get(segment)?,
            _ => return None,
        }
    }
    if current.is_null() {
        None
    } else {
        Some(current)
    }
}
