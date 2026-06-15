//! WebAssembly bindings for `paginate-core`, powering the documentation
//! playground (`website/src/pages/playground.tsx`).
//!
//! The **same** engine that backs `pypaginate` and `@cyblow/paginate` runs here
//! in the browser — proving the "one core, every language" claim live. Inputs and
//! outputs cross as JSON strings (no `serde-wasm-bindgen` needed); each function
//! parses JSON into the core [`Value`] model, runs the engine, and returns JSON.

#![allow(clippy::missing_errors_doc)]

use paginate_core as core;
use serde_json::Value as Json;
use wasm_bindgen::prelude::*;

/// Parse a JSON array string into core values.
fn to_values(items_json: &str) -> Result<Vec<core::Value>, JsError> {
    let json: Json = serde_json::from_str(items_json).map_err(|e| JsError::new(&e.to_string()))?;
    let array = json
        .as_array()
        .ok_or_else(|| JsError::new("items must be a JSON array"))?;
    Ok(array.iter().map(core::json::from_json).collect())
}

/// Select the items at `indices` and render them back to a JSON array string.
fn select_json(items: &[core::Value], indices: &[usize]) -> String {
    let picked: Vec<Json> = indices.iter().map(|&i| core::json::to_json(&items[i])).collect();
    serde_json::to_string(&Json::Array(picked)).unwrap_or_else(|_| "[]".to_owned())
}

/// Filter `items` (a JSON array) by one condition; returns the matching items.
#[wasm_bindgen]
pub fn filter(items_json: &str, field: &str, operator: &str, value_json: &str) -> Result<String, JsError> {
    let items = to_values(items_json)?;
    let op = core::FilterOp::from_name(operator)
        .ok_or_else(|| JsError::new(&format!("unknown operator: {operator}")))?;
    let value: Json = serde_json::from_str(value_json).map_err(|e| JsError::new(&e.to_string()))?;
    let spec = core::FilterSpec {
        field: field.to_owned(),
        op,
        value: core::json::from_json(&value),
        logic: core::FilterLogic::And,
    };
    let input = core::FilterInput::Flat(vec![spec]);
    let indices = core::filter::filter_indices(&items, &input).map_err(|e| JsError::new(&e.to_string()))?;
    Ok(select_json(&items, &indices))
}

/// Sort `items` (a JSON array) by one key; returns the reordered items.
#[wasm_bindgen]
pub fn sort(items_json: &str, field: &str, direction: &str) -> Result<String, JsError> {
    let items = to_values(items_json)?;
    let spec = core::SortSpec {
        field: field.to_owned(),
        direction: core::SortDirection::from_token(direction).map_err(|e| JsError::new(&e.to_string()))?,
        nulls: core::NullsPosition::Last,
    };
    let indices = core::sort::sort_indices(&items, &[spec]).map_err(|e| JsError::new(&e.to_string()))?;
    Ok(select_json(&items, &indices))
}

/// Ranked search over `items` (a JSON array); returns matches best-first.
#[wasm_bindgen]
pub fn search(items_json: &str, query: &str, fields_json: &str, fuzzy: &str) -> Result<String, JsError> {
    let items = to_values(items_json)?;
    let fields: Vec<String> =
        serde_json::from_str(fields_json).map_err(|e| JsError::new(&e.to_string()))?;
    let spec = core::SearchSpec {
        query: query.to_owned(),
        fields,
        weights: None,
        mode: core::SearchFieldMode::Contains,
        fuzzy: core::FuzzyMode::from_token(fuzzy).map_err(|e| JsError::new(&e.to_string()))?,
        threshold: 30,
        min_length: 1,
        max_results: None,
    };
    let indices = core::search::search_indices(&items, &spec).map_err(|e| JsError::new(&e.to_string()))?;
    Ok(select_json(&items, &indices))
}

/// Encode ordering values (a JSON array) into a portable, URL-safe cursor.
#[wasm_bindgen(js_name = encodeCursor)]
pub fn encode_cursor(values_json: &str) -> Result<String, JsError> {
    let json: Json = serde_json::from_str(values_json).map_err(|e| JsError::new(&e.to_string()))?;
    let array = json
        .as_array()
        .ok_or_else(|| JsError::new("expected a JSON array of ordering values"))?;
    let values: Vec<core::Value> = array.iter().map(core::json::from_json).collect();
    core::encode_cursor(&values).map_err(|e| JsError::new(&e.to_string()))
}

/// Decode a cursor back into its ordering values (a JSON array).
#[wasm_bindgen(js_name = decodeCursor)]
pub fn decode_cursor(cursor: &str) -> Result<String, JsError> {
    let values = core::decode_cursor(cursor).map_err(|e| JsError::new(&e.to_string()))?;
    let json: Vec<Json> = values.iter().map(core::json::to_json).collect();
    serde_json::to_string(&Json::Array(json)).map_err(|e| JsError::new(&e.to_string()))
}
