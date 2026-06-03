"""Async/sync helpers for backend-agnostic test execution.

Lets tests call ``await run(env.do_paginate(...))`` regardless of
whether the backend returns a coroutine or a plain value.
"""

from __future__ import annotations

import inspect
from typing import TypeVar


T = TypeVar("T")


async def run(result: T) -> T:
    """Await if coroutine, return directly if sync.

    Args:
        result: A value or an awaitable.

    Returns:
        The resolved value.
    """
    if inspect.isawaitable(result):
        return await result  # type: ignore[misc]
    return result


__all__ = ["run"]
