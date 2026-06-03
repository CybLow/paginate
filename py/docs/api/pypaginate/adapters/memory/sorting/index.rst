pypaginate.adapters.memory.sorting
==================================

.. py:module:: pypaginate.adapters.memory.sorting

.. autoapi-nested-parse::

   In-memory sort backend with partition-sort strategy.

   Implements SortBackend protocol for Python sequences.
   Partitions nulls from non-nulls, sorts non-nulls with a plain
   key (no tuple wrapping), then concatenates for null placement.



Classes
-------

.. autoapisummary::

   pypaginate.adapters.memory.sorting.MemorySortBackend


Module Contents
---------------

.. py:class:: MemorySortBackend

   Sort backend for in-memory sequences.


   .. py:method:: apply_sorting(query: object, sorting: collections.abc.Sequence[pypaginate.domain.specs.SortSpec]) -> object
      :staticmethod:


      Apply sort specs to a sequence.

      :param query: A Python sequence of items.
      :param sorting: Sort specifications (applied in order).

      :returns: New sorted list of items.



