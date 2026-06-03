pypaginate.adapters.memory.filters
==================================

.. py:module:: pypaginate.adapters.memory.filters

.. autoapi-nested-parse::

   In-memory filter backend with inline operator dispatch.

   Implements FilterBackend protocol for Python sequences.
   Compiles filter specs into inlined predicate closures that
   bypass operator.evaluate() method dispatch for common ops.



Classes
-------

.. autoapisummary::

   pypaginate.adapters.memory.filters.MemoryFilterBackend


Module Contents
---------------

.. py:class:: MemoryFilterBackend(registry: pypaginate.filtering.registry.OperatorRegistry | None = None)

   Filter backend for in-memory sequences.


   .. py:method:: apply_filters(query: object, filters: collections.abc.Sequence[pypaginate.domain.specs.FilterSpec]) -> object

      Apply filter specs to a sequence.

      :param query: A Python sequence of items.
      :param filters: Filter specifications to apply.

      :returns: Filtered list of items matching all specs.



