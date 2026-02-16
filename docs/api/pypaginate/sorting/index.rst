pypaginate.sorting
==================

.. py:module:: pypaginate.sorting

.. autoapi-nested-parse::

   Sorting utilities.

   This module provides sorting services with:
   - Natural ordering with deterministic tie-breaking
   - Null value positioning (first/last)
   - Reverse sorting

   Public API
   ----------
   SortEngine
       Generic sorting service for collections.
   sort_items
       One-shot function to sort items.
   create_sort_service
       Factory function to create SortEngine instances.
   SqlSortAdapter
       SQL-specific sort adapter for building SQLAlchemy ORDER BY clauses.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/pypaginate/sorting/engine/index
   /api/pypaginate/sorting/sql_adapter/index


Attributes
----------

.. autoapisummary::

   pypaginate.sorting.Nulls


Classes
-------

.. autoapisummary::

   pypaginate.sorting.SortEngine
   pypaginate.sorting.SqlSortAdapter


Functions
---------

.. autoapisummary::

   pypaginate.sorting.create_sort_service
   pypaginate.sorting.sort_items


Package Contents
----------------

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



.. py:class:: SqlSortAdapter

   Build SQLAlchemy ORDER BY clauses from sort specifications.

   This adapter translates high-level sort specifications into
   SQLAlchemy order by expressions with proper null handling.


   .. py:method:: build_order_expression(column: sqlalchemy.orm.InstrumentedAttribute[Any], descending: bool = False, nulls_position: str | None = None) -> sqlalchemy.sql.elements.UnaryExpression[Any]
      :staticmethod:


      Build a SQLAlchemy ORDER BY expression.

      :param column: SQLAlchemy column to sort by
      :param descending: Whether to sort in descending order
      :param nulls_position: Where to place NULL values ("first" or "last")

      :returns: SQLAlchemy order by expression



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

