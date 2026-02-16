pypaginate.filters.predicates.registry
======================================

.. py:module:: pypaginate.filters.predicates.registry

.. autoapi-nested-parse::

   Registry of filter operator factories.



Attributes
----------

.. autoapisummary::

   pypaginate.filters.predicates.registry.FilterPredicate
   pypaginate.filters.predicates.registry.OperatorFactory


Classes
-------

.. autoapisummary::

   pypaginate.filters.predicates.registry.OperatorRegistry


Module Contents
---------------

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



.. py:data:: FilterPredicate

   Callable type for filter predicates.

   A predicate accepts a candidate value and returns True if it matches.

.. py:data:: OperatorFactory

   Callable type for factories creating predicates from arguments.

   A factory accepts an argument and returns a configured predicate.

