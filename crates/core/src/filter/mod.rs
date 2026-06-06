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

use crate::accessor::{compile_path, resolve};
use crate::coerce;
use crate::error::{CoreError, Result};
use crate::value::Value;

pub use types::{FilterGroup, FilterInput, FilterLogic, FilterNode, FilterOp, FilterSpec};

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
                Ok(re.is_match(&coerce::to_py_str_cow(resolve(item, &path)?)))
            }))
        }
        FilterOp::Like => {
            let matcher = like::LikeMatcher::compile(&coerce::to_py_str(&value), false);
            Ok(Box::new(move |item| {
                Ok(matcher.matches(&coerce::to_py_str_cow(resolve(item, &path)?)))
            }))
        }
        FilterOp::ILike => {
            let matcher = like::LikeMatcher::compile(&coerce::to_py_str(&value), true);
            Ok(Box::new(move |item| {
                Ok(matcher.matches(&coerce::to_py_str_cow(resolve(item, &path)?)))
            }))
        }
        FilterOp::Contains => {
            let needle = coerce::to_py_str(&value);
            Ok(Box::new(move |item| {
                Ok(coerce::to_py_str_cow(resolve(item, &path)?).contains(&needle))
            }))
        }
        FilterOp::StartsWith => {
            let prefix = coerce::to_py_str(&value);
            Ok(Box::new(move |item| {
                Ok(coerce::to_py_str_cow(resolve(item, &path)?).starts_with(&prefix))
            }))
        }
        FilterOp::EndsWith => {
            let suffix = coerce::to_py_str(&value);
            Ok(Box::new(move |item| {
                Ok(coerce::to_py_str_cow(resolve(item, &path)?).ends_with(&suffix))
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
mod tests;
