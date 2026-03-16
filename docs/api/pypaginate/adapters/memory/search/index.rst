pypaginate.adapters.memory.search
=================================

.. py:module:: pypaginate.adapters.memory.search

.. autoapi-nested-parse::

   In-memory search backend delegating to text normalization.

   Implements SearchBackend protocol for Python sequences.
   Pre-normalizes the query and compiles field accessors ONCE.
   Compiles a single match function to minimize per-item overhead.



Classes
-------

.. autoapisummary::

   pypaginate.adapters.memory.search.MemorySearchBackend


Module Contents
---------------

.. py:class:: MemorySearchBackend

   Search backend for in-memory sequences.


   .. py:method:: apply_search(query: object, spec: pypaginate.domain.specs.SearchSpec) -> object
      :staticmethod:


      Apply a search spec to a sequence.

      :param query: A Python sequence of items.
      :param spec: Search specification with query and fields.

      :returns: Filtered list of items matching the search.



