pypaginate.filters.sql_adapter
==============================

.. py:module:: pypaginate.filters.sql_adapter

.. autoapi-nested-parse::

   SQL adapter for filter operations.

   Provides SQL-specific filtering capabilities for repositories.



Classes
-------

.. autoapisummary::

   pypaginate.filters.sql_adapter.SqlFilterAdapter


Module Contents
---------------

.. py:class:: SqlFilterAdapter

   Build SQLAlchemy filter conditions from operator specifications.


   .. py:method:: build_condition(column: sqlalchemy.orm.InstrumentedAttribute[Any], operator: str, value: object) -> sqlalchemy.sql.elements.ColumnElement[bool]
      :staticmethod:


      Build a SQLAlchemy filter condition.



   .. py:method:: combine_conditions(conditions: list[sqlalchemy.sql.elements.ColumnElement[bool]], logic: str = 'and') -> sqlalchemy.sql.elements.ColumnElement[bool]
      :staticmethod:


      Combine multiple conditions with AND or OR logic.



