//! PyO3 bindings compiled into pypaginate as the `pypaginate._core` extension.
//!
//! The binding layer's only job is marshalling: convert host (Python) values to
//! the shared `paginate-core` engine's plain `Value` model, call the pure
//! engine, and convert results back. The filter/sort/search entry points return
//! **indices** so Python can select from its original objects without
//! round-tripping them through Rust.
use pyo3::prelude::*;
use pyo3::types::PyTuple;

// The shared engine crate (`paginate-core`, lib name `paginate_core`).
use ::paginate_core as core;

mod conv;
mod dataset;
mod engines;
mod specs;

// -- cursor codec ------------------------------------------------------------

/// Encode a sequence of ordering values into a URL-safe cursor string.
#[pyfunction]
fn encode_cursor(values: &Bound<'_, PyAny>) -> PyResult<String> {
    let mut decoded = Vec::new();
    for value in values.try_iter()? {
        decoded.push(conv::py_to_value(&value?)?);
    }
    Ok(core::cursor::encode_cursor(&decoded))
}

/// Decode a cursor string back into a tuple of ordering values.
#[pyfunction]
fn decode_cursor<'py>(py: Python<'py>, cursor: &str) -> PyResult<Bound<'py, PyTuple>> {
    let values = core::cursor::decode_cursor(cursor).map_err(|e| conv::core_err(&e))?;
    let objects: Vec<Py<PyAny>> = values
        .iter()
        .map(|v| conv::value_to_py(py, v))
        .collect::<PyResult<_>>()?;
    PyTuple::new(py, objects)
}

// -- text --------------------------------------------------------------------

/// Normalize text for search/filtering (ASCII fast path + NFKD accent strip).
#[pyfunction]
fn normalize_text(value: &str) -> String {
    core::normalize_text(value)
}

// -- pagination math ---------------------------------------------------------

/// Zero-based row offset for `(page, limit)`.
#[pyfunction]
fn offset(page: u64, limit: u64) -> u64 {
    core::pagination::offset(page, limit)
}

/// Total page count for `total` rows at `limit` per page.
#[pyfunction]
fn max_pages(total: u64, limit: u64) -> u64 {
    core::pagination::max_pages(total, limit)
}

/// Page metadata as `(page, pages, has_next, has_previous)`.
#[pyfunction]
fn offset_meta(page: u64, limit: u64, total: u64) -> (u64, u64, bool, bool) {
    let meta = core::pagination::offset_meta(page, limit, total);
    (meta.page, meta.pages, meta.has_next, meta.has_previous)
}

/// Clamp `page` into the valid `[1, max_page]` range.
#[pyfunction]
fn clamp_page(page: u64, limit: u64, total: u64) -> u64 {
    core::pagination::clamp_page(page, limit, total)
}

#[pymodule]
fn _core(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add("__version__", env!("CARGO_PKG_VERSION"))?;
    let py = module.py();
    module.add("PaginateError", py.get_type::<conv::PaginateError>())?;
    module.add(
        "InvalidCursorError",
        py.get_type::<conv::InvalidCursorError>(),
    )?;
    module.add("FilterError", py.get_type::<conv::FilterError>())?;
    module.add("SortError", py.get_type::<conv::SortError>())?;
    module.add("SearchError", py.get_type::<conv::SearchError>())?;
    module.add_function(wrap_pyfunction!(encode_cursor, module)?)?;
    module.add_function(wrap_pyfunction!(decode_cursor, module)?)?;
    module.add_function(wrap_pyfunction!(normalize_text, module)?)?;
    module.add_function(wrap_pyfunction!(offset, module)?)?;
    module.add_function(wrap_pyfunction!(max_pages, module)?)?;
    module.add_function(wrap_pyfunction!(offset_meta, module)?)?;
    module.add_function(wrap_pyfunction!(clamp_page, module)?)?;
    module.add_function(wrap_pyfunction!(engines::filter_indices, module)?)?;
    module.add_function(wrap_pyfunction!(engines::filter_group_indices, module)?)?;
    module.add_function(wrap_pyfunction!(engines::search_indices, module)?)?;
    module.add_function(wrap_pyfunction!(engines::sort_indices, module)?)?;
    module.add_function(wrap_pyfunction!(engines::match_indices, module)?)?;
    module.add_class::<dataset::Dataset>()?;
    Ok(())
}
