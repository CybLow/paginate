pypaginate.engine.pipeline
==========================

.. py:module:: pypaginate.engine.pipeline

.. autoapi-nested-parse::

   Pipelines — compose filter, sort, search, then paginate.

   Separate sync and async pipelines for type safety.
   Each applies optional specs before delegating to its paginator.



Classes
-------

.. autoapisummary::

   pypaginate.engine.pipeline.AsyncPipeline
   pypaginate.engine.pipeline.SyncPipeline


Module Contents
---------------

.. py:class:: AsyncPipeline(paginator: pypaginate.engine.paginator.AsyncPaginator[ItemT], *, filter_backend: pypaginate.domain.protocols.FilterBackend | None = None, sort_backend: pypaginate.domain.protocols.SortBackend | None = None, search_backend: pypaginate.domain.protocols.SearchBackend | None = None)

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Async: filter -> sort -> search -> paginate.


   .. py:method:: execute(query: object, params: pypaginate.domain.params.OffsetParams, *, filters: collections.abc.Sequence[pypaginate.domain.specs.FilterSpec] = (), sorting: collections.abc.Sequence[pypaginate.domain.specs.SortSpec] = (), search: pypaginate.domain.specs.SearchSpec | None = None) -> Any
      :async:


      Apply specs then paginate asynchronously.

      :param query: Query object.
      :param params: Offset pagination parameters.
      :param filters: Filter specifications.
      :param sorting: Sort specifications.
      :param search: Search specification.

      :returns: Paginated result with filters/sorts applied.



.. py:class:: SyncPipeline(paginator: pypaginate.engine.paginator.Paginator[ItemT], *, filter_backend: pypaginate.domain.protocols.FilterBackend | None = None, sort_backend: pypaginate.domain.protocols.SortBackend | None = None, search_backend: pypaginate.domain.protocols.SearchBackend | None = None)

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Sync: filter -> sort -> search -> paginate.


   .. py:method:: execute(query: object, params: pypaginate.domain.params.OffsetParams, *, filters: collections.abc.Sequence[pypaginate.domain.specs.FilterSpec] = (), sorting: collections.abc.Sequence[pypaginate.domain.specs.SortSpec] = (), search: pypaginate.domain.specs.SearchSpec | None = None) -> Any

      Apply specs then paginate synchronously.

      :param query: Data source.
      :param params: Offset pagination parameters.
      :param filters: Filter specifications.
      :param sorting: Sort specifications.
      :param search: Search specification.

      :returns: Paginated result with filters/sorts applied.



