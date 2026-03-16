pypaginate.adapters.memory
==========================

.. py:module:: pypaginate.adapters.memory

.. autoapi-nested-parse::

   In-memory backends for pagination, filtering, sorting, and search.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/pypaginate/adapters/memory/backend/index
   /api/pypaginate/adapters/memory/filters/index
   /api/pypaginate/adapters/memory/search/index
   /api/pypaginate/adapters/memory/sorting/index


Classes
-------

.. autoapisummary::

   pypaginate.adapters.memory.MemoryBackend
   pypaginate.adapters.memory.MemoryFilterBackend
   pypaginate.adapters.memory.MemorySearchBackend
   pypaginate.adapters.memory.MemorySortBackend


Package Contents
----------------

.. py:class:: MemoryBackend

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Sync pagination backend for in-memory sequences.

   Counts via ``len()`` and fetches via slicing.
   Satisfies ``SyncPaginationBackend[ItemT]`` protocol.


   .. py:method:: count(query: object) -> int

      Count items in a sequence.

      :param query: A Python sequence (list, tuple, etc.).

      :returns: Number of items.

      :raises TypeError: If query is not a Sequence.



   .. py:method:: fetch(query: object, offset: int, limit: int) -> list[ItemT]

      Fetch a slice of items from a sequence.

      :param query: A Python sequence.
      :param offset: Start index.
      :param limit: Maximum items to return.

      :returns: List of items for the requested slice.

      :raises TypeError: If query is not a Sequence.



.. py:class:: MemoryFilterBackend(registry: pypaginate.filtering.registry.OperatorRegistry | None = None)

   Filter backend for in-memory sequences.


   .. py:method:: apply_filters(query: object, filters: collections.abc.Sequence[pypaginate.domain.specs.FilterSpec]) -> object

      Apply filter specs to a sequence.

      :param query: A Python sequence of items.
      :param filters: Filter specifications to apply.

      :returns: Filtered list of items matching all specs.



.. py:class:: MemorySearchBackend

   Search backend for in-memory sequences.


   .. py:method:: apply_search(query: object, spec: pypaginate.domain.specs.SearchSpec) -> object
      :staticmethod:


      Apply a search spec to a sequence.

      :param query: A Python sequence of items.
      :param spec: Search specification with query and fields.

      :returns: Filtered list of items matching the search.



.. py:class:: MemorySortBackend

   Sort backend for in-memory sequences.


   .. py:method:: apply_sorting(query: object, sorting: collections.abc.Sequence[pypaginate.domain.specs.SortSpec]) -> object
      :staticmethod:


      Apply sort specs to a sequence.

      :param query: A Python sequence of items.
      :param sorting: Sort specifications (applied in order).

      :returns: New sorted list of items.



