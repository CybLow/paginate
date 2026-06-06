//! The resident napi `Dataset` (marshal once, query many) and its page result.
//!
//! Unlike the one-shot functions in [`crate::engines`] — which re-marshal the
//! whole array across napi on every call and lose to V8 — the `Dataset`
//! marshals the rows into `core::Value` ONCE and answers many queries natively
//! (returning indices). This is the same "amortize the boundary" design as the
//! PyO3 `Dataset` and the only shape where crossing into Rust pays off for JS.
//! See `BENCHMARKS.md`.

use napi::bindgen_prelude::Result;
use napi_derive::napi;
use serde_json::Value as Json;

use crate::conv::{core_err, json_array_to_values, to_u32};
use crate::engines::{build_search_spec, parse_filter_specs, parse_search_stage, parse_sort_specs};
use ::paginate_core as core;

/// One page of results returned by [`Dataset::page`]. Numeric fields export as
/// JS `number`; `has_next`/`has_previous` as `hasNext`/`hasPrevious`.
#[napi(object)]
pub struct DatasetPage {
    /// Indices (into the original array) of this page's rows, in final order.
    pub indices: Vec<u32>,
    /// Total matched rows after filtering, before paging.
    pub total: i64,
    /// The requested page number.
    pub page: i64,
    /// Total number of pages.
    pub pages: i64,
    /// Whether a following page exists.
    pub has_next: bool,
    /// Whether a preceding page exists.
    pub has_previous: bool,
}

/// An in-memory dataset held in Rust as `core::Value` rows, queried by index.
/// Build it once from a JS array of objects, then call `filter`/`sort`/`search`/
/// `page`; each returns indices the caller maps back to its own objects.
#[napi]
pub struct Dataset {
    rows: Vec<core::Value>,
    columns: core::columnar::Columns,
    trigram: core::search::TrigramIndex,
}

#[napi]
impl Dataset {
    /// Marshal a JS array of objects into the resident dataset once, building the
    /// columnar fast-path data and the trigram search index.
    #[napi(constructor)]
    pub fn new(items: Json) -> Result<Self> {
        let rows = json_array_to_values(&items)?;
        let columns = core::columnar::Columns::build(&rows);
        let trigram = core::search::TrigramIndex::build(&rows);
        Ok(Self {
            rows,
            columns,
            trigram,
        })
    }

    /// Number of rows.
    #[napi(getter)]
    pub fn size(&self) -> u32 {
        self.rows.len() as u32
    }

    /// Indices matching flat filter specs `[{field, op, value, logic?}]`.
    #[napi]
    pub fn filter(&self, specs: Json) -> Result<Vec<u32>> {
        let core_specs = parse_filter_specs(&specs)?;
        if let [spec] = core_specs.as_slice() {
            if let Some(indices) = self.columns.filter(&spec.field, spec.op, &spec.value) {
                return Ok(to_u32(indices));
            }
        }
        let input = core::filter::FilterInput::Flat(core_specs);
        core::filter::filter_indices(&self.rows, &input)
            .map(to_u32)
            .map_err(|e| core_err(&e))
    }

    /// A permutation of row indices for sort specs `[{field, direction?, nulls?}]`.
    #[napi]
    pub fn sort(&self, specs: Json) -> Result<Vec<u32>> {
        let core_specs = parse_sort_specs(&specs)?;
        if !core_specs.is_empty() {
            let order: Vec<usize> = (0..self.rows.len()).collect();
            let keys: Vec<(&str, core::sort::SortDirection)> = core_specs
                .iter()
                .map(|spec| (spec.field.as_str(), spec.direction))
                .collect();
            if let Some(sorted) = self.columns.sort_subset(&order, &keys) {
                return Ok(to_u32(sorted));
            }
        }
        core::sort::sort_indices(&self.rows, &core_specs)
            .map(to_u32)
            .map_err(|e| core_err(&e))
    }

    /// Ranked-search indices over `fields`. Fuzzy/token-sort use the resident
    /// trigram index to score only candidate rows (exact result, far less work).
    #[napi]
    #[allow(clippy::too_many_arguments)]
    pub fn search(
        &self,
        query: String,
        fields: Vec<String>,
        mode: Option<String>,
        fuzzy: Option<String>,
        threshold: Option<i64>,
        min_length: Option<u32>,
        max_results: Option<u32>,
    ) -> Result<Vec<u32>> {
        let spec = build_search_spec(
            query,
            fields,
            mode,
            fuzzy,
            threshold,
            min_length,
            max_results,
        );
        core::search::search_with_index(&self.rows, &spec, &self.trigram)
            .map(to_u32)
            .map_err(|e| core_err(&e))
    }

    /// Filter + sort + offset-paginate in ONE native call. Returns the page's
    /// row indices + offset metadata; the caller selects its rows by index.
    #[napi]
    pub fn page(
        &self,
        page: u32,
        limit: u32,
        filters: Option<Json>,
        sorts: Option<Json>,
        search: Option<Json>,
    ) -> Result<DatasetPage> {
        let filter_input = match &filters {
            Some(specs) => {
                let parsed = parse_filter_specs(specs)?;
                (!parsed.is_empty()).then_some(core::filter::FilterInput::Flat(parsed))
            }
            None => None,
        };
        let sort_specs = match &sorts {
            Some(specs) => parse_sort_specs(specs)?,
            None => Vec::new(),
        };
        // Owned search parts (the SearchStage borrows them across the call).
        let search_parts = match &search {
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
        let result = core::pipeline::offset_page_searched(
            &self.rows,
            Some(&self.columns),
            filter_input.as_ref(),
            stage.as_ref(),
            &sort_specs,
            u64::from(page),
            u64::from(limit),
        )
        .map_err(|e| core_err(&e))?;
        Ok(DatasetPage {
            indices: to_u32(result.indices),
            total: result.total as i64,
            page: result.page as i64,
            pages: result.pages as i64,
            has_next: result.has_next,
            has_previous: result.has_previous,
        })
    }
}
