pypaginate.query.builders
=========================

.. py:module:: pypaginate.query.builders

.. autoapi-nested-parse::

   SQL query builders.

   This module provides utilities for building SQL queries:
   - count_builder: Build optimized COUNT queries



Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/pypaginate/query/builders/count_builder/index


Functions
---------

.. autoapisummary::

   pypaginate.query.builders.build_count_statement
   pypaginate.query.builders.fetch_count
   pypaginate.query.builders.strip_ordering


Package Contents
----------------

.. py:function:: build_count_statement(query: pypaginate.database.types.SelectStatement, explicit: pypaginate.database.types.CountStatement | None, *, unique: bool) -> pypaginate.database.types.CountStatement

   Build the statement used to compute the total number of rows.

   :param query: Base Select statement to count from.
   :param explicit: Optional explicit count statement (takes precedence).
   :param unique: When True, count distinct rows to remove duplicates.

   :returns: A Select statement yielding a single int value.


.. py:function:: fetch_count(session: sqlalchemy.ext.asyncio.AsyncSession, stmt: pypaginate.database.types.CountStatement) -> int
   :async:


   Execute the count statement and return an integer.

   :param session: Async SQLAlchemy session used to execute the statement.
   :param stmt: Statement returning a single integer value.

   :returns: The count coerced to int; returns 0 when no value is produced.


.. py:function:: strip_ordering(query: sqlalchemy.sql.Select[RowT]) -> sqlalchemy.sql.Select[RowT]

   Return a statement without ORDER BY clauses.

   Removing ordering ensures the COUNT aggregate is not affected by
   user-provided sorting and can be delegated efficiently by the database.

   :param query: Input SQLAlchemy Select statement.

   :returns: A new Select with ORDER BY removed.


