pypaginate.sorting.engine
=========================

.. py:module:: pypaginate.sorting.engine

.. autoapi-nested-parse::

   In-memory sort engine applying SortSpec sequences.

   Applies multiple sort specifications in priority order using
   Python's stable sort guarantee. Each spec controls direction
   and null placement independently.



Classes
-------

.. autoapisummary::

   pypaginate.sorting.engine.SortEngine


Module Contents
---------------

.. py:class:: SortEngine

   Stateless engine that sorts sequences by SortSpec rules.

   Uses Python's stable sort: applies specs in reverse order
   so the first spec has highest priority.


   .. py:method:: apply(items: collections.abc.Sequence[T], sorting: collections.abc.Sequence[pypaginate.domain.specs.SortSpec]) -> list[T]

      Sort items according to the given sort specifications.

      :param items: Input sequence to sort.
      :param sorting: Sort specs in priority order (first = highest).

      :returns: New sorted list (original unchanged).

      :raises SortError: If sorting fails for any reason.



