"""Tests for JSON Logic evaluator."""

from __future__ import annotations

from pypaginate.filters.predicates.jsonlogic_evaluator import (
    evaluate_json_logic_rule,
)


class TestEvaluateJsonLogicRule:
    """Test evaluate_json_logic_rule function."""

    def test_true_literal(self) -> None:
        """True should return True."""
        result = evaluate_json_logic_rule(True, {})
        assert result is True

    def test_false_literal(self) -> None:
        """False should return False."""
        result = evaluate_json_logic_rule(False, {})
        assert result is False

    def test_var_access(self) -> None:
        """Should access variable from context."""
        rule = {"var": "name"}
        context = {"name": "John"}
        result = evaluate_json_logic_rule(rule, context)
        assert result == "John"

    def test_var_nested_access(self) -> None:
        """Should access nested variable."""
        rule = {"var": "user.name"}
        context = {"user": {"name": "John"}}
        result = evaluate_json_logic_rule(rule, context)
        assert result == "John"

    def test_and_operator(self) -> None:
        """AND should combine conditions."""
        rule = {"and": [True, True]}
        result = evaluate_json_logic_rule(rule, {})
        assert result is True

        rule = {"and": [True, False]}
        result = evaluate_json_logic_rule(rule, {})
        assert result is False

    def test_or_operator(self) -> None:
        """OR should combine conditions."""
        rule = {"or": [True, False]}
        result = evaluate_json_logic_rule(rule, {})
        assert result is True

        rule = {"or": [False, False]}
        result = evaluate_json_logic_rule(rule, {})
        assert result is False

    def test_not_operator(self) -> None:
        """NOT should negate."""
        rule = {"!": True}
        result = evaluate_json_logic_rule(rule, {})
        assert result is False

        rule = {"!": False}
        result = evaluate_json_logic_rule(rule, {})
        assert result is True

    def test_complex_nested(self) -> None:
        """Should handle nested rules."""
        rule = {
            "and": [
                {"var": "active"},
                {">": [{"var": "age"}, 18]},
            ]
        }
        context = {"active": True, "age": 25}
        result = evaluate_json_logic_rule(rule, context)
        assert result is True

        context = {"active": True, "age": 15}
        result = evaluate_json_logic_rule(rule, context)
        assert result is False
