pypaginate.domain.protocols
===========================

.. py:module:: pypaginate.domain.protocols

.. autoapi-nested-parse::

   Backend contracts (ports) for the hexagonal architecture.

   Each protocol defines the minimal interface a backend must implement.
   Protocols are generic over query type ``Q`` and item type ``T``
   for full type safety in backend implementations.



Classes
-------

.. autoapisummary::

   pypaginate.domain.protocols.CursorBackend
   pypaginate.domain.protocols.FilterBackend
   pypaginate.domain.protocols.PaginationBackend
   pypaginate.domain.protocols.SearchBackend
   pypaginate.domain.protocols.SortBackend
   pypaginate.domain.protocols.SyncPaginationBackend


Module Contents
---------------

.. py:class:: CursorBackend

   Bases: :py:obj:`Protocol`\ [\ :py:obj:`T`\ ]


   Async backend for cursor/keyset-based pagination.


   .. py:method:: fetch_page(query: object, *, limit: int, after: str | None = None, before: str | None = None) -> tuple[list[T], str | None, str | None]
      :async:


      Fetch a page: returns (items, next_cursor, prev_cursor).



.. py:class:: FilterBackend

   Bases: :py:obj:`Protocol`


   Translates filter specs to backend query conditions.


   .. py:method:: apply_filters(query: object, filters: collections.abc.Sequence[pypaginate.domain.specs.FilterSpec]) -> object

      Apply filter specifications to a query.



.. py:class:: PaginationBackend

   Bases: :py:obj:`Protocol`\ [\ :py:obj:`T`\ ]


   Async backend for offset-based pagination.


   .. py:method:: count(query: object) -> int
      :async:


      Count total items matching the query.



   .. py:method:: fetch(query: object, offset: int, limit: int) -> list[T]
      :async:


      Fetch a slice of items from the query.



.. py:class:: SearchBackend

   Bases: :py:obj:`Protocol`


   Translates search specs to backend query conditions.


   .. py:method:: apply_search(query: object, spec: pypaginate.domain.specs.SearchSpec) -> object
      :staticmethod:


      Apply search specification to a query.



.. py:class:: SortBackend

   Bases: :py:obj:`Protocol`


   Translates sort specs to backend query ordering.


   .. py:method:: apply_sorting(query: object, sorting: collections.abc.Sequence[pypaginate.domain.specs.SortSpec]) -> object
      :staticmethod:


      Apply sort specifications to a query.



.. py:class:: SyncPaginationBackend

   Bases: :py:obj:`Protocol`\ [\ :py:obj:`T`\ ]


   Sync backend for offset-based pagination.


   .. py:method:: count(query: object) -> int

      Count total items matching the query.



   .. py:method:: fetch(query: object, offset: int, limit: int) -> list[T]

      Fetch a slice of items from the query.



