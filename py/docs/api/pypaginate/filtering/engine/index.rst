pypaginate.filtering.engine
===========================

.. py:module:: pypaginate.filtering.engine

.. autoapi-nested-parse::

   Filter engine applying filter specs to in-memory sequences.

   Compiles filter specs into fast predicate closures ONCE,
   then applies them N times without per-item overhead.



Classes
-------

.. autoapisummary::

   pypaginate.filtering.engine.FilterEngine


Module Contents
---------------

.. py:class:: FilterEngine(registry: pypaginate.filtering.registry.OperatorRegistry)

   Apply filter specifications to in-memory sequences.

   :param registry: Operator registry for looking up operators.


   .. py:method:: apply(items: collections.abc.Sequence[T], filters: collections.abc.Sequence[pypaginate.domain.specs.FilterSpec] | pypaginate.domain.specs.FilterGroup) -> list[T]

      Apply filters to items. Accepts flat list or nested FilterGroup.

      :param items: Source sequence to filter.
      :param filters: FilterSpec list or FilterGroup (via And/Or builders).

      :returns: Filtered list of items matching all specs.



