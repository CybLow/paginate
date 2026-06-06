//! # paginate-core
//!
//! Pure, language-agnostic engine behind [`pypaginate`]. It owns the
//! computational heart of the library — cursor encoding, offset math, text
//! normalization, filtering, sorting and search — with **zero binding
//! dependencies** so the exact same crate links natively into Python (via
//! PyO3) today and compiles unchanged to WebAssembly / N-API for the planned
//! JS/TS port.
//!
//! ## Design rules
//!
//! * **Plain data only.** Everything crosses the boundary as [`value::Value`],
//!   a small JSON-like enum. No host objects, no framework types.
//! * **Deterministic & side-effect free.** Same input, same output — which is
//!   what lets the Python property-based invariants double as the port's
//!   conformance suite.
//! * **Behaviour parity.** Each module mirrors the semantics of its Python
//!   counterpart (e.g. the cursor wire format is byte-identical, so cursors
//!   minted by either implementation decode in the other).
//!
//! [`pypaginate`]: https://github.com/CybLow/paginate

#![forbid(unsafe_code)]

// Internal-only modules: shared helpers and the error type. `CoreError`/`Result`
// reach the public API through the flat re-exports below, never `core::error::`.
mod accessor;
mod coerce;
mod error;

pub mod columnar;
pub mod cursor;
pub mod filter;
pub mod keyset;
pub mod normalize;
pub mod pagination;
pub mod pipeline;
pub mod search;
pub mod sort;
pub mod validate;
pub mod value;

// Wire-form DTOs + JSON Schema export — the cross-language type contract. Behind
// the `schema` feature so the default build carries no schemars dependency.
#[cfg(feature = "schema")]
pub mod schema;

// Flat re-export of the public surface: callers (and the PyO3 / napi bindings)
// write `paginate_core::FilterSpec`, never `paginate_core::filter::types::...`,
// so the module layout can change without breaking them. This is the single,
// canonical home of the domain contract the language bindings wrap.
pub use columnar::Columns;
pub use cursor::{decode_cursor, encode_cursor};
pub use error::{CoreError, Result};
pub use filter::{FilterGroup, FilterInput, FilterLogic, FilterNode, FilterOp, FilterSpec};
pub use normalize::normalize_text;
pub use pipeline::{offset_page, offset_page_searched, Page, SearchStage};
pub use search::{FuzzyMode, SearchFieldMode, SearchSpec, TrigramIndex};
pub use sort::{NullsPosition, SortDirection, SortSpec};
pub use validate::MAX_LIMIT;
pub use value::Value;
