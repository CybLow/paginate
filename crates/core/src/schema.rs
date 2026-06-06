//! Wire-form DTOs + JSON Schema export — the cross-language type contract.
//!
//! Behind the `schema` feature so the default engine build carries no schemars
//! dependency. These types mirror the exact **wire shapes** the bindings
//! exchange (operator *names*, `value` as arbitrary JSON), independent of the
//! engine's internal types. `cargo test -p paginate-core --features schema
//! export_schema` writes `schemas/paginate.schema.json` — the single source of
//! truth from which the Python (dataclasses / Pydantic) and TS types are
//! generated.

use schemars::JsonSchema;

/// Logical combinator for filter conditions.
#[derive(JsonSchema)]
#[schemars(rename_all = "snake_case")]
pub enum FilterLogic {
    /// All conditions must match.
    And,
    /// Any condition may match.
    Or,
}

/// One of the 20 supported filter operators (wire names).
#[derive(JsonSchema)]
#[schemars(rename_all = "snake_case")]
pub enum FilterOperator {
    /// `==`
    Eq,
    /// `!=`
    Ne,
    /// `>`
    Gt,
    /// `>=`
    Gte,
    /// `<`
    Lt,
    /// `<=`
    Lte,
    /// membership in a list
    In,
    /// non-membership in a list
    NotIn,
    /// substring containment
    Contains,
    /// string prefix
    StartsWith,
    /// string suffix
    EndsWith,
    /// SQL-style LIKE (case-sensitive)
    Like,
    /// SQL-style LIKE (case-insensitive)
    #[schemars(rename = "ilike")]
    ILike,
    /// inclusive range `[lo, hi]`
    Between,
    /// value is null/absent
    IsNull,
    /// value is present
    IsNotNull,
    /// regular-expression match
    Regex,
    /// empty string/collection
    Empty,
    /// non-empty string/collection
    NotEmpty,
    /// field/key exists
    Exists,
}

/// How a search token matches a field value.
#[derive(JsonSchema)]
#[schemars(rename_all = "snake_case")]
pub enum SearchFieldMode {
    /// Token is a prefix of the value.
    Prefix,
    /// Token appears anywhere in the value.
    Contains,
    /// Token equals the value.
    Exact,
}

/// Fuzzy matching strategy.
#[derive(JsonSchema)]
#[schemars(rename_all = "snake_case")]
pub enum FuzzyMode {
    /// No fuzzing (mode-based matching only).
    Exact,
    /// Trigram similarity scoring.
    Fuzzy,
    /// Token-sorted trigram scoring (order-insensitive).
    TokenSort,
}

/// Sort direction.
#[derive(JsonSchema)]
#[schemars(rename_all = "snake_case")]
pub enum SortDirection {
    /// Ascending.
    Asc,
    /// Descending.
    Desc,
}

/// Null placement relative to non-null values.
#[derive(JsonSchema)]
#[schemars(rename_all = "snake_case")]
pub enum NullsPosition {
    /// Nulls sort before non-nulls.
    First,
    /// Nulls sort after non-nulls.
    Last,
}

/// A single filter condition.
#[derive(JsonSchema)]
pub struct FilterSpec {
    /// Dotted field path (e.g. `user.age`).
    pub field: String,
    /// Operator to apply.
    pub operator: FilterOperator,
    /// Comparison value (meaning depends on the operator).
    pub value: serde_json::Value,
    /// AND/OR join in flat-list mode (default `and`).
    pub logic: Option<FilterLogic>,
}

/// A node in a nested filter tree: a leaf spec or a nested group.
#[derive(JsonSchema)]
#[schemars(untagged)]
pub enum FilterNode {
    /// A leaf condition.
    Spec(FilterSpec),
    /// A nested group.
    Group(FilterGroup),
}

/// A composite AND/OR group of conditions (recursively nestable).
#[derive(JsonSchema)]
pub struct FilterGroup {
    /// How the child conditions combine.
    pub logic: FilterLogic,
    /// Child conditions (specs or nested groups).
    pub conditions: Vec<FilterNode>,
}

/// A single sort key.
#[derive(JsonSchema)]
pub struct SortSpec {
    /// Dotted field path.
    pub field: String,
    /// Direction (default `asc`).
    pub direction: Option<SortDirection>,
    /// Null placement (default `last`).
    pub nulls: Option<NullsPosition>,
}

/// A search specification.
#[derive(JsonSchema)]
pub struct SearchSpec {
    /// Raw query string.
    pub query: String,
    /// Fields to search (dotted paths).
    pub fields: Vec<String>,
    /// Match mode (default `contains`).
    pub mode: Option<SearchFieldMode>,
    /// Fuzzy strategy (default `exact`).
    pub fuzzy: Option<FuzzyMode>,
    /// Minimum trigram similarity, 0-100 (default 30).
    pub threshold: Option<i64>,
    /// Minimum query length before searching kicks in (default 1).
    pub min_length: Option<i64>,
    /// Optional cap on the number of ranked results.
    pub max_results: Option<i64>,
    /// Optional per-field weights (default weight 1.0).
    pub weights: Option<std::collections::BTreeMap<String, f64>>,
}

/// Offset pagination parameters.
#[derive(JsonSchema)]
pub struct OffsetParams {
    /// 1-based page number.
    pub page: i64,
    /// Page size.
    pub limit: i64,
}

/// Cursor pagination parameters.
#[derive(JsonSchema)]
pub struct CursorParams {
    /// Page size.
    pub limit: i64,
    /// Opaque cursor to page forward from.
    pub after: Option<String>,
    /// Opaque cursor to page backward from.
    pub before: Option<String>,
}

/// Offset page metadata (the page minus its items).
#[derive(JsonSchema)]
pub struct OffsetPageMeta {
    /// Total matching rows across all pages.
    pub total: i64,
    /// The (possibly clamped) 1-based page number.
    pub page: i64,
    /// Total number of pages.
    pub pages: i64,
    /// Page size.
    pub limit: i64,
    /// Whether a following page exists.
    pub has_next: bool,
    /// Whether a preceding page exists.
    pub has_previous: bool,
}

/// Cursor page metadata (the page minus its items).
#[derive(JsonSchema)]
pub struct CursorPageMeta {
    /// Page size.
    pub limit: i64,
    /// Whether a following page exists.
    pub has_next: bool,
    /// Whether a preceding page exists.
    pub has_previous: bool,
    /// Cursor to fetch the next page (null if none).
    pub next_cursor: Option<String>,
    /// Cursor to fetch the previous page (null if none).
    pub previous_cursor: Option<String>,
}

#[cfg(test)]
mod export {
    use super::{
        CursorPageMeta, CursorParams, FilterGroup, FilterSpec, OffsetPageMeta, OffsetParams,
        SearchSpec, SortSpec,
    };
    use schemars::SchemaGenerator;

    /// Write the canonical JSON Schema — a `$defs`-only document of every wire
    /// type (no aggregate wrapper) — to `schemas/paginate.schema.json`. Run via
    /// `cargo test -p paginate-core --features schema export_schema` (the `just
    /// gen` codegen step); a normal test run (no `schema` feature) skips it.
    #[test]
    fn export_schema() {
        let mut generator = SchemaGenerator::default();
        // Each top-level type pulls its dependencies (enums, FilterNode) into the
        // shared `$defs`; nested groups recurse via `$ref`.
        generator.subschema_for::<FilterSpec>();
        generator.subschema_for::<FilterGroup>();
        generator.subschema_for::<SortSpec>();
        generator.subschema_for::<SearchSpec>();
        generator.subschema_for::<OffsetParams>();
        generator.subschema_for::<CursorParams>();
        generator.subschema_for::<OffsetPageMeta>();
        generator.subschema_for::<CursorPageMeta>();
        let doc = serde_json::json!({
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "paginate",
            "$defs": generator.take_definitions(true),
        });
        let json = serde_json::to_string_pretty(&doc).expect("schema serializes");
        let dir = concat!(env!("CARGO_MANIFEST_DIR"), "/../../schemas");
        std::fs::create_dir_all(dir).expect("create schemas dir");
        std::fs::write(format!("{dir}/paginate.schema.json"), json + "\n").expect("write schema");
    }
}
