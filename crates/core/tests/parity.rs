//! Cross-language parity: the Rust core must agree, byte-for-byte and
//! index-for-index, with the frozen golden in `tests/fixtures/parity.json` that
//! the Python and Node bindings are tested against too. If a codec or engine
//! change breaks cross-language agreement, this test (and its peers in py/ and
//! ts/) fail until the fixture is deliberately regenerated and its diff reviewed.
//!
//! See `tests/fixtures/generate_parity.py` for how the golden is produced.

use std::collections::BTreeMap;

use paginate_core as core;
use serde_json::Value as Json;

use core::cursor::{decode_cursor, encode_cursor};
use core::filter::{self, FilterInput, FilterLogic, FilterOp, FilterSpec};
use core::search::{self, FuzzyMode, SearchFieldMode, SearchSpec};
use core::sort::{self, NullsPosition, SortDirection, SortSpec};
use core::Value;

const FIXTURE: &str = include_str!(concat!(
    env!("CARGO_MANIFEST_DIR"),
    "/../../tests/fixtures/parity.json"
));

fn fixture() -> Json {
    serde_json::from_str(FIXTURE).expect("parity.json parses")
}

// -- JSON -> core Value (decodes the tagged typed-scalar wire form) -----------

fn to_value(json: &Json) -> Value {
    match json {
        Json::Null => Value::Null,
        Json::Bool(b) => Value::Bool(*b),
        Json::Number(n) => number(n),
        Json::String(s) => Value::Str(s.clone()),
        Json::Array(items) => Value::List(items.iter().map(to_value).collect()),
        Json::Object(map) => object(map),
    }
}

fn number(n: &serde_json::Number) -> Value {
    n.as_i64().map_or_else(
        || Value::Float(n.as_f64().expect("finite number")),
        Value::Int,
    )
}

fn object(map: &serde_json::Map<String, Json>) -> Value {
    if let Some(Json::String(tag)) = map.get("__type__") {
        let raw = map.get("v").and_then(Json::as_str).unwrap_or_default();
        return tagged(tag, raw.to_owned());
    }
    let entries = map.iter().map(|(k, v)| (k.clone(), to_value(v)));
    Value::Map(entries.collect::<BTreeMap<_, _>>())
}

fn tagged(tag: &str, raw: String) -> Value {
    match tag {
        "datetime" => Value::DateTime(raw),
        "date" => Value::Date(raw),
        "decimal" => Value::Decimal(raw),
        "uuid" => Value::Uuid(raw),
        other => panic!("unknown type tag: {other}"),
    }
}

fn values(case: &Json, key: &str) -> Vec<Value> {
    case[key]
        .as_array()
        .expect("array field")
        .iter()
        .map(to_value)
        .collect()
}

fn expected(case: &Json) -> Vec<usize> {
    case["expected"]
        .as_array()
        .expect("expected array")
        .iter()
        .map(|i| i.as_u64().expect("index") as usize)
        .collect()
}

// -- spec builders ------------------------------------------------------------

fn logic(name: &str) -> FilterLogic {
    if name == "or" {
        FilterLogic::Or
    } else {
        FilterLogic::And
    }
}

fn filter_spec(arr: &Json) -> FilterSpec {
    let parts = arr.as_array().expect("spec tuple");
    FilterSpec {
        field: parts[0].as_str().expect("field").to_owned(),
        op: FilterOp::from_name(parts[1].as_str().expect("op")).expect("known op"),
        value: to_value(&parts[2]),
        logic: logic(parts[3].as_str().expect("logic")),
    }
}

fn sort_spec(arr: &Json) -> SortSpec {
    let parts = arr.as_array().expect("sort tuple");
    SortSpec {
        field: parts[0].as_str().expect("field").to_owned(),
        direction: if parts[1].as_str() == Some("desc") {
            SortDirection::Desc
        } else {
            SortDirection::Asc
        },
        nulls: if parts[2].as_str() == Some("first") {
            NullsPosition::First
        } else {
            NullsPosition::Last
        },
    }
}

fn search_mode(name: &str) -> SearchFieldMode {
    match name {
        "prefix" => SearchFieldMode::Prefix,
        "exact" => SearchFieldMode::Exact,
        _ => SearchFieldMode::Contains,
    }
}

// -- tests --------------------------------------------------------------------

#[test]
fn cursors_encode_and_round_trip() {
    let data = fixture();
    for group in ["cursors", "cursors_typed"] {
        for case in data[group].as_array().expect("cursor cases") {
            let vals = values(case, "values");
            let golden = case["encoded"].as_str().expect("encoded");
            assert_eq!(encode_cursor(&vals), golden, "encode {group}");
            assert_eq!(
                decode_cursor(golden).expect("decode"),
                vals,
                "decode {group}"
            );
        }
    }
}

#[test]
fn filter_matches_golden() {
    let data = fixture();
    for case in data["filter"].as_array().expect("filter cases") {
        let items = values(case, "items");
        let specs = case["specs"]
            .as_array()
            .expect("specs")
            .iter()
            .map(filter_spec);
        let got =
            filter::filter_indices(&items, &FilterInput::Flat(specs.collect())).expect("filter ok");
        assert_eq!(got, expected(case));
    }
}

#[test]
fn sort_matches_golden() {
    let data = fixture();
    for case in data["sort"].as_array().expect("sort cases") {
        let items = values(case, "items");
        let specs: Vec<SortSpec> = case["specs"]
            .as_array()
            .expect("specs")
            .iter()
            .map(sort_spec)
            .collect();
        let got = sort::sort_indices(&items, &specs).expect("sort ok");
        assert_eq!(got, expected(case));
    }
}

#[test]
fn search_matches_golden() {
    let data = fixture();
    for case in data["search"].as_array().expect("search cases") {
        let items = values(case, "items");
        let spec = SearchSpec {
            query: case["query"].as_str().expect("query").to_owned(),
            fields: case["fields"]
                .as_array()
                .expect("fields")
                .iter()
                .map(|f| f.as_str().expect("field").to_owned())
                .collect(),
            weights: None,
            mode: search_mode(case["mode"].as_str().expect("mode")),
            fuzzy: FuzzyMode::Exact,
            threshold: 75,
            min_length: 1,
            max_results: None,
        };
        let got = search::search_indices(&items, &spec).expect("search ok");
        assert_eq!(got, expected(case));
    }
}
