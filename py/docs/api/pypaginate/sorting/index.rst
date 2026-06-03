pypaginate.sorting
==================

.. py:module:: pypaginate.sorting

.. autoapi-nested-parse::

   Universal sorting -- backend-agnostic sort engine.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/pypaginate/sorting/engine/index
   /api/pypaginate/sorting/keys/index


Classes
-------

.. autoapisummary::

   pypaginate.sorting.SortEngine


Package Contents
----------------

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



