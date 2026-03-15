"""Tests for all 17 filter operators using parametrize."""

from __future__ import annotations

import pytest

from pypaginate.domain.exceptions import FilterValidationError
from pypaginate.filtering.operators import Between
from pypaginate.filtering.registry import OperatorRegistry


# -- Comparison operators ----------------------------------------------------


@pytest.mark.parametrize(
    ("op_name", "field_val", "spec_val", "expected"),
    [
        ("eq", 42, 42, True),
        ("eq", 42, 99, False),
        ("eq", "alice", "alice", True),
        ("eq", "alice", "bob", False),
        ("ne", 1, 2, True),
        ("ne", 1, 1, False),
        ("gt", 10, 5, True),
        ("gt", 5, 10, False),
        ("gt", 5, 5, False),
        ("gte", 10, 5, True),
        ("gte", 5, 5, True),
        ("gte", 4, 5, False),
        ("lt", 3, 5, True),
        ("lt", 5, 3, False),
        ("lt", 5, 5, False),
        ("lte", 3, 5, True),
        ("lte", 5, 5, True),
        ("lte", 6, 5, False),
    ],
    ids=lambda v: str(v),
)
def test_comparison_operator(
    filter_registry: OperatorRegistry,
    op_name: str,
    field_val: object,
    spec_val: object,
    expected: bool,
) -> None:
    op = filter_registry.get(op_name)

    result = op.evaluate(field_val, spec_val)

    assert result is expected, f"{op_name}({field_val}, {spec_val})"


# -- Membership operators ----------------------------------------------------


@pytest.mark.parametrize(
    ("op_name", "field_val", "spec_val", "expected"),
    [
        ("in", "a", ["a", "b", "c"], True),
        ("in", "z", ["a", "b"], False),
        ("in", 1, [1, 2, 3], True),
        ("not_in", "z", ["a", "b"], True),
        ("not_in", "a", ["a", "b"], False),
    ],
    ids=lambda v: str(v),
)
def test_membership_operator(
    filter_registry: OperatorRegistry,
    op_name: str,
    field_val: object,
    spec_val: object,
    expected: bool,
) -> None:
    op = filter_registry.get(op_name)

    result = op.evaluate(field_val, spec_val)

    assert result is expected, f"{op_name}({field_val}, {spec_val})"


# -- String operators --------------------------------------------------------


@pytest.mark.parametrize(
    ("op_name", "field_val", "spec_val", "expected"),
    [
        ("contains", "hello world", "world", True),
        ("contains", "hello", "xyz", False),
        ("contains", "hello", "", True),
        ("starts_with", "hello world", "hello", True),
        ("starts_with", "hello", "world", False),
        ("ends_with", "hello world", "world", True),
        ("ends_with", "hello world", "hello", False),
    ],
    ids=lambda v: str(v),
)
def test_string_operator(
    filter_registry: OperatorRegistry,
    op_name: str,
    field_val: str,
    spec_val: str,
    expected: bool,
) -> None:
    op = filter_registry.get(op_name)

    result = op.evaluate(field_val, spec_val)

    assert result is expected, f"{op_name}({field_val!r}, {spec_val!r})"


# -- Pattern operators -------------------------------------------------------


@pytest.mark.parametrize(
    ("op_name", "field_val", "spec_val", "expected"),
    [
        ("like", "hello", "%llo", True),
        ("like", "hello", "%xyz", False),
        ("like", "hat", "h_t", True),
        ("ilike", "HELLO", "%llo", True),
        ("ilike", "HELLO", "%xyz", False),
        ("regex", "abc123", r"\d+", True),
        ("regex", "abc", r"\d+", False),
        ("regex", "user@example.com", r".+@.+\..+", True),
    ],
    ids=lambda v: str(v),
)
def test_pattern_operator(
    filter_registry: OperatorRegistry,
    op_name: str,
    field_val: str,
    spec_val: str,
    expected: bool,
) -> None:
    op = filter_registry.get(op_name)

    result = op.evaluate(field_val, spec_val)

    assert result is expected, f"{op_name}({field_val!r}, {spec_val!r})"


# -- Between operator --------------------------------------------------------


@pytest.mark.parametrize(
    ("field_val", "spec_val", "expected"),
    [
        (5, [1, 10], True),
        (1, [1, 10], True),
        (10, [1, 10], True),
        (15, [1, 10], False),
        (0, [1, 10], False),
    ],
    ids=["in_range", "low_boundary", "high_boundary", "above", "below"],
)
def test_between_operator(
    filter_registry: OperatorRegistry,
    field_val: int,
    spec_val: list[int],
    expected: bool,
) -> None:
    op = filter_registry.get("between")

    result = op.evaluate(field_val, spec_val)

    assert result is expected


def test_between_with_invalid_pair_raises() -> None:
    with pytest.raises(FilterValidationError, match="2 elements"):
        Between().evaluate(5, [1, 2, 3])


# -- Null operators ----------------------------------------------------------


@pytest.mark.parametrize(
    ("op_name", "field_val", "expected"),
    [
        ("is_null", None, True),
        ("is_null", "hello", False),
        ("is_null", 0, False),
        ("is_null", "", False),
        ("is_not_null", "hello", True),
        ("is_not_null", None, False),
        ("is_not_null", 0, True),
    ],
    ids=lambda v: str(v),
)
def test_null_operator(
    filter_registry: OperatorRegistry,
    op_name: str,
    field_val: object,
    expected: bool,
) -> None:
    op = filter_registry.get(op_name)

    result = op.evaluate(field_val, None)

    assert result is expected, f"{op_name}({field_val!r})"
