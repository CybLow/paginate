//! Typed per-column filtering: comparison/equality and the substring operators
//! on a dense scalar column, or `None` for anything the columnar path does not
//! provably handle (ranges, null/empty, `like`/`ilike`/`regex`, a needle whose
//! coercion can't be proven row-equal).

use std::collections::HashSet;
use std::hash::Hash;

use crate::coerce;
use crate::filter::{FilterOp, LikeMatcher};
use crate::value::Value;

use super::build::{value_as_bool, value_as_int, value_as_str};

fn collect(len: usize, keep: impl Fn(usize) -> bool) -> Vec<usize> {
    (0..len).filter(|&i| keep(i)).collect()
}

/// Inclusive `lo <= col[i] <= hi` when `value` is the `[lo, hi]` pair, both of
/// the column's type (mixed types fall back to the row engine, which coerces).
fn between_col<T: PartialOrd>(
    col: &[T],
    value: &Value,
    get: impl Fn(&Value) -> Option<T>,
) -> Option<Vec<usize>> {
    let Value::List(pair) = value else {
        return None;
    };
    let [lo, hi] = pair.as_slice() else {
        return None; // not exactly two -> row engine (which errors)
    };
    let (lo, hi) = (get(lo)?, get(hi)?);
    Some(collect(col.len(), |i| lo <= col[i] && col[i] <= hi))
}

/// `In`/`NotIn` membership when every list item is the column's hashable type:
/// builds the set once (`O(n + list)`) vs the row engine's per-row list scan.
fn member_col<T: Eq + Hash>(
    col: &[T],
    op: FilterOp,
    value: &Value,
    get: impl Fn(&Value) -> Option<T>,
) -> Option<Vec<usize>> {
    let Value::List(items) = value else {
        return None;
    };
    let set: HashSet<T> = items.iter().map(get).collect::<Option<_>>()?;
    let want = op == FilterOp::In;
    Some(collect(col.len(), |i| set.contains(&col[i]) == want))
}

/// Numeric needle for float bounds (Int/Float/Bool/Decimal -> f64), NaN rejected.
fn as_num(value: &Value) -> Option<f64> {
    coerce::as_number(value).filter(|f| !f.is_nan())
}

pub(super) fn filter_int(col: &[i64], op: FilterOp, value: &Value) -> Option<Vec<usize>> {
    match op {
        FilterOp::Between => return between_col(col, value, value_as_int),
        FilterOp::In | FilterOp::NotIn => return member_col(col, op, value, value_as_int),
        _ => {}
    }
    let &Value::Int(needle) = value else {
        return None; // non-int needle (e.g. `age > 2.5`) -> row engine via as_number
    };
    let keep = comparison(op)?;
    Some(collect(col.len(), |i| keep(&col[i], &needle)))
}

pub(super) fn filter_float(col: &[f64], op: FilterOp, value: &Value) -> Option<Vec<usize>> {
    if op == FilterOp::Between {
        return between_col(col, value, as_num); // f64 isn't hashable -> no In here
    }
    let needle = coerce::as_number(value)?; // Int/Float/Bool/Decimal -> f64, else fallback
    if needle.is_nan() {
        return None; // row engine errors (ordered) or all-false (eq); let it decide
    }
    let keep = comparison(op)?;
    Some(collect(col.len(), |i| keep(&col[i], &needle)))
}

pub(super) fn filter_str(col: &[String], op: FilterOp, value: &Value) -> Option<Vec<usize>> {
    // Substring operators on a dense Str column: stringify the needle exactly as
    // the row engine does (`to_py_str`) and scan directly — skipping the per-row
    // accessor walk and boxed-predicate dispatch the row engine pays, which the
    // columnar path exists to remove. The `str` methods are byte-identical.
    if let Some(matches) = str_op(op) {
        let needle = coerce::to_py_str(value);
        return Some(collect(col.len(), |i| matches(&col[i], &needle)));
    }
    if let Some(ci) = like_ci(op) {
        // Compile the LIKE/ILIKE matcher once, then scan — same as the row engine
        // does per spec, minus the per-row accessor walk and boxed dispatch.
        let matcher = LikeMatcher::compile(&coerce::to_py_str(value), ci);
        return Some(collect(col.len(), |i| matcher.matches(&col[i])));
    }
    if matches!(op, FilterOp::In | FilterOp::NotIn) {
        return member_col(col, op, value, value_as_str);
    }
    // Comparison/equality need a string needle (byte order == code-point order).
    let Value::Str(needle) = value else {
        return None; // non-string needle -> row engine (type-aware eq / as_text)
    };
    let keep = comparison::<str>(op)?;
    Some(collect(col.len(), |i| {
        keep(col[i].as_str(), needle.as_str())
    }))
}

/// The three substring operators as `(field, needle) -> bool`, or `None` for any
/// non-substring operator. Byte-identical to the row engine's `str` methods.
fn str_op(op: FilterOp) -> Option<fn(&str, &str) -> bool> {
    Some(match op {
        FilterOp::Contains => |f, n| f.contains(n),
        FilterOp::StartsWith => |f, n| f.starts_with(n),
        FilterOp::EndsWith => |f, n| f.ends_with(n),
        _ => return None,
    })
}

/// `Some(case_insensitive)` for `Like`/`ILike`, else `None`.
fn like_ci(op: FilterOp) -> Option<bool> {
    match op {
        FilterOp::Like => Some(false),
        FilterOp::ILike => Some(true),
        _ => None,
    }
}

pub(super) fn filter_bool(col: &[bool], op: FilterOp, value: &Value) -> Option<Vec<usize>> {
    if matches!(op, FilterOp::In | FilterOp::NotIn) {
        return member_col(col, op, value, value_as_bool);
    }
    let &Value::Bool(needle) = value else {
        return None; // non-bool needle (e.g. active == 1) -> row engine via as_number
    };
    // bool == bool matches coerce::eq (both fold to 0/1) and false < true matches
    // coerce::compare's explicit (Bool, Bool) arm, so all six ops stay row-exact.
    let keep = comparison(op)?;
    Some(collect(col.len(), |i| keep(&col[i], &needle)))
}

/// The six order/equality operators as a predicate, or `None` for any operator
/// the columnar path does not handle (string ops, ranges, null/empty).
///
/// `Eq`/`Ne` use the column's native `==` — for a homogeneously-typed column
/// that equals `coerce::eq` — while the four ordering operators delegate to the
/// shared [`FilterOp::holds_for`], so this fast path and the row engine
/// derive ordering from one source and cannot drift.
fn comparison<T: PartialOrd + ?Sized>(op: FilterOp) -> Option<impl Fn(&T, &T) -> bool> {
    let supported = matches!(
        op,
        FilterOp::Eq | FilterOp::Ne | FilterOp::Gt | FilterOp::Gte | FilterOp::Lt | FilterOp::Lte
    );
    supported.then_some(move |a: &T, b: &T| match op {
        FilterOp::Eq => a == b,
        FilterOp::Ne => a != b,
        _ => a
            .partial_cmp(b)
            .and_then(|o| op.holds_for(o))
            .unwrap_or(false),
    })
}
