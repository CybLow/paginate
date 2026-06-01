"""In-memory search engine applying SearchSpec to sequences.

Pre-normalizes tokens and compiles field accessors ONCE.
Supports weighted fields, token sort ratio, min/max limits.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypeVar

from pypaginate.domain.enums import FuzzyMode, SearchFieldMode
from pypaginate.domain.exceptions import PaginationError
from pypaginate.domain.specs import SearchSpec
from pypaginate.filtering.accessor import compile_accessor
from pypaginate.search.matching import fuzzy_score, matches_field
from pypaginate.search.parser import TokenParser
from pypaginate.text.normalize import normalize_text


# -- Optional native acceleration (paginate-core, Rust) ----------------------
# Ranked search is compute-heavy enough that the native engine beats the
# pure-Python one (benchmarked ~1.4-2.1x at 10K), unlike the lighter filter/sort
# paths where FFI marshalling dominates. Same graceful fallback as the cursor
# codec / msgspec / rapidfuzz.
try:
    from paginate_core import (  # type: ignore[import-not-found]
        search_indices as _native_search,
    )

    _HAS_NATIVE = True
except ImportError:
    _HAS_NATIVE = False

# Below this size the FFI + per-item projection overhead is not worth it.
_NATIVE_MIN_ITEMS = 1000
_NATIVE_MODES = {
    SearchFieldMode.PREFIX: "prefix",
    SearchFieldMode.CONTAINS: "contains",
    SearchFieldMode.EXACT: "exact",
}


T = TypeVar("T")


def _native_eligible(items: Sequence[object], spec: SearchSpec) -> bool:
    """Native search is used only where it is faster AND matches pure Python:
    non-fuzzy, unweighted, and large enough to amortize the FFI overhead."""
    return (
        _HAS_NATIVE
        and spec.fuzzy is FuzzyMode.EXACT
        and spec.weights is None
        and len(items) >= _NATIVE_MIN_ITEMS
    )


def _apply_native(items: Sequence[T], spec: SearchSpec) -> list[T]:
    """Rank via the native engine, then select originals by returned index."""
    items_list = list(items)
    indices = _native_search(
        items_list,
        spec.query,
        list(spec.fields),
        mode=_NATIVE_MODES[spec.mode],
        fuzzy="exact",
        threshold=spec.threshold,
        min_length=spec.min_length,
        max_results=spec.max_results,
    )
    return [items_list[i] for i in indices]


class SearchEngine:
    """Stateless engine that searches sequences by SearchSpec."""

    __slots__ = ("_parser",)

    def __init__(self) -> None:
        self._parser = TokenParser()

    def apply(self, items: Sequence[T], spec: SearchSpec) -> list[T]:
        """Filter and rank items by search relevance.

        Delegates to the native ``paginate-core`` engine when eligible
        (see :func:`_native_eligible`), else uses the pure-Python path.
        """
        if _native_eligible(items, spec):
            return _apply_native(items, spec)
        if len(spec.query.strip()) < spec.min_length:
            return list(items)
        if spec.fuzzy is FuzzyMode.TOKEN_SORT:
            norm_tokens = [normalize_text(spec.query)]
        else:
            tokens = self._parser.parse(spec.query)
            if not tokens:
                return list(items)
            norm_tokens = [normalize_text(t) for t in tokens]
        accessors = [compile_accessor(f) for f in spec.fields]
        weights = spec.weights
        fuzzy_mode = spec.fuzzy
        mode = spec.mode
        threshold = spec.threshold

        if len(accessors) == 1:
            result = _rank_single(
                items,
                norm_tokens,
                accessors[0],
                fuzzy_mode,
                mode,
                threshold,
            )
        else:
            result = _rank_multi(
                items,
                norm_tokens,
                accessors,
                spec.fields,
                weights,
                fuzzy_mode,
                mode,
                threshold,
            )
        if spec.max_results is not None:
            return result[: spec.max_results]
        return result


def _rank_single(
    items: Sequence[T],
    norm_tokens: list[str],
    accessor: Callable[[object], object],
    fuzzy_mode: FuzzyMode,
    mode: SearchFieldMode,
    threshold: int,
) -> list[T]:
    """Fast path: single field, no list alloc per item."""
    scored = []
    is_fuzzy = fuzzy_mode is not FuzzyMode.EXACT
    for item in items:
        s = _score_single(item, norm_tokens, accessor, is_fuzzy, fuzzy_mode, mode, threshold)
        if s > 0:
            scored.append((s, item))
    scored.sort(key=lambda p: p[0], reverse=True)
    return [item for _, item in scored]


def _score_single(
    item: object,
    norm_tokens: list[str],
    accessor: Callable[[object], object],
    is_fuzzy: bool,
    fuzzy_mode: FuzzyMode,
    mode: SearchFieldMode,
    threshold: int,
) -> int:
    """Score single field."""
    try:
        value = accessor(item)
    except PaginationError:
        return 0
    if not isinstance(value, str):
        return 0
    nv = normalize_text(value)
    total = 0
    for nt in norm_tokens:
        if is_fuzzy:
            s = fuzzy_score(nv, nt, threshold, fuzzy_mode)
            if s == 0:
                return 0
            total += s
        elif matches_field(nv, nt, mode):
            total += 100
        else:
            return 0
    return total


def _rank_multi(
    items: Sequence[T],
    norm_tokens: list[str],
    accessors: list[Callable[[object], object]],
    field_names: tuple[str, ...],
    weights: dict[str, float] | None,
    fuzzy_mode: FuzzyMode,
    mode: SearchFieldMode,
    threshold: int,
) -> list[T]:
    """Multi-field with optional weights."""
    is_fuzzy = fuzzy_mode is not FuzzyMode.EXACT
    scored = []
    for item in items:
        s = _score_multi(
            item,
            norm_tokens,
            accessors,
            field_names,
            weights,
            is_fuzzy,
            fuzzy_mode,
            mode,
            threshold,
        )
        if s > 0:
            scored.append((s, item))
    scored.sort(key=lambda p: p[0], reverse=True)
    return [item for _, item in scored]


def _score_multi(
    item: object,
    norm_tokens: list[str],
    accessors: list[Callable[[object], object]],
    field_names: tuple[str, ...],
    weights: dict[str, float] | None,
    is_fuzzy: bool,
    fuzzy_mode: FuzzyMode,
    mode: SearchFieldMode,
    threshold: int,
) -> int:
    """Score across multiple weighted fields."""
    pairs = _extract(item, accessors, field_names)
    if not pairs:
        return 0
    total = 0
    for nt in norm_tokens:
        best = _best_weighted(pairs, nt, weights, is_fuzzy, fuzzy_mode, mode, threshold)
        if best == 0:
            return 0
        total += best
    return total


def _extract(
    item: object,
    accessors: list[Callable[[object], object]],
    field_names: tuple[str, ...],
) -> list[tuple[str, str]]:
    """Extract and normalize field values. Returns (field_name, norm_value)."""
    result: list[tuple[str, str]] = []
    for accessor, fname in zip(accessors, field_names, strict=True):
        try:
            value = accessor(item)
        except PaginationError:
            continue
        if isinstance(value, str):
            result.append((fname, normalize_text(value)))
    return result


def _best_weighted(
    pairs: list[tuple[str, str]],
    norm_token: str,
    weights: dict[str, float] | None,
    is_fuzzy: bool,
    fuzzy_mode: FuzzyMode,
    mode: SearchFieldMode,
    threshold: int,
) -> int:
    """Best weighted score across fields."""
    best = 0
    for fname, nv in pairs:
        w = weights.get(fname, 1.0) if weights else 1.0
        if is_fuzzy:
            raw = fuzzy_score(nv, norm_token, threshold, fuzzy_mode)
            best = max(best, int(raw * w))
        elif matches_field(nv, norm_token, mode):
            return int(100 * w)
    return best


__all__ = ["SearchEngine"]
