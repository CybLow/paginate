pypaginate.adapters.sqlalchemy.cursor
=====================================

.. py:module:: pypaginate.adapters.sqlalchemy.cursor

.. autoapi-nested-parse::

   Cursor/keyset pagination backends (async and sync).

   Implements ``CursorBackend[T]`` protocol using built-in cursor
   encoding and keyset WHERE clause construction. Requires the query
   to have an ORDER BY clause.



Classes
-------

.. autoapisummary::

   pypaginate.adapters.sqlalchemy.cursor.SQLAlchemyCursorBackend
   pypaginate.adapters.sqlalchemy.cursor.SyncSQLAlchemyCursorBackend


Module Contents
---------------

.. py:class:: SQLAlchemyCursorBackend(session: sqlalchemy.ext.asyncio.AsyncSession)

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Async cursor/keyset pagination backend.

   Satisfies ``CursorBackend[ItemT]`` protocol.

   :param session: An async SQLAlchemy session.


   .. py:method:: fetch_page(query: sqlalchemy.sql.Select[Any], *, limit: int, after: str | None = None, before: str | None = None) -> tuple[list[ItemT], str | None, str | None]
      :async:


      Fetch a keyset-paginated page.

      :param query: A SQLAlchemy Select with ORDER BY.
      :param limit: Maximum items per page.
      :param after: Cursor for the next page.
      :param before: Cursor for the previous page.

      :returns: Tuple of (items, next_cursor, prev_cursor).



.. py:class:: SyncSQLAlchemyCursorBackend(session: sqlalchemy.orm.Session)

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Sync cursor/keyset pagination backend.

   Satisfies cursor backend contract for synchronous sessions.

   :param session: A synchronous SQLAlchemy session.


   .. py:method:: fetch_page(query: sqlalchemy.sql.Select[Any], *, limit: int, after: str | None = None, before: str | None = None) -> tuple[list[ItemT], str | None, str | None]

      Fetch a keyset-paginated page.

      :param query: A SQLAlchemy Select with ORDER BY.
      :param limit: Maximum items per page.
      :param after: Cursor for the next page.
      :param before: Cursor for the previous page.

      :returns: Tuple of (items, next_cursor, prev_cursor).



