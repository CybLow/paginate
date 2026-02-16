pypaginate.filters.predicates
=============================

.. py:module:: pypaginate.filters.predicates

.. autoapi-nested-parse::

   Predicate-based filtering for pagination.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/pypaginate/filters/predicates/builder/index
   /api/pypaginate/filters/predicates/engine/index
   /api/pypaginate/filters/predicates/field_accessor/index
   /api/pypaginate/filters/predicates/jsonlogic_evaluator/index
   /api/pypaginate/filters/predicates/operator_arguments/index
   /api/pypaginate/filters/predicates/operators/index
   /api/pypaginate/filters/predicates/registry/index


Attributes
----------

.. autoapisummary::

   pypaginate.filters.predicates.FilterPredicate
   pypaginate.filters.predicates.OperatorFactory


Classes
-------

.. autoapisummary::

   pypaginate.filters.predicates.CompiledFilter
   pypaginate.filters.predicates.FieldAccessor
   pypaginate.filters.predicates.FilterEngine
   pypaginate.filters.predicates.JsonLogicPredicateBuilder
   pypaginate.filters.predicates.OperatorRegistry


Functions
---------

.. autoapisummary::

   pypaginate.filters.predicates.filter_items


Package Contents
----------------

.. py:class:: CompiledFilter

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Pair a field accessor with its predicate.


   .. py:method:: matches(item: ItemT) -> bool

      Return True when item matches the predicate.

      :param item: Item to evaluate against the filter.

      :returns: True if the item passes the filter predicate.



   .. py:attribute:: accessor
      :type:  pypaginate.filters.predicates.field_accessor.FieldAccessor

      Accessor resolving field values on items.


   .. py:attribute:: predicate
      :type:  pypaginate.filters.predicates.registry.FilterPredicate[object]

      Callable evaluating the resolved value.


.. py:class:: FieldAccessor

   Resolve dotted paths on heterogeneous containers.


   .. py:method:: from_string(raw_path: str) -> FieldAccessor
      :classmethod:


      Create an accessor from a dotted path string.

      :param raw_path: Dotted path notation (e.g. "user.address.city").

      :returns: A configured FieldAccessor instance.



   .. py:method:: resolve(obj: object) -> object

      Resolve the accessor against obj and return the extracted value.

      :param obj: Object to extract value from.

      :returns: The resolved value at the accessor's path.



   .. py:attribute:: expression
      :type:  CompiledExpression

      Compiled :mod:`jmespath` expression.


.. py:class:: FilterEngine(registry: pypaginate.filters.predicates.registry.OperatorRegistry[object] | None = None)

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Compile declarative filter specifications into callables.


   .. py:method:: apply(items: collections.abc.Sequence[ItemT], filters: collections.abc.Mapping[str, object]) -> list[ItemT]

      Filter items using a mapping of path -> filter spec.

      :param items: Sequence of items to filter.
      :param filters: Mapping of field paths to filter specifications.

      :returns: List of items matching all filter criteria.



.. py:class:: JsonLogicPredicateBuilder

   Compile filter specifications into predicates using JSON Logic semantics.


   .. py:method:: build(spec: object) -> pypaginate.filters.predicates.registry.FilterPredicate[object]

      Compile spec into a single predicate callable.

      :param spec: Filter specification to compile.

      :returns: A predicate function that evaluates candidates.



   .. py:attribute:: registry
      :type:  pypaginate.filters.predicates.registry.OperatorRegistry[object]

      Operator registry used to instantiate predicates.


.. py:class:: OperatorRegistry

   Bases: :py:obj:`Generic`\ [\ :py:obj:`CandidateT_inv`\ ]


   Mapping of operator names to predicate factories.


   .. py:method:: build(name: str, argument: object) -> FilterPredicate[CandidateT_inv]

      Return a predicate by resolving name with argument.

      :param name: Operator name to resolve.
      :param argument: Argument to pass to the operator factory.

      :returns: A predicate function for filtering.

      :raises FilterValidationError: If name is not registered.



   .. py:method:: default() -> OperatorRegistry[object]
      :classmethod:


      Create a registry pre-populated with standard operators.

      :returns: A new OperatorRegistry with default operators registered.



   .. py:method:: register(names: collections.abc.Sequence[str], factory: OperatorFactory[CandidateT_inv]) -> None

      Register a factory for a list of operator names.

      :param names: List of operator name aliases.
      :param factory: Factory function creating predicates.



.. py:function:: filter_items(items: collections.abc.Sequence[ItemT], filters: collections.abc.Mapping[str, object], *, registry: pypaginate.filters.predicates.registry.OperatorRegistry[object] | None = None) -> list[ItemT]

   Apply declarative filters to an in-memory sequence.

   :param items: Sequence of candidate items to filter.
   :param filters: Mapping of ``path -> filter`` specifications.
   :param registry: Optional operator registry (default operators otherwise).

   :returns: Filtered list of items matching all compiled predicates.


.. py:data:: FilterPredicate

   Callable type for filter predicates.

   A predicate accepts a candidate value and returns True if it matches.

.. py:data:: OperatorFactory

   Callable type for factories creating predicates from arguments.

   A factory accepts an argument and returns a configured predicate.

