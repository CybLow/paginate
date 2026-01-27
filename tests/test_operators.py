"""Tests for filter operators - comprehensive coverage."""

from __future__ import annotations

import pytest

from pypaginator.filters.predicates.operators.comparison import (
    EqualityFactory,
    OrderingFactory,
    COMPARATORS,
)
from pypaginator.filters.predicates.operators.simple import (
    MembershipFactory,
    NullityFactory,
    EmptyFactory,
)
from pypaginator.filters.predicates.operators.text import TextFactory
from pypaginator.filters.predicates.operators.range import RangeFactory
from pypaginator.exceptions import FilterValidationError


class TestEqualityFactory:
    """Test EqualityFactory class."""

    def test_equality_match(self) -> None:
        """Equal values should match."""
        factory = EqualityFactory(negate=False)
        predicate = factory(5)
        assert predicate(5) is True
        assert predicate(6) is False

    def test_equality_with_string(self) -> None:
        """Should work with strings."""
        factory = EqualityFactory()
        predicate = factory("hello")
        assert predicate("hello") is True
        assert predicate("world") is False

    def test_inequality(self) -> None:
        """Negated factory should check inequality."""
        factory = EqualityFactory(negate=True)
        predicate = factory(5)
        assert predicate(5) is False
        assert predicate(6) is True

    def test_none_equality(self) -> None:
        """Should handle None values."""
        factory = EqualityFactory()
        predicate = factory(None)
        assert predicate(None) is True
        assert predicate(5) is False


class TestOrderingFactory:
    """Test OrderingFactory class."""

    def test_gt_predicate(self) -> None:
        """Greater than should work."""
        factory = OrderingFactory(name="gt", comparator=COMPARATORS["gt"])
        predicate = factory(5)
        assert predicate(6) is True
        assert predicate(5) is False
        assert predicate(4) is False

    def test_gte_predicate(self) -> None:
        """Greater than or equal should work."""
        factory = OrderingFactory(name="gte", comparator=COMPARATORS["gte"])
        predicate = factory(5)
        assert predicate(6) is True
        assert predicate(5) is True
        assert predicate(4) is False

    def test_lt_predicate(self) -> None:
        """Less than should work."""
        factory = OrderingFactory(name="lt", comparator=COMPARATORS["lt"])
        predicate = factory(5)
        assert predicate(4) is True
        assert predicate(5) is False
        assert predicate(6) is False

    def test_lte_predicate(self) -> None:
        """Less than or equal should work."""
        factory = OrderingFactory(name="lte", comparator=COMPARATORS["lte"])
        predicate = factory(5)
        assert predicate(4) is True
        assert predicate(5) is True
        assert predicate(6) is False

    def test_none_reference_raises(self) -> None:
        """Should raise on None reference."""
        factory = OrderingFactory(name="gt", comparator=COMPARATORS["gt"])
        with pytest.raises(FilterValidationError):
            factory(None)

    def test_none_candidate_returns_false(self) -> None:
        """None candidate should return False."""
        factory = OrderingFactory(name="gt", comparator=COMPARATORS["gt"])
        predicate = factory(5)
        assert predicate(None) is False


class TestMembershipFactory:
    """Test MembershipFactory class."""

    def test_in_membership(self) -> None:
        """Should check membership."""
        factory = MembershipFactory(name="in", invert=False)
        predicate = factory([1, 2, 3])
        assert predicate(2) is True
        assert predicate(5) is False

    def test_not_in_membership(self) -> None:
        """Inverted should check non-membership."""
        factory = MembershipFactory(name="nin", invert=True)
        predicate = factory([1, 2, 3])
        assert predicate(2) is False
        assert predicate(5) is True

    def test_tuple_membership(self) -> None:
        """Should work with tuples."""
        factory = MembershipFactory(name="in")
        predicate = factory((1, 2, 3))
        assert predicate(2) is True


class TestNullityFactory:
    """Test NullityFactory class."""

    def test_is_null(self) -> None:
        """Should detect null values."""
        factory = NullityFactory(expect_null=True)
        predicate = factory(True)
        assert predicate(None) is True
        assert predicate(5) is False

    def test_is_not_null(self) -> None:
        """Expect non-null should detect non-null values."""
        factory = NullityFactory(expect_null=False)
        predicate = factory(True)
        assert predicate(None) is False
        assert predicate(5) is True


class TestEmptyFactory:
    """Test EmptyFactory class."""

    def test_is_empty_list(self) -> None:
        """Should detect empty lists."""
        factory = EmptyFactory(expect_empty=True)
        predicate = factory(None)
        assert predicate([]) is True
        assert predicate([1, 2]) is False

    def test_is_empty_string(self) -> None:
        """Should detect empty strings."""
        factory = EmptyFactory(expect_empty=True)
        predicate = factory(None)
        assert predicate("") is True
        assert predicate("hello") is False

    def test_is_not_empty(self) -> None:
        """Expect non-empty should detect non-empty."""
        factory = EmptyFactory(expect_empty=False)
        predicate = factory(None)
        assert predicate([]) is False
        assert predicate([1]) is True


class TestTextFactory:
    """Test TextFactory class."""

    def test_contains_substring(self) -> None:
        """Should find substring."""
        factory = TextFactory(
            name="contains",
            matcher=lambda haystack, needle: needle in haystack,
            case_sensitive=True,
        )
        predicate = factory("ell")
        assert predicate("hello") is True
        assert predicate("world") is False

    def test_case_insensitive(self) -> None:
        """Case insensitive should match."""
        factory = TextFactory(
            name="contains",
            matcher=lambda haystack, needle: needle in haystack,
            case_sensitive=False,
        )
        predicate = factory("ELL")
        # Will be normalized to lowercase
        assert predicate("hello") is True

    def test_starts_with(self) -> None:
        """Should match prefix."""
        factory = TextFactory(
            name="starts_with",
            matcher=lambda haystack, needle: haystack.startswith(needle),
            case_sensitive=False,
        )
        predicate = factory("hel")
        assert predicate("hello") is True
        assert predicate("world") is False

    def test_ends_with(self) -> None:
        """Should match suffix."""
        factory = TextFactory(
            name="ends_with",
            matcher=lambda haystack, needle: haystack.endswith(needle),
            case_sensitive=False,
        )
        predicate = factory("llo")
        assert predicate("hello") is True
        assert predicate("world") is False

    def test_null_argument_raises(self) -> None:
        """Should raise on None argument."""
        factory = TextFactory(
            name="contains",
            matcher=lambda haystack, needle: needle in haystack,
            case_sensitive=True,
        )
        with pytest.raises(FilterValidationError):
            factory(None)


class TestRangeFactory:
    """Test RangeFactory class."""

    def test_between(self) -> None:
        """Should match values in range."""
        factory = RangeFactory(name="between")
        predicate = factory([5, 10])
        assert predicate(7) is True
        assert predicate(5) is True
        assert predicate(10) is True
        assert predicate(4) is False
        assert predicate(11) is False

    def test_none_candidate_returns_false(self) -> None:
        """None candidate should return False."""
        factory = RangeFactory(name="between")
        predicate = factory([5, 10])
        assert predicate(None) is False
