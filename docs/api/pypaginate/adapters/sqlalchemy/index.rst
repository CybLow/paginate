pypaginate.adapters.sqlalchemy
==============================

.. py:module:: pypaginate.adapters.sqlalchemy

.. autoapi-nested-parse::

   SQLAlchemy backends for pagination, filtering, sorting, and search.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/pypaginate/adapters/sqlalchemy/backend/index
   /api/pypaginate/adapters/sqlalchemy/columns/index
   /api/pypaginate/adapters/sqlalchemy/cursor/index
   /api/pypaginate/adapters/sqlalchemy/filters/index
   /api/pypaginate/adapters/sqlalchemy/search/index
   /api/pypaginate/adapters/sqlalchemy/sorting/index
   /api/pypaginate/adapters/sqlalchemy/types/index


Classes
-------

.. autoapisummary::

   pypaginate.adapters.sqlalchemy.SQLAlchemyBackend
   pypaginate.adapters.sqlalchemy.SQLAlchemyCursorBackend
   pypaginate.adapters.sqlalchemy.SQLAlchemyFilterBackend
   pypaginate.adapters.sqlalchemy.SQLAlchemySearchBackend
   pypaginate.adapters.sqlalchemy.SQLAlchemySortBackend
   pypaginate.adapters.sqlalchemy.SyncSQLAlchemyBackend
   pypaginate.adapters.sqlalchemy.SyncSQLAlchemyCursorBackend


Package Contents
----------------

.. py:class:: SQLAlchemyBackend(session: sqlalchemy.ext.asyncio.AsyncSession, *, count_query: object | None = None, unique: bool = False)

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Async offset pagination backend for SQLAlchemy.

   Satisfies ``PaginationBackend[ItemT]`` protocol.

   :param session: An async SQLAlchemy session.


   .. py:method:: count(query: object) -> int
      :async:


      Count rows. Uses custom count query if provided.



   .. py:method:: fetch(query: object, offset: int, limit: int) -> list[ItemT]
      :async:


      Fetch rows with OFFSET/LIMIT. Deduplicates if unique=True.



.. py:class:: SQLAlchemyCursorBackend(session: sqlalchemy.ext.asyncio.AsyncSession)

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Async cursor/keyset pagination backend using sqlakeyset.

   Satisfies ``CursorBackend[ItemT]`` protocol.

   :param session: An async SQLAlchemy session.


   .. py:method:: fetch_page(query: object, *, limit: int, after: str | None = None, before: str | None = None) -> tuple[list[ItemT], str | None, str | None]
      :async:


      Fetch a keyset-paginated page via sqlakeyset.

      :param query: A SQLAlchemy Select with ORDER BY.
      :param limit: Maximum items per page.
      :param after: Bookmark cursor for the next page.
      :param before: Bookmark cursor for the previous page.

      :returns: Tuple of (items, next_cursor, prev_cursor).



.. py:class:: SQLAlchemyFilterBackend

   Translates FilterSpec to SQLAlchemy WHERE clauses.

   Satisfies ``FilterBackend`` protocol.


   .. py:method:: apply_filters(query: object, filters: collections.abc.Sequence[pypaginate.domain.specs.FilterSpec]) -> object

      Apply filter specs to a SQLAlchemy Select.

      :param query: A SQLAlchemy Select statement.
      :param filters: Filter specifications to apply.

      :returns: Modified Select with WHERE clauses.



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



.. py:class:: SQLAlchemySortBackend

   Translates SortSpec to SQLAlchemy ORDER BY clauses.

   Satisfies ``SortBackend`` protocol.


   .. py:method:: apply_sorting(query: object, sorting: collections.abc.Sequence[pypaginate.domain.specs.SortSpec]) -> object
      :staticmethod:


      Apply sort specs to a SQLAlchemy Select.

      :param query: A SQLAlchemy Select statement.
      :param sorting: Sort specifications (applied in order).

      :returns: Modified Select with ORDER BY clauses.



.. py:class:: SyncSQLAlchemyBackend(session: sqlalchemy.orm.Session, *, count_query: object | None = None, unique: bool = False)

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Sync offset pagination backend for SQLAlchemy.

   Satisfies ``SyncPaginationBackend[ItemT]`` protocol.

   :param session: A synchronous SQLAlchemy session.


   .. py:method:: count(query: object) -> int

      Count rows. Uses custom count query if provided.



   .. py:method:: fetch(query: object, offset: int, limit: int) -> list[ItemT]

      Fetch rows with OFFSET/LIMIT. Deduplicates if unique=True.



.. py:class:: SyncSQLAlchemyCursorBackend(session: sqlalchemy.orm.Session)

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Sync cursor/keyset pagination backend using sqlakeyset.

   Satisfies cursor backend contract for synchronous sessions.

   :param session: A synchronous SQLAlchemy session.


   .. py:method:: fetch_page(query: object, *, limit: int, after: str | None = None, before: str | None = None) -> tuple[list[ItemT], str | None, str | None]

      Fetch a keyset-paginated page via sqlakeyset.

      :param query: A SQLAlchemy Select with ORDER BY.
      :param limit: Maximum items per page.
      :param after: Bookmark cursor for the next page.
      :param before: Bookmark cursor for the previous page.

      :returns: Tuple of (items, next_cursor, prev_cursor).



