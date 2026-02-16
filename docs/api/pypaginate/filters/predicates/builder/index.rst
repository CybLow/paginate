pypaginate.filters.predicates.builder
=====================================

.. py:module:: pypaginate.filters.predicates.builder

.. autoapi-nested-parse::

   Predicate builders orchestrating the FilterEngine strategies.



Classes
-------

.. autoapisummary::

   pypaginate.filters.predicates.builder.JsonLogicPredicateBuilder


Module Contents
---------------

.. py:class:: JsonLogicPredicateBuilder

   Compile filter specifications into predicates using JSON Logic semantics.


   .. py:method:: build(spec: object) -> pypaginate.filters.predicates.registry.FilterPredicate[object]

      Compile spec into a single predicate callable.

      :param spec: Filter specification to compile.

      :returns: A predicate function that evaluates candidates.



   .. py:attribute:: registry
      :type:  pypaginate.filters.predicates.registry.OperatorRegistry[object]

      Operator registry used to instantiate predicates.


