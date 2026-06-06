//! Marshalling between Python objects and the core [`Value`] model.
//!
//! `py_to_value` mirrors the Python cursor codec's type handling (datetime,
//! date, Decimal, UUID get their typed variants); `value_to_py` reconstructs
//! the rich host types on the way back. The typed-scalar checks only run for
//! non-scalar inputs — plain int/str/float/bool short-circuit first — so the
//! per-call `import` (a `sys.modules` hit after the first) stays off the hot
//! path for the common case.

use std::collections::BTreeMap;

use pyo3::create_exception;
use pyo3::exceptions::{PyKeyError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBool, PyBytes, PyDict, PyFloat, PyInt, PyList, PyString, PyTuple};
use pyo3::IntoPyObjectExt;

use paginate_core::{CoreError, Value};

// Typed exceptions exposed to Python. `PaginateError` subclasses `ValueError`,
// so existing `except ValueError` handlers keep working while callers gain
// precise, catchable types.
create_exception!(paginate_core, PaginateError, PyValueError);
create_exception!(paginate_core, InvalidCursorError, PaginateError);
create_exception!(paginate_core, FilterError, PaginateError);
create_exception!(paginate_core, SortError, PaginateError);
create_exception!(paginate_core, SearchError, PaginateError);

fn py_type<'py>(py: Python<'py>, module: &str, name: &str) -> PyResult<Bound<'py, PyAny>> {
    py.import(module)?.getattr(name)
}

/// Convert a Python object into a core [`Value`].
pub fn py_to_value(obj: &Bound<'_, PyAny>) -> PyResult<Value> {
    if obj.is_none() {
        return Ok(Value::Null);
    }
    // bool before int (bool is a subclass of int in Python).
    if obj.is_instance_of::<PyBool>() {
        return Ok(Value::Bool(obj.extract()?));
    }
    if obj.is_instance_of::<PyInt>() {
        return match obj.extract::<i64>() {
            Ok(value) => Ok(Value::Int(value)),
            // Out of i64 range: fall back to a string, like the codec's catch-all.
            Err(_) => Ok(Value::Str(obj.str()?.extract()?)),
        };
    }
    if obj.is_instance_of::<PyFloat>() {
        return Ok(Value::Float(obj.extract()?));
    }
    if obj.is_instance_of::<PyString>() {
        return Ok(Value::Str(obj.extract()?));
    }
    if let Ok(bytes) = obj.cast::<PyBytes>() {
        return Ok(Value::Bytes(bytes.as_bytes().to_vec()));
    }

    let py = obj.py();
    // datetime before date — datetime is a subclass of date.
    if obj.is_instance(&py_type(py, "datetime", "datetime")?)? {
        return Ok(Value::DateTime(obj.call_method0("isoformat")?.extract()?));
    }
    if obj.is_instance(&py_type(py, "datetime", "date")?)? {
        return Ok(Value::Date(obj.call_method0("isoformat")?.extract()?));
    }
    if obj.is_instance(&py_type(py, "decimal", "Decimal")?)? {
        return Ok(Value::Decimal(obj.str()?.extract()?));
    }
    if obj.is_instance(&py_type(py, "uuid", "UUID")?)? {
        return Ok(Value::Uuid(obj.str()?.extract()?));
    }

    if let Ok(list) = obj.cast::<PyList>() {
        return Ok(Value::List(
            list.iter()
                .map(|x| py_to_value(&x))
                .collect::<PyResult<_>>()?,
        ));
    }
    if let Ok(tuple) = obj.cast::<PyTuple>() {
        return Ok(Value::List(
            tuple
                .iter()
                .map(|x| py_to_value(&x))
                .collect::<PyResult<_>>()?,
        ));
    }
    if let Ok(dict) = obj.cast::<PyDict>() {
        let mut map = BTreeMap::new();
        for (key, value) in dict.iter() {
            let key = key
                .extract::<String>()
                .or_else(|_| key.str()?.extract::<String>())?;
            map.insert(key, py_to_value(&value)?);
        }
        return Ok(Value::Map(map));
    }
    // Catch-all: stringify, mirroring the Python codec's `str(value)` fallback.
    Ok(Value::Str(obj.str()?.extract()?))
}

/// Convert a core [`Value`] back into a Python object, reconstructing the rich
/// host types (datetime/date/Decimal/UUID) from their typed variants.
pub fn value_to_py(py: Python<'_>, value: &Value) -> PyResult<Py<PyAny>> {
    Ok(match value {
        Value::Null => py.None(),
        Value::Bool(b) => b.into_py_any(py)?,
        Value::Int(i) => i.into_py_any(py)?,
        Value::Float(f) => f.into_py_any(py)?,
        Value::Str(s) => s.into_py_any(py)?,
        Value::Bytes(b) => PyBytes::new(py, b).into_py_any(py)?,
        Value::List(items) => {
            let list = PyList::empty(py);
            for item in items {
                list.append(value_to_py(py, item)?)?;
            }
            list.into_py_any(py)?
        }
        Value::Map(map) => {
            let dict = PyDict::new(py);
            for (key, item) in map {
                dict.set_item(key, value_to_py(py, item)?)?;
            }
            dict.into_py_any(py)?
        }
        Value::DateTime(s) => py_type(py, "datetime", "datetime")?
            .call_method1("fromisoformat", (s,))?
            .unbind(),
        Value::Date(s) => py_type(py, "datetime", "date")?
            .call_method1("fromisoformat", (s,))?
            .unbind(),
        Value::Decimal(s) => py_type(py, "decimal", "Decimal")?.call1((s,))?.unbind(),
        Value::Uuid(s) => py_type(py, "uuid", "UUID")?.call1((s,))?.unbind(),
    })
}

/// Map a core error onto its typed Python exception. `FieldNotFound` stays a
/// `KeyError`; the rest become `PaginateError` subclasses (themselves
/// `ValueError`s, so existing handlers keep catching them).
pub fn core_err(err: &CoreError) -> PyErr {
    let message = err.to_string();
    match err {
        CoreError::FieldNotFound { .. } => PyKeyError::new_err(message),
        CoreError::InvalidCursor { .. } => InvalidCursorError::new_err(message),
        CoreError::Filter { .. } => FilterError::new_err(message),
        CoreError::Sort { .. } => SortError::new_err(message),
        CoreError::Search { .. } => SearchError::new_err(message),
        // Input validation surfaces as a plain ValueError; the Python params
        // layer re-raises it as the public `ValidationError`.
        CoreError::Validation { .. } => PyValueError::new_err(message),
        // `CoreError` is `#[non_exhaustive]`; a future variant maps to the base.
        _ => PaginateError::new_err(message),
    }
}
