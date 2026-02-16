pypaginate.engines.sql
======================

.. py:module:: pypaginate.engines.sql

.. autoapi-nested-parse::

   SQLAlchemy pagination orchestrator.



Classes
-------

.. autoapisummary::

   pypaginate.engines.sql.KeysetPaginationSnapshot
   pypaginate.engines.sql.PaginationSnapshot
   pypaginate.engines.sql.SqlPaginator


Functions
---------

.. autoapisummary::

   pypaginate.engines.sql.get_pagination_strategy


Module Contents
---------------

.. py:class:: KeysetPaginationSnapshot

   Bases: :py:obj:`Generic`\ [\ :py:obj:`KeysetItemT`\ ]


   Immutable snapshot produced by keyset pagination.

   Stores the materialized items alongside the original parameters and the
   serialized bookmarks required to navigate to adjacent pages.

   .. attribute:: items

      Materialized list of payload items for the current page.

   .. attribute:: params

      Parameters used to compute the current page.

   .. attribute:: next

      Serialized bookmark to retrieve the next page, if available.

   .. attribute:: previous

      Serialized bookmark to retrieve the previous page, if available.

   .. attribute:: current

      Serialized bookmark pointing to the current page position.


.. py:class:: PaginationSnapshot

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ , :py:obj:`ParamsT`\ ]


   Immutable snapshot returned by the paginator.

   .. attribute:: items

      Materialized items for the current page.

   .. attribute:: total

      Total number of rows matching the base query.

   .. attribute:: params

      Effective parameters used to compute the page.


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



.. py:function:: get_pagination_strategy(name: str) -> collections.abc.Callable[Ellipsis, collections.abc.Awaitable[object]]

   Return the paginator method associated with name.

   :param name: Strategy identifier ("offset" or "keyset").

   :returns: The bound coroutine function implementing the strategy.

   :raises PaginationConfigurationError: When name is unknown.


