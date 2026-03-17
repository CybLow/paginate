pypaginate.engine.paginator
===========================

.. py:module:: pypaginate.engine.paginator

.. autoapi-nested-parse::

   Sync and async paginators for offset-based pagination.

   Each paginator owns the pipeline: count -> clamp -> fetch -> OffsetPage.



Classes
-------

.. autoapisummary::

   pypaginate.engine.paginator.AsyncPaginator
   pypaginate.engine.paginator.Paginator


Module Contents
---------------

.. py:class:: AsyncPaginator(backend: pypaginate.domain.protocols.PaginationBackend[ItemT], *, overflow: pypaginate.domain.enums.OverflowStrategy = OverflowStrategy.EMPTY)

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Async orchestrator: count -> clamp -> fetch -> OffsetPage.


   .. py:method:: paginate(query: object, params: pypaginate.domain.params.OffsetParams) -> Any
      :async:


      Execute the async pagination pipeline.

      :param query: Backend-specific query object.
      :param params: Offset pagination parameters.

      :returns: OffsetPage (or FastOffsetPage if msgspec installed).



.. py:class:: Paginator(backend: pypaginate.domain.protocols.SyncPaginationBackend[ItemT], *, overflow: pypaginate.domain.enums.OverflowStrategy = OverflowStrategy.EMPTY)

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Sync orchestrator: count -> clamp -> fetch -> OffsetPage.


   .. py:method:: paginate(query: object, params: pypaginate.domain.params.OffsetParams) -> Any

      Execute the sync pagination pipeline.

      :param query: Backend-specific query or data source.
      :param params: Offset pagination parameters.

      :returns: OffsetPage (or FastOffsetPage if msgspec installed).



