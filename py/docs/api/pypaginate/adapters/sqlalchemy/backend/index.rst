pypaginate.adapters.sqlalchemy.backend
======================================

.. py:module:: pypaginate.adapters.sqlalchemy.backend

.. autoapi-nested-parse::

   Offset pagination backends for SQLAlchemy (async and sync).

   Implements ``PaginationBackend[T]`` and ``SyncPaginationBackend[T]``
   protocols using SELECT COUNT(*) for counting and OFFSET/LIMIT for fetching.



Classes
-------

.. autoapisummary::

   pypaginate.adapters.sqlalchemy.backend.SQLAlchemyBackend
   pypaginate.adapters.sqlalchemy.backend.SyncSQLAlchemyBackend


Module Contents
---------------

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



.. py:class:: SyncSQLAlchemyBackend(session: sqlalchemy.orm.Session, *, count_query: object | None = None, unique: bool = False)

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Sync offset pagination backend for SQLAlchemy.

   Satisfies ``SyncPaginationBackend[ItemT]`` protocol.

   :param session: A synchronous SQLAlchemy session.


   .. py:method:: count(query: object) -> int

      Count rows. Uses custom count query if provided.



   .. py:method:: fetch(query: object, offset: int, limit: int) -> list[ItemT]

      Fetch rows with OFFSET/LIMIT. Deduplicates if unique=True.



