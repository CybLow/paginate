//! Host-specific marshalling for the napi binding: the JS array helper and the
//! core-error → napi-error mapping. The `serde_json::Value` ↔ [`core::Value`]
//! bridge itself lives in `core::json` (tested once, shared) and is re-exported
//! here under the binding's local names.

use napi::bindgen_prelude::{Error, Result, Status};
use serde_json::Value as Json;

use ::paginate_core as core;

// The JSON ↔ Value bridge is owned and unit-tested by the core crate; the
// binding only re-exports it under its established local names.
pub(crate) use core::json::{from_json as json_to_value, to_json as value_to_json};

/// Marshal a JS array of values into core [`core::Value`]s (errors if not an
/// array). Consumes `items` so the (resident-Dataset / one-shot) marshalling
/// **moves** each row's strings and object keys instead of cloning them
/// (measured ~1.7x faster than the borrowing bridge on a 10K array).
pub(crate) fn json_array_to_values(items: Json) -> Result<Vec<core::Value>> {
    match items {
        Json::Array(array) => Ok(array.into_iter().map(core::json::from_json_owned).collect()),
        _ => Err(Error::new(Status::InvalidArg, "items must be an array")),
    }
}

/// Convert core `usize` indices to the `u32` array napi returns to JS.
pub(crate) fn to_u32(indices: Vec<usize>) -> Vec<u32> {
    indices.into_iter().map(|i| i as u32).collect()
}

/// Map a core error onto a napi error thrown to JS. (`From<CoreError>` is not
/// possible — both types are foreign to this crate — so a helper is the idiom.)
pub(crate) fn core_err(err: &core::CoreError) -> Error {
    Error::new(Status::InvalidArg, err.to_string())
}
