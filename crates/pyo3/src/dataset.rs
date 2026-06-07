//! A Rust-resident dataset: marshal host rows into `Value` **once**, then run
//! many filter/sort/search queries natively without re-crossing the FFI per
//! query.
//!
//! This is the architecture where Rust's compute advantage actually shows. The
//! one-shot bindings in `engines.rs` re-marshal every item on every call — which
//! the benchmark showed loses to JIT'd hosts, because marshalling dominates the
//! tiny per-item work. Here the marshalling is paid once and amortized across
//! queries, so for a stable in-memory dataset served by many paginated /
//! filtered requests, native wins — and wins more with every query.
//!
//! Methods return **indices** into the original list, so the caller selects its
//! own host objects and they never round-trip back through Rust.

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyTuple};

use crate::conv::{core_err, py_to_value};
use crate::specs as wire;
use ::paginate_core as core;

/// An in-memory dataset held in Rust as `Value` rows, queried by index.
#[pyclass(frozen, module = "paginate_core")]
pub struct Dataset {
    rows: Vec<core::Value>,
    columns: core::columnar::Columns,
    trigram: core::search::TrigramIndex,
}

#[pymethods]
impl Dataset {
    /// Marshal a list of items (dicts/objects) into the resident dataset once,
    /// building the columnar fast-path data and the trigram search index.
    #[new]
    fn new(items: &Bound<'_, PyList>) -> PyResult<Self> {
        let mut rows = Vec::with_capacity(items.len());
        for item in items.iter() {
            rows.push(py_to_value(&item)?);
        }
        let columns = core::columnar::Columns::build(&rows);
        let trigram = core::search::TrigramIndex::build(&rows);
        Ok(Self {
            rows,
            columns,
            trigram,
        })
    }

    /// Number of rows.
    fn __len__(&self) -> usize {
        self.rows.len()
    }

    /// `Dataset(rows=N)`.
    fn __repr__(&self) -> String {
        format!("Dataset(rows={})", self.rows.len())
    }

    /// Indices matching flat filter specs `[(field, op, value, logic)]`.
    fn filter(&self, py: Python<'_>, specs: &Bound<'_, PyList>) -> PyResult<Vec<usize>> {
        let core_specs = parse_filters(specs)?;
        let (rows, columns) = (&self.rows, &self.columns);
        // Release the GIL for the pure-Rust compute: frees other Python threads
        // and lets the free-threaded interpreter run queries in parallel.
        py.detach(|| {
            // Columnar fast path: a single comparison on a typed (int/float/str)
            // column; falls back to the row engine for anything else.
            if let [spec] = core_specs.as_slice() {
                if let Some(indices) = columns.filter(&spec.field, spec.op, &spec.value) {
                    return Ok(indices);
                }
            }
            core::filter::filter_indices(rows, &core::filter::FilterInput::Flat(core_specs))
        })
        .map_err(|e| core_err(&e))
    }

    /// Index permutation for sort specs `[(field, direction, nulls)]`.
    fn sort(&self, py: Python<'_>, specs: &Bound<'_, PyList>) -> PyResult<Vec<usize>> {
        let core_specs = parse_sorts(specs)?;
        let (rows, columns) = (&self.rows, &self.columns);
        py.detach(|| {
            // Columnar fast path: every sort key on a typed column.
            if !core_specs.is_empty() {
                let order: Vec<usize> = (0..rows.len()).collect();
                let keys: Vec<(&str, core::sort::SortDirection)> = core_specs
                    .iter()
                    .map(|spec| (spec.field.as_str(), spec.direction))
                    .collect();
                if let Some(sorted) = columns.sort_subset(&order, &keys) {
                    return Ok(sorted);
                }
            }
            core::sort::sort_indices(rows, &core_specs)
        })
        .map_err(|e| core_err(&e))
    }

    /// Ranked-search indices over `fields`. Fuzzy/token-sort use the resident
    /// trigram index to score only candidate rows (exact result, far less work).
    #[pyo3(signature = (query, fields, mode="contains", fuzzy="exact", threshold=30, min_length=1, max_results=None))]
    #[allow(clippy::too_many_arguments)]
    fn search(
        &self,
        py: Python<'_>,
        query: String,
        fields: Vec<String>,
        mode: &str,
        fuzzy: &str,
        threshold: i64,
        min_length: usize,
        max_results: Option<usize>,
    ) -> PyResult<Vec<usize>> {
        let spec = core::search::SearchSpec {
            query,
            fields,
            weights: None,
            mode: wire::mode(mode)?,
            fuzzy: wire::fuzzy(fuzzy)?,
            threshold,
            min_length,
            max_results,
        };
        let (rows, trigram) = (&self.rows, &self.trigram);
        py.detach(|| core::search::search_with_index(rows, &spec, trigram)).map_err(|e| core_err(&e))
    }

    /// Filter + search + sort + offset-paginate in ONE native call. Returns a dict
    /// `{indices, total, page, pages, has_next, has_previous}`; the caller
    /// selects its rows by the returned indices — so the host stays a thin
    /// adapter and a page request is a single FFI crossing.
    #[pyo3(signature = (page, limit, filters=None, sorts=None, search=None))]
    fn page<'py>(
        &self,
        py: Python<'py>,
        page: u64,
        limit: u64,
        filters: Option<&Bound<'py, PyList>>,
        sorts: Option<&Bound<'py, PyList>>,
        search: Option<&Bound<'py, PyTuple>>,
    ) -> PyResult<Bound<'py, PyDict>> {
        let filter_input = match filters {
            Some(specs) if !specs.is_empty() => {
                Some(core::filter::FilterInput::Flat(parse_filters(specs)?))
            }
            _ => None,
        };
        let sort_specs = match sorts {
            Some(specs) => parse_sorts(specs)?,
            None => Vec::new(),
        };
        // Owned search parts (the SearchStage borrows them across the call).
        let search_parts = match search {
            Some(spec) => Some(parse_search_stage(spec)?),
            None => None,
        };
        let stage = search_parts
            .as_ref()
            .map(
                |(query, fields, mode, fuzzy, threshold)| core::pipeline::SearchStage {
                    query,
                    fields,
                    mode: *mode,
                    fuzzy: *fuzzy,
                    threshold: *threshold,
                    index: Some(&self.trigram),
                },
            );
        let result = py
            .detach(|| {
                core::pipeline::offset_page_searched(
                    &self.rows,
                    Some(&self.columns),
                    filter_input.as_ref(),
                    stage.as_ref(),
                    &sort_specs,
                    page,
                    limit,
                )
            })
            .map_err(|e| core_err(&e))?;

        let dict = PyDict::new(py);
        dict.set_item("indices", result.indices)?;
        dict.set_item("total", result.total)?;
        dict.set_item("page", result.page)?;
        dict.set_item("pages", result.pages)?;
        dict.set_item("has_next", result.has_next)?;
        dict.set_item("has_previous", result.has_previous)?;
        Ok(dict)
    }
}

fn parse_filters(specs: &Bound<'_, PyList>) -> PyResult<Vec<core::filter::FilterSpec>> {
    let mut out = Vec::with_capacity(specs.len());
    for spec in specs.iter() {
        let tuple = spec.cast::<PyTuple>()?;
        let op_name: String = tuple.get_item(1)?.extract()?;
        let op = core::filter::FilterOp::from_name(&op_name)
            .ok_or_else(|| PyValueError::new_err(format!("unknown operator: {op_name}")))?;
        out.push(core::filter::FilterSpec {
            field: tuple.get_item(0)?.extract()?,
            op,
            value: py_to_value(&tuple.get_item(2)?)?,
            logic: wire::logic(&tuple.get_item(3)?.extract::<String>()?)?,
        });
    }
    Ok(out)
}

fn parse_sorts(specs: &Bound<'_, PyList>) -> PyResult<Vec<core::sort::SortSpec>> {
    let mut out = Vec::with_capacity(specs.len());
    for spec in specs.iter() {
        let tuple = spec.cast::<PyTuple>()?;
        out.push(core::sort::SortSpec {
            field: tuple.get_item(0)?.extract()?,
            direction: wire::direction(&tuple.get_item(1)?.extract::<String>()?)?,
            nulls: wire::nulls(&tuple.get_item(2)?.extract::<String>()?)?,
        });
    }
    Ok(out)
}

/// Owned parts of a search stage tuple `(query, fields, mode, fuzzy, threshold)`.
type SearchStageParts = (
    String,
    Vec<String>,
    core::search::SearchFieldMode,
    core::search::FuzzyMode,
    i64,
);

/// Parse the `(query, fields, mode, fuzzy, threshold)` search tuple.
fn parse_search_stage(spec: &Bound<'_, PyTuple>) -> PyResult<SearchStageParts> {
    Ok((
        spec.get_item(0)?.extract()?,
        spec.get_item(1)?.extract()?,
        wire::mode(&spec.get_item(2)?.extract::<String>()?)?,
        wire::fuzzy(&spec.get_item(3)?.extract::<String>()?)?,
        spec.get_item(4)?.extract()?,
    ))
}
