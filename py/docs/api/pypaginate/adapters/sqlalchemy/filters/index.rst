pypaginate.adapters.sqlalchemy.filters
======================================

.. py:module:: pypaginate.adapters.sqlalchemy.filters

.. autoapi-nested-parse::

   SQLAlchemy filter backend translating FilterSpec to WHERE clauses.

   Maps each FilterOperator to a SQLAlchemy column expression builder.
   Supports AND/OR logic via ``FilterLogic``.



Classes
-------

.. autoapisummary::

   pypaginate.adapters.sqlalchemy.filters.SQLAlchemyFilterBackend


Module Contents
---------------

.. py:class:: SQLAlchemyFilterBackend

   Translates FilterSpec to SQLAlchemy WHERE clauses.

   Satisfies ``FilterBackend`` protocol.


   .. py:method:: apply_filters(query: object, filters: collections.abc.Sequence[pypaginate.domain.specs.FilterSpec]) -> object

      Apply filter specs to a SQLAlchemy Select.

      :param query: A SQLAlchemy Select statement.
      :param filters: Filter specifications to apply.

      :returns: Modified Select with WHERE clauses.



