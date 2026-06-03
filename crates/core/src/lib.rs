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

mod accessor;

pub mod coerce;
pub mod columnar;
pub mod cursor;
pub mod error;
pub mod filter;
pub mod normalize;
pub mod pagination;
pub mod pipeline;
pub mod search;
pub mod sort;
pub mod value;

pub use error::{CoreError, Result};
pub use normalize::normalize_text;
pub use value::Value;
