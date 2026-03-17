pypaginate.adapters.sqlalchemy.columns
======================================

.. py:module:: pypaginate.adapters.sqlalchemy.columns

.. autoapi-nested-parse::

   Column resolution for SQLAlchemy queries.

   Extracts mapped columns from ORM entities referenced in a
   SQLAlchemy Select statement, used by filters, sorting, and search.



Functions
---------

.. autoapisummary::

   pypaginate.adapters.sqlalchemy.columns.resolve_column


Module Contents
---------------

.. py:function:: resolve_column(query: sqlalchemy.sql.Select[Any], field: str) -> Any

   Resolve a field name to a SQLAlchemy column attribute.

   Inspects the query's column_descriptions to find the ORM entity,
   then resolves the field via ``getattr``.

   :param query: A SQLAlchemy Select statement.
   :param field: Dotted or simple field name (e.g., ``"name"``).

   :returns: The column attribute for use in WHERE/ORDER BY clauses.

   :raises ConfigurationError: If no entity found or field does not exist.


