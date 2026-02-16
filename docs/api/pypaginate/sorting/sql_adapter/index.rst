pypaginate.sorting.sql_adapter
==============================

.. py:module:: pypaginate.sorting.sql_adapter

.. autoapi-nested-parse::

   SQL adapter for sorting operations.

   This module provides SQL-specific sorting capabilities that complement
   the in-memory sorting engine.



Classes
-------

.. autoapisummary::

   pypaginate.sorting.sql_adapter.SqlSortAdapter


Module Contents
---------------

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



