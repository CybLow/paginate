pypaginate.adapters.sqlalchemy.sorting
======================================

.. py:module:: pypaginate.adapters.sqlalchemy.sorting

.. autoapi-nested-parse::

   SQLAlchemy sort backend translating SortSpec to ORDER BY clauses.

   Maps SortDirection and NullsPosition to SQLAlchemy column modifiers.



Classes
-------

.. autoapisummary::

   pypaginate.adapters.sqlalchemy.sorting.SQLAlchemySortBackend


Module Contents
---------------

.. py:class:: SQLAlchemySortBackend

   Translates SortSpec to SQLAlchemy ORDER BY clauses.

   Satisfies ``SortBackend`` protocol.


   .. py:method:: apply_sorting(query: object, sorting: collections.abc.Sequence[pypaginate.domain.specs.SortSpec]) -> object
      :staticmethod:


      Apply sort specs to a SQLAlchemy Select.

      :param query: A SQLAlchemy Select statement.
      :param sorting: Sort specifications (applied in order).

      :returns: Modified Select with ORDER BY clauses.



