//! In-memory filtering: 20 operators, flat AND/OR lists, and nested groups.
//! Behaviour mirrors pypaginate's `filtering/` package.
//!
//! [`filter_indices`] returns the indices of matching items so the binding
//! layer can select from the original host objects without cloning them through
//! the core. [`apply`] is a convenience that clones the matched values.

mod like;
mod operators;

use regex::Regex;

use crate::accessor::{compile_path, resolve};
use crate::coerce;
use crate::error::{CoreError, Result};
use crate::value::Value;

/// Logical combinator for filter conditions.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FilterLogic {
    And,
    Or,
}

/// One of the 20 supported filter operators.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FilterOp {
    Eq,
    Ne,
    Gt,
    Gte,
    Lt,
    Lte,
    In,
    NotIn,
    Contains,
    StartsWith,
    EndsWith,
    Like,
    ILike,
    Between,
    IsNull,
    IsNotNull,
    Regex,
    Empty,
    NotEmpty,
    Exists,
}

impl FilterOp {
    /// Parse the Python operator name (e.g. `"not_in"`, `"starts_with"`).
    #[must_use]
    pub fn from_name(name: &str) -> Option<Self> {
        Some(match name {
            "eq" => Self::Eq,
            "ne" => Self::Ne,
            "gt" => Self::Gt,
            "gte" => Self::Gte,
            "lt" => Self::Lt,
            "lte" => Self::Lte,
            "in" => Self::In,
            "not_in" => Self::NotIn,
            "contains" => Self::Contains,
            "starts_with" => Self::StartsWith,
            "ends_with" => Self::EndsWith,
            "like" => Self::Like,
            "ilike" => Self::ILike,
            "between" => Self::Between,
            "is_null" => Self::IsNull,
            "is_not_null" => Self::IsNotNull,
            "regex" => Self::Regex,
            "empty" => Self::Empty,
            "not_empty" => Self::NotEmpty,
            "exists" => Self::Exists,
            _ => return None,
        })
    }
}

/// A single filter condition.
#[derive(Debug, Clone)]
pub struct FilterSpec {
    /// Dotted field path (e.g. `"user.age"`).
    pub field: String,
    /// Operator to apply.
    pub op: FilterOp,
    /// Comparison value (meaning depends on the operator).
    pub value: Value,
    /// Whether this spec joins others with AND or OR (flat-list mode).
    pub logic: FilterLogic,
}

/// A node in a nested filter tree.
#[derive(Debug, Clone)]
pub enum FilterNode {
    /// A leaf condition.
    Spec(FilterSpec),
    /// A nested group.
    Group(FilterGroup),
}

/// A composite AND/OR group of conditions.
#[derive(Debug, Clone)]
pub struct FilterGroup {
    /// How the child conditions combine.
    pub logic: FilterLogic,
    /// Child conditions (specs or nested groups).
    pub conditions: Vec<FilterNode>,
}

/// Filter input: either a flat spec list or a nested group.
#[derive(Debug, Clone)]
pub enum FilterInput {
    /// Flat list combined via each spec's `logic`.
    Flat(Vec<FilterSpec>),
    /// Nested AND/OR tree.
    Group(FilterGroup),
}

const MAX_REGEX_LENGTH: usize = 200;

type Pred = Box<dyn Fn(&Value) -> Result<bool>>;

/// Return the indices of items matching `input`, in original order.
///
/// # Errors
/// Propagates [`CoreError::FieldNotFound`] for an unresolved path and
/// [`CoreError::Filter`] for bad operands or an invalid regex.
pub fn filter_indices(items: &[Value], input: &FilterInput) -> Result<Vec<usize>> {
    let predicate = compile_input(input)?;
    let mut matched = Vec::new();
    for (index, item) in items.iter().enumerate() {
        if predicate(item)? {
            matched.push(index);
        }
    }
    Ok(matched)
}

/// Convenience wrapper around [`filter_indices`] that clones matched items.
///
/// # Errors
/// See [`filter_indices`].
pub fn apply(items: &[Value], input: &FilterInput) -> Result<Vec<Value>> {
    let indices = filter_indices(items, input)?;
    Ok(indices.into_iter().map(|i| items[i].clone()).collect())
}

fn compile_input(input: &FilterInput) -> Result<Pred> {
    match input {
        FilterInput::Group(group) => compile_group(group),
        FilterInput::Flat(specs) => compile_flat(specs),
    }
}

fn compile_flat(specs: &[FilterSpec]) -> Result<Pred> {
    if specs.is_empty() {
        return Ok(Box::new(|_| Ok(true)));
    }
    let mut ands: Vec<Pred> = Vec::new();
    let mut ors: Vec<Pred> = Vec::new();
    for spec in specs {
        let predicate = compile_spec(spec)?;
        match spec.logic {
            FilterLogic::And => ands.push(predicate),
            FilterLogic::Or => ors.push(predicate),
        }
    }
    Ok(Box::new(move |item| {
        for p in &ands {
            if !p(item)? {
                return Ok(false);
            }
        }
        if ors.is_empty() {
            return Ok(true);
        }
        for p in &ors {
            if p(item)? {
                return Ok(true);
            }
        }
        Ok(false)
    }))
}

fn compile_group(group: &FilterGroup) -> Result<Pred> {
    let mut children: Vec<Pred> = Vec::with_capacity(group.conditions.len());
    for condition in &group.conditions {
        children.push(match condition {
            FilterNode::Spec(spec) => compile_spec(spec)?,
            FilterNode::Group(sub) => compile_group(sub)?,
        });
    }
    let logic = group.logic;
    Ok(Box::new(move |item| match logic {
        FilterLogic::And => {
            for p in &children {
                if !p(item)? {
                    return Ok(false);
                }
            }
            Ok(true)
        }
        FilterLogic::Or => {
            for p in &children {
                if p(item)? {
                    return Ok(true);
                }
            }
            Ok(false)
        }
    }))
}

fn compile_spec(spec: &FilterSpec) -> Result<Pred> {
    let path = compile_path(&spec.field)?;
    let op = spec.op;
    let value = spec.value.clone();
    match op {
        FilterOp::Regex => {
            let re = compile_regex(&coerce::to_py_str(&value))?;
            Ok(Box::new(move |item| {
                Ok(re.is_match(&coerce::to_py_str(resolve(item, &path)?)))
            }))
        }
        FilterOp::Like => {
            let matcher = like::LikeMatcher::compile(&coerce::to_py_str(&value), false);
            Ok(Box::new(move |item| {
                Ok(matcher.matches(&coerce::to_py_str(resolve(item, &path)?)))
            }))
        }
        FilterOp::ILike => {
            let matcher = like::LikeMatcher::compile(&coerce::to_py_str(&value), true);
            Ok(Box::new(move |item| {
                Ok(matcher.matches(&coerce::to_py_str(resolve(item, &path)?)))
            }))
        }
        FilterOp::Contains => {
            let needle = coerce::to_py_str(&value);
            Ok(Box::new(move |item| {
                Ok(coerce::to_py_str(resolve(item, &path)?).contains(&needle))
            }))
        }
        FilterOp::StartsWith => {
            let prefix = coerce::to_py_str(&value);
            Ok(Box::new(move |item| {
                Ok(coerce::to_py_str(resolve(item, &path)?).starts_with(&prefix))
            }))
        }
        FilterOp::EndsWith => {
            let suffix = coerce::to_py_str(&value);
            Ok(Box::new(move |item| {
                Ok(coerce::to_py_str(resolve(item, &path)?).ends_with(&suffix))
            }))
        }
        _ => Ok(Box::new(move |item| {
            operators::eval_op(op, resolve(item, &path)?, &value)
        })),
    }
}

fn compile_regex(pattern: &str) -> Result<Regex> {
    if pattern.chars().count() > MAX_REGEX_LENGTH {
        return Err(CoreError::Filter {
            message: format!("Invalid regex: exceeds {MAX_REGEX_LENGTH} characters"),
        });
    }
    Regex::new(pattern).map_err(|err| CoreError::Filter {
        message: format!("Invalid regex pattern: '{pattern}': {err}"),
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::BTreeMap;

    fn item(pairs: &[(&str, Value)]) -> Value {
        let mut map = BTreeMap::new();
        for (key, value) in pairs {
            map.insert((*key).to_owned(), value.clone());
        }
        Value::Map(map)
    }

    fn spec(field: &str, op: FilterOp, value: Value) -> FilterSpec {
        FilterSpec {
            field: field.to_owned(),
            op,
            value,
            logic: FilterLogic::And,
        }
    }

    fn flat(specs: Vec<FilterSpec>) -> FilterInput {
        FilterInput::Flat(specs)
    }

    #[test]
    fn comparison_and_numeric_equality() {
        let items = vec![
            item(&[("age", Value::Int(20))]),
            item(&[("age", Value::Int(40))]),
            item(&[("age", Value::Int(18))]),
        ];
        let idx = filter_indices(
            &items,
            &flat(vec![spec("age", FilterOp::Gte, Value::Int(20))]),
        )
        .unwrap();
        assert_eq!(idx, vec![0, 1]);
        // 40 == 40.0 (cross-type numeric equality, like Python).
        let idx = filter_indices(
            &items,
            &flat(vec![spec("age", FilterOp::Eq, Value::Float(40.0))]),
        )
        .unwrap();
        assert_eq!(idx, vec![1]);
    }

    #[test]
    fn string_operators() {
        let items = vec![
            item(&[("name", Value::Str("Alice".into()))]),
            item(&[("name", Value::Str("Bob".into()))]),
        ];
        let idx = filter_indices(
            &items,
            &flat(vec![spec(
                "name",
                FilterOp::Contains,
                Value::Str("li".into()),
            )]),
        )
        .unwrap();
        assert_eq!(idx, vec![0]);
        let idx = filter_indices(
            &items,
            &flat(vec![spec("name", FilterOp::Like, Value::Str("Bo%".into()))]),
        )
        .unwrap();
        assert_eq!(idx, vec![1]);
        let idx = filter_indices(
            &items,
            &flat(vec![spec(
                "name",
                FilterOp::ILike,
                Value::Str("%LICE".into()),
            )]),
        )
        .unwrap();
        assert_eq!(idx, vec![0]);
    }

    #[test]
    fn membership_range_and_empty() {
        let items = vec![
            item(&[("s", Value::Str("a".into())), ("n", Value::Int(5))]),
            item(&[("s", Value::Str("".into())), ("n", Value::Int(50))]),
        ];
        let in_list = Value::List(vec![Value::Str("a".into()), Value::Str("b".into())]);
        let idx = filter_indices(&items, &flat(vec![spec("s", FilterOp::In, in_list)])).unwrap();
        assert_eq!(idx, vec![0]);
        let bounds = Value::List(vec![Value::Int(0), Value::Int(10)]);
        let idx =
            filter_indices(&items, &flat(vec![spec("n", FilterOp::Between, bounds)])).unwrap();
        assert_eq!(idx, vec![0]);
        let idx =
            filter_indices(&items, &flat(vec![spec("s", FilterOp::Empty, Value::Null)])).unwrap();
        assert_eq!(idx, vec![1]);
    }

    #[test]
    fn regex_operator() {
        let items = vec![
            item(&[("code", Value::Str("AB123".into()))]),
            item(&[("code", Value::Str("xx".into()))]),
        ];
        let idx = filter_indices(
            &items,
            &flat(vec![spec(
                "code",
                FilterOp::Regex,
                Value::Str("[0-9]+".into()),
            )]),
        )
        .unwrap();
        assert_eq!(idx, vec![0]);
    }

    #[test]
    fn nested_group_and_of_or() {
        // (a == 1 OR b == 2) AND c == 3
        let items = vec![
            item(&[
                ("a", Value::Int(1)),
                ("b", Value::Int(0)),
                ("c", Value::Int(3)),
            ]),
            item(&[
                ("a", Value::Int(0)),
                ("b", Value::Int(2)),
                ("c", Value::Int(3)),
            ]),
            item(&[
                ("a", Value::Int(1)),
                ("b", Value::Int(2)),
                ("c", Value::Int(9)),
            ]),
        ];
        let group = FilterGroup {
            logic: FilterLogic::And,
            conditions: vec![
                FilterNode::Group(FilterGroup {
                    logic: FilterLogic::Or,
                    conditions: vec![
                        FilterNode::Spec(spec("a", FilterOp::Eq, Value::Int(1))),
                        FilterNode::Spec(spec("b", FilterOp::Eq, Value::Int(2))),
                    ],
                }),
                FilterNode::Spec(spec("c", FilterOp::Eq, Value::Int(3))),
            ],
        };
        let idx = filter_indices(&items, &FilterInput::Group(group)).unwrap();
        assert_eq!(idx, vec![0, 1]);
    }

    #[test]
    fn flat_or_logic() {
        let items = vec![
            item(&[("name", Value::Str("Alice".into())), ("age", Value::Int(1))]),
            item(&[("name", Value::Str("Bob".into())), ("age", Value::Int(99))]),
            item(&[("name", Value::Str("Cara".into())), ("age", Value::Int(1))]),
        ];
        let specs = vec![
            FilterSpec {
                field: "name".into(),
                op: FilterOp::Eq,
                value: Value::Str("Alice".into()),
                logic: FilterLogic::Or,
            },
            FilterSpec {
                field: "age".into(),
                op: FilterOp::Eq,
                value: Value::Int(99),
                logic: FilterLogic::Or,
            },
        ];
        let idx = filter_indices(&items, &flat(specs)).unwrap();
        assert_eq!(idx, vec![0, 1]);
    }

    #[test]
    fn dotted_path_resolves_nested() {
        let inner = item(&[("age", Value::Int(30))]);
        let items = vec![item(&[("user", inner)])];
        let idx = filter_indices(
            &items,
            &flat(vec![spec("user.age", FilterOp::Gte, Value::Int(18))]),
        )
        .unwrap();
        assert_eq!(idx, vec![0]);
    }

    #[test]
    fn errors_and_edge_cases() {
        let items = vec![item(&[("a", Value::Int(1))])];
        assert!(matches!(
            filter_indices(
                &items,
                &flat(vec![spec("missing", FilterOp::Eq, Value::Int(1))])
            ),
            Err(CoreError::FieldNotFound { .. })
        ));
        assert!(matches!(
            filter_indices(
                &items,
                &flat(vec![spec("_secret", FilterOp::Eq, Value::Int(1))])
            ),
            Err(CoreError::Filter { .. })
        ));
        // Empty filter list returns everything.
        let idx = filter_indices(&items, &flat(vec![])).unwrap();
        assert_eq!(idx, vec![0]);
    }

    #[test]
    fn op_names_round_trip() {
        assert_eq!(FilterOp::from_name("not_in"), Some(FilterOp::NotIn));
        assert_eq!(
            FilterOp::from_name("starts_with"),
            Some(FilterOp::StartsWith)
        );
        assert_eq!(FilterOp::from_name("nope"), None);
    }
}
