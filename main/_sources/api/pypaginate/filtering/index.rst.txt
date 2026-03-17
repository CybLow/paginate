pypaginate.filtering
====================

.. py:module:: pypaginate.filtering

.. autoapi-nested-parse::

   Universal filtering -- backend-agnostic predicate evaluation.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/pypaginate/filtering/accessor/index
   /api/pypaginate/filtering/engine/index
   /api/pypaginate/filtering/like/index
   /api/pypaginate/filtering/operators/index
   /api/pypaginate/filtering/regex/index
   /api/pypaginate/filtering/registry/index


Classes
-------

.. autoapisummary::

   pypaginate.filtering.FilterEngine
   pypaginate.filtering.OperatorRegistry


Functions
---------

.. autoapisummary::

   pypaginate.filtering.create_default_registry


Package Contents
----------------

.. py:class:: FilterEngine(registry: pypaginate.filtering.registry.OperatorRegistry)

   Apply filter specifications to in-memory sequences.

   :param registry: Operator registry for looking up operators.


   .. py:method:: apply(items: collections.abc.Sequence[T], filters: collections.abc.Sequence[pypaginate.domain.specs.FilterSpec] | pypaginate.domain.specs.FilterGroup) -> list[T]

      Apply filters to items. Accepts flat list or nested FilterGroup.

      :param items: Source sequence to filter.
      :param filters: FilterSpec list or FilterGroup (via And/Or builders).

      :returns: Filtered list of items matching all specs.



.. py:class:: OperatorRegistry

   Registry mapping operator names to Operator instances.


   .. py:method:: get(name: str) -> pypaginate.filtering.operators.Operator

      Look up an operator by name.

      :param name: Operator name.

      :returns: The registered Operator instance.

      :raises FilterError: If no operator is registered under *name*.



   .. py:method:: register(name: str, operator: pypaginate.filtering.operators.Operator) -> None

      Register an operator under the given name.

      :param name: Operator name (e.g. ``"eq"``).
      :param operator: An object implementing the Operator protocol.



.. py:function:: create_default_registry() -> OperatorRegistry

   Create an OperatorRegistry with all built-in operators.

   :returns: A fully populated OperatorRegistry.


