pypaginate.adapters.memory.backend
==================================

.. py:module:: pypaginate.adapters.memory.backend

.. autoapi-nested-parse::

   In-memory pagination backend.

   Implements SyncPaginationBackend for Python sequences.
   Validates input type at runtime for clear error messages.



Classes
-------

.. autoapisummary::

   pypaginate.adapters.memory.backend.MemoryBackend


Module Contents
---------------

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



