//! In-memory filtering: 20 operators, flat AND/OR lists, and nested groups.
//! Behaviour mirrors pypaginate's `filtering/` package.
//!
//! [`filter_indices`] returns the indices of matching items so the binding
//! layer can select from the original host objects without cloning them through
//! the core. [`apply`] is a convenience that clones the matched values.

mod like;
mod operators;
mod types;

use regex::Regex;

use crate::accessor::{compile_path, resolve, resolve_present};
use crate::coerce;
use crate::error::{CoreError, Result};
use crate::value::Value;

pub use types::{FilterGroup, FilterInput, FilterLogic, FilterNode, FilterOp, FilterSpec};

// Re-exported for the columnar fast path's LIKE/ILIKE scan over a Str column.
pub(crate) use like::LikeMatcher;

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
    let value = spec.value.clone();
    if let Some(pred) = compile_str_op(spec.op, &value, &path)? {
        return Ok(pred);
    }
    match spec.op {
        // `exists` is presence-only: an absent field is `false`, not an error
        // (unlike the strict-`resolve` operators), and a present-but-null field
        // still exists.
        FilterOp::Exists => Ok(Box::new(move |item| {
            Ok(resolve_present(item, &path).is_some())
        })),
        op => Ok(Box::new(move |item| {
            operators::eval_op(op, resolve(item, &path)?, &value)
        })),
    }
}

/// Compile the string-matching operators — each a test precompiled once and
/// applied to the resolved field's string form via [`str_pred`] — or `None` for
/// any other operator (handled directly by [`compile_spec`]).
fn compile_str_op(op: FilterOp, value: &Value, path: &[String]) -> Result<Option<Pred>> {
    let pred = match op {
        FilterOp::Regex => {
            let re = compile_regex(&coerce::to_py_str(value))?;
            str_pred(path, move |s| re.is_match(s))
        }
        FilterOp::Like => {
            let matcher = LikeMatcher::compile(&coerce::to_py_str(value), false);
            str_pred(path, move |s| matcher.matches(s))
        }
        FilterOp::ILike => {
            let matcher = LikeMatcher::compile(&coerce::to_py_str(value), true);
            str_pred(path, move |s| matcher.matches(s))
        }
        FilterOp::Contains => {
            let needle = coerce::to_py_str(value);
            str_pred(path, move |s| s.contains(&needle))
        }
        FilterOp::StartsWith => {
            let prefix = coerce::to_py_str(value);
            str_pred(path, move |s| s.starts_with(&prefix))
        }
        FilterOp::EndsWith => {
            let suffix = coerce::to_py_str(value);
            str_pred(path, move |s| s.ends_with(&suffix))
        }
        _ => return Ok(None),
    };
    Ok(Some(pred))
}

/// A predicate that resolves the (strict) `path`, renders it to a string, and
/// applies a precompiled `test` — the shape shared by every string operator.
fn str_pred(path: &[String], test: impl Fn(&str) -> bool + 'static) -> Pred {
    let path = path.to_vec();
    Box::new(move |item| Ok(test(&coerce::to_py_str_cow(resolve(item, &path)?))))
}

fn compile_regex(pattern: &str) -> Result<Regex> {
    // Bound the length check itself: stop scanning once the cap is exceeded.
    if pattern.chars().take(MAX_REGEX_LENGTH + 1).count() > MAX_REGEX_LENGTH {
        return Err(CoreError::Filter {
            message: format!("Invalid regex: exceeds {MAX_REGEX_LENGTH} characters"),
        });
    }
    Regex::new(pattern).map_err(|err| CoreError::Filter {
        message: format!("Invalid regex pattern: '{pattern}': {err}"),
    })
}

#[cfg(test)]
mod tests;
