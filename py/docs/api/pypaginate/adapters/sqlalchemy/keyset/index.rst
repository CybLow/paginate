pypaginate.adapters.sqlalchemy.keyset
=====================================

.. py:module:: pypaginate.adapters.sqlalchemy.keyset

.. autoapi-nested-parse::

   Keyset pagination WHERE clause builder.

   Constructs the lexicographic comparison needed for cursor/keyset
   pagination directly from SQLAlchemy column expressions.
   No external dependencies -- pure SQLAlchemy 2.0 API.



Classes
-------

.. autoapisummary::

   pypaginate.adapters.sqlalchemy.keyset.OrderColumn


Functions
---------

.. autoapisummary::

   pypaginate.adapters.sqlalchemy.keyset.build_keyset_condition
   pypaginate.adapters.sqlalchemy.keyset.extract_order_columns


Module Contents
---------------

.. py:class:: OrderColumn(element: sqlalchemy.sql.elements.ColumnElement[Any], *, is_ascending: bool)

   Parsed ORDER BY column with direction metadata.


   .. py:property:: order_clause
      :type: Any


      Return the SQLAlchemy asc/desc expression for ORDER BY.


   .. py:property:: reversed
      :type: OrderColumn


      Return a copy with flipped direction.


.. py:function:: build_keyset_condition(columns: list[OrderColumn], cursor_values: tuple[Any, Ellipsis]) -> Any

   Build the WHERE clause for keyset pagination.

   For ``ORDER BY (a ASC, b DESC)`` with cursor ``(v1, v2)``::

       WHERE (a > v1) OR (a = v1 AND b < v2)

   Uses the conjunction-at-top-level form for optimizer friendliness.

   :param columns: Parsed ORDER BY columns.
   :param cursor_values: Tuple of values matching each column.

   :returns: A SQLAlchemy boolean expression.

   :raises ConfigurationError: If columns/values count mismatch.


.. py:function:: extract_order_columns(query: sqlalchemy.sql.Select[Any]) -> list[OrderColumn]

   Extract ORDER BY columns from a Select statement.

   Unwraps ``UnaryExpression`` (asc/desc wrappers) to get the bare
   column element and its sort direction.  Bare columns (no explicit
   direction) default to ascending.

   :param query: A SQLAlchemy Select with an ORDER BY clause.

   :returns: Ordered list of ``OrderColumn`` objects.

   :raises ConfigurationError: If the query has no ORDER BY clause.


