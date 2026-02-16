pypaginate.sorting.engine
=========================

.. py:module:: pypaginate.sorting.engine

.. autoapi-nested-parse::

   Sorting engine with natural ordering and tie-breaking.

   This module provides sorting services with:
   - Natural ordering with deterministic fallbacks
   - Null value positioning (first/last)
   - Reverse sorting



Attributes
----------

.. autoapisummary::

   pypaginate.sorting.engine.Nulls


Classes
-------

.. autoapisummary::

   pypaginate.sorting.engine.SortEngine


Functions
---------

.. autoapisummary::

   pypaginate.sorting.engine.create_sort_service
   pypaginate.sorting.engine.sort_items


Module Contents
---------------

.. py:class:: SortEngine

   Bases: :py:obj:`Generic`\ [\ :py:obj:`T`\ ]


   Sort items using natural ordering with deterministic fallbacks.


   .. py:method:: sort(items: list[T], sort_field: str, *, reverse: bool, nulls_position: Nulls, tie_breaker_field: str | None) -> list[T]
      :staticmethod:


      Sort items by sort_field with stable tie-breaking.

      :param items: List of items to sort (modified by index only).
      :param sort_field: Attribute name used for primary ordering.
      :param reverse: Whether to reverse the ordering.
      :param nulls_position: Where to place None values ("first"/"last").
      :param tie_breaker_field: Optional secondary attribute used for stable ordering.

      :returns: A new list with items sorted according to the provided options.



.. py:function:: create_sort_service(*, _sort_method: collections.abc.Callable[Ellipsis, list[object]] = SortEngine.sort) -> SortEngine[object]

   Return a stateless SortEngine instance.

   :param _sort_method: Sort method reference for static analyzers.

   :returns: A new SortEngine instance.


.. py:function:: sort_items(items: list[T], sort_field: str, *, reverse: bool, nulls_position: Nulls, tie_breaker_field: str | None) -> list[T]

   One-shot helper building a service and sorting items.

   :param items: List of items to sort.
   :param sort_field: Attribute name used for primary ordering.
   :param reverse: Whether to reverse the ordering.
   :param nulls_position: Where to place None values.
   :param tie_breaker_field: Optional attribute used for stable ordering.

   :returns: The sorted list of items.


.. py:data:: Nulls

   Literal type for null value positioning in sort results.

