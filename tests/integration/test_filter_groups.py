"""FilterGroup integration tests via memory backend."""

from __future__ import annotations

from pypaginate import FilterSpec, OffsetParams
from pypaginate.domain.specs import And, Or
from pypaginate.filtering.engine import FilterEngine
from tests.fixtures.backends import SEED_DATA, setup_memory
from tests.fixtures.helpers import run


async def test_and_group_narrows_results() -> None:
    """And() group returns only items matching all conditions."""
    await setup_memory()
    engine = FilterEngine()
    group = And(
        FilterSpec(field="name", operator="contains", value="a"),
        FilterSpec(field="name", operator="contains", value="e"),
    )

    result = engine.apply(list(SEED_DATA), group)

    names = {item["name"] for item in result}
    for name in names:
        assert "a" in name.lower() and "e" in name.lower()


async def test_or_group_widens_results() -> None:
    """Or() group returns items matching any condition."""
    engine = FilterEngine()
    group = Or(
        FilterSpec(field="name", operator="eq", value="Alice"),
        FilterSpec(field="name", operator="eq", value="Bob"),
    )

    result = engine.apply(list(SEED_DATA), group)

    names = {item["name"] for item in result}
    assert names == {"Alice", "Bob"}


async def test_nested_and_or_groups() -> None:
    """Nested And(Or(...), spec) combines logic correctly."""
    engine = FilterEngine()
    group = And(
        Or(
            FilterSpec(field="name", operator="eq", value="Alice"),
            FilterSpec(field="name", operator="eq", value="Bob"),
            FilterSpec(field="name", operator="eq", value="Charlie"),
        ),
        FilterSpec(field="age", operator="gte", value=30),
    )

    result = engine.apply(list(SEED_DATA), group)

    names = {item["name"] for item in result}
    assert names == {"Alice", "Charlie"}
    for item in result:
        assert item["age"] >= 30


async def test_and_group_through_pipeline() -> None:
    """And() filters work end-to-end via memory pipeline."""
    env = await setup_memory()
    page = await run(
        env.do_pipeline(
            env.query,
            OffsetParams(page=1, limit=100),
            filters=[
                FilterSpec(field="name", operator="eq", value="Alice"),
            ],
        )
    )

    assert page.total == 1
    assert len(page.items) == 1
    assert env.get_field(page.items[0], "name") == "Alice"


async def test_or_group_no_match_returns_empty() -> None:
    """Or() group with no matching conditions returns empty."""
    engine = FilterEngine()
    group = Or(
        FilterSpec(field="name", operator="eq", value="NoOne"),
        FilterSpec(field="name", operator="eq", value="Nobody"),
    )

    result = engine.apply(list(SEED_DATA), group)

    assert result == []


async def test_deeply_nested_groups() -> None:
    """Multiple nesting levels resolve correctly."""
    engine = FilterEngine()
    group = And(
        Or(
            And(
                FilterSpec(field="age", operator="gte", value=30),
                FilterSpec(field="age", operator="lte", value=35),
            ),
            FilterSpec(field="name", operator="eq", value="Bob"),
        ),
    )

    result = engine.apply(list(SEED_DATA), group)

    names = {item["name"] for item in result}
    assert "Bob" in names
    for item in result:
        if item["name"] != "Bob":
            assert 30 <= item["age"] <= 35
