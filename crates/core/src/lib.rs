//! # paginate-core
//!
//! Pure, language-agnostic engine behind the [`pypaginate`] (Python) and
//! [`@cyblow/paginate`] (TypeScript) packages. It owns the computational heart
//! of the library — cursor encoding, offset math, text normalization,
//! filtering, sorting and search — with **zero binding dependencies** so the
//! exact same crate links natively into Python (via PyO3) and Node/TypeScript
//! (via napi-rs), and compiles unchanged to WebAssembly for an optional
//! browser/edge target.
//!
//! ## Design rules
//!
//! * **Plain data only.** Everything crosses the boundary as [`value::Value`],
//!   a small JSON-like enum. No host objects, no framework types.
//! * **Deterministic & side-effect free.** Same input, same output — which is
//!   what lets the shared property-based invariants double as every binding's
//!   conformance suite.
//! * **Behaviour parity.** Each binding wraps this one engine, so results match
//!   across languages (e.g. the cursor wire format is byte-identical, so cursors
//!   minted by any implementation decode in the others).
//!
//! [`pypaginate`]: https://github.com/CybLow/paginate
//! [`@cyblow/paginate`]: https://www.npmjs.com/package/@cyblow/paginate

#![forbid(unsafe_code)]
#![warn(missing_docs)]

// Internal-only modules: shared helpers and the error type. `CoreError`/`Result`
// reach the public API through the flat re-exports below, never `core::error::`.
mod accessor;
mod coerce;
mod error;

pub mod columnar;
pub mod cursor;
pub mod filter;
pub mod json;
pub mod keyset;
pub mod normalize;
pub mod pagination;
pub mod pipeline;
pub mod resident;
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
pub use error::{CoreError, ErrorKind, Result};
pub use filter::{FilterGroup, FilterInput, FilterLogic, FilterNode, FilterOp, FilterSpec};
pub use normalize::normalize_text;
pub use pagination::Limit;
pub use pipeline::{offset_page, offset_page_searched, Page, SearchStage};
pub use search::{FuzzyMode, SearchFieldMode, SearchSpec, TrigramIndex};
pub use sort::{NullsPosition, SortDirection, SortSpec};
pub use validate::MAX_LIMIT;
pub use value::Value;
