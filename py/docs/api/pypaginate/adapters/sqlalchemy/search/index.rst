pypaginate.adapters.sqlalchemy.search
=====================================

.. py:module:: pypaginate.adapters.sqlalchemy.search

.. autoapi-nested-parse::

   SQLAlchemy search backend translating SearchSpec to ILIKE clauses.

   Combines field conditions with OR (any field matches) and
   token conditions with AND (all tokens must match).



Classes
-------

.. autoapisummary::

   pypaginate.adapters.sqlalchemy.search.SQLAlchemySearchBackend


Module Contents
---------------

.. py:class:: SQLAlchemySearchBackend

   Translates SearchSpec to SQLAlchemy ILIKE clauses.

   Satisfies ``SearchBackend`` protocol. Tokenizes the query
   and matches each token against all specified fields.


   .. py:method:: apply_search(query: object, spec: pypaginate.domain.specs.SearchSpec) -> object
      :staticmethod:


      Apply a search spec to a SQLAlchemy Select.

      :param query: A SQLAlchemy Select statement.
      :param spec: Search specification with query and fields.

      :returns: Modified Select with WHERE clauses for search.



