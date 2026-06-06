//! Typed per-column filtering: a comparison/equality op on a dense scalar column,
//! or `None` for anything the columnar path does not provably handle (string ops,
//! ranges, null/empty, a needle whose coercion can't be proven row-equal).

use crate::coerce;
use crate::filter::FilterOp;
use crate::value::Value;

fn collect(len: usize, keep: impl Fn(usize) -> bool) -> Vec<usize> {
    (0..len).filter(|&i| keep(i)).collect()
}

pub(super) fn filter_int(col: &[i64], op: FilterOp, value: &Value) -> Option<Vec<usize>> {
    let &Value::Int(needle) = value else {
        return None; // non-int needle (e.g. `age > 2.5`) -> row engine via as_number
    };
    let keep: fn(&i64, &i64) -> bool = comparison(op)?;
    Some(collect(col.len(), |i| keep(&col[i], &needle)))
}

pub(super) fn filter_float(col: &[f64], op: FilterOp, value: &Value) -> Option<Vec<usize>> {
    let needle = coerce::as_number(value)?; // Int/Float/Bool/Decimal -> f64, else fallback
    if needle.is_nan() {
        return None; // row engine errors (ordered) or all-false (eq); let it decide
    }
    let keep: fn(&f64, &f64) -> bool = comparison(op)?;
    Some(collect(col.len(), |i| keep(&col[i], &needle)))
}

pub(super) fn filter_str(col: &[String], op: FilterOp, value: &Value) -> Option<Vec<usize>> {
    let Value::Str(needle) = value else {
        return None; // non-string needle -> row engine (type-aware eq / as_text)
    };
    let keep: fn(&str, &str) -> bool = comparison(op)?;
    Some(collect(col.len(), |i| {
        keep(col[i].as_str(), needle.as_str())
    }))
}

pub(super) fn filter_bool(col: &[bool], op: FilterOp, value: &Value) -> Option<Vec<usize>> {
    let &Value::Bool(needle) = value else {
        return None; // non-bool needle (e.g. active == 1) -> row engine via as_number
    };
    // bool == bool matches coerce::eq (both fold to 0/1) and false < true matches
    // coerce::compare's explicit (Bool, Bool) arm, so all six ops stay row-exact.
    let keep: fn(&bool, &bool) -> bool = comparison(op)?;
    Some(collect(col.len(), |i| keep(&col[i], &needle)))
}

/// The six order/equality operators as a comparison function, or `None` for any
/// operator the columnar path does not handle (string ops, ranges, null/empty).
fn comparison<T: PartialOrd + ?Sized>(op: FilterOp) -> Option<fn(&T, &T) -> bool> {
    Some(match op {
        FilterOp::Gt => |a, b| a > b,
        FilterOp::Gte => |a, b| a >= b,
        FilterOp::Lt => |a, b| a < b,
        FilterOp::Lte => |a, b| a <= b,
        FilterOp::Eq => |a, b| a == b,
        FilterOp::Ne => |a, b| a != b,
        _ => return None,
    })
}
