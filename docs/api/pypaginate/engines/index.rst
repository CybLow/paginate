pypaginate.engines
==================

.. py:module:: pypaginate.engines

.. autoapi-nested-parse::

   Pagination engines for different strategies.

   This module provides the core pagination engines:
   - MemoryPaginator: In-memory pagination
   - SqlPaginator: SQL-based pagination

   Each engine implements a specific pagination strategy.
   Note: Keyset pagination is handled directly by SqlPaginator.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/pypaginate/engines/keyset/index
   /api/pypaginate/engines/memory/index
   /api/pypaginate/engines/sql/index


Classes
-------

.. autoapisummary::

   pypaginate.engines.MemoryPaginator
   pypaginate.engines.SqlPaginator


Functions
---------

.. autoapisummary::

   pypaginate.engines.filter_iter


Package Contents
----------------

.. py:class:: MemoryPaginator(*, clamp: bool = False)

   Bases: :py:obj:`Generic`\ [\ :py:obj:`T`\ ]


   Paginate sequences or iterables while preserving streaming semantics.


   .. py:method:: paginate(items: collections.abc.Iterable[T], params: pypaginate.core.PageParams, predicate: collections.abc.Callable[[T], bool] | None = None) -> pypaginate.core.Page[T]

      Paginate a sequence or iterable.

      :param items: Iterable of items to paginate.
      :param params: Page parameters.
      :param predicate: Optional filter predicate.

      :returns: A Page object with the requested window.



.. py:class:: SqlPaginator(session: sqlalchemy.ext.asyncio.AsyncSession, *, clamp: bool)

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Transform a SQLAlchemy statement into a paginated payload.

   The paginator supports both offset-based and keyset-based strategies and
   provides helpers to materialize results, compute counts, and clamp
   parameters.


   .. py:method:: paginate(query: pypaginate.database.types.SelectStatement, context: pypaginate.core.context.PaginationContext[ParamsT], *, scalars: bool) -> pypaginate.core.snapshots.PaginationSnapshot[ItemT, ParamsT]
      :async:


      Paginate a statement using the offset strategy.

      :param query: Statement to paginate.
      :param context: Execution context carrying parameters and options.
      :param scalars: Whether to select scalar results (ORM entities otherwise).

      :returns: A PaginationSnapshot with materialized items and metadata.



   .. py:method:: paginate_keyset(query: pypaginate.database.types.SelectStatement, params: pypaginate.core.pages.KeysetPageParams, *, unique: bool, scalars: bool = True) -> pypaginate.core.snapshots.KeysetPaginationSnapshot[ItemT]
      :async:


      Paginate a statement using the keyset strategy.

      :param query: Statement to paginate.
      :param params: Keyset-specific parameters (limit and bookmarks).
      :param unique: Whether to deduplicate rows before pagination.
      :param scalars: Whether to coerce rows to scalars when possible.

      :returns: A KeysetPaginationSnapshot with items and markers.



.. py:function:: filter_iter(items: collections.abc.Iterable[T], predicate: collections.abc.Callable[[T], bool] | None) -> collections.abc.Iterator[T]

   Yield items that satisfy an optional predicate.

   :param items: Iterable of items to iterate over.
   :param predicate: Optional predicate applied to each item.

   :returns: An iterator yielding items for which ``predicate(item)`` is ``True``.
             When ``predicate`` is ``None``, yields all items.


