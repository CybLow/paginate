pypaginate.filters.predicates.operators
=======================================

.. py:module:: pypaginate.filters.predicates.operators

.. autoapi-nested-parse::

   Registration helpers for default filter operator factories.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/pypaginate/filters/predicates/operators/comparison/index
   /api/pypaginate/filters/predicates/operators/patterns/index
   /api/pypaginate/filters/predicates/operators/range/index
   /api/pypaginate/filters/predicates/operators/simple/index
   /api/pypaginate/filters/predicates/operators/text/index


Classes
-------

.. autoapisummary::

   pypaginate.filters.predicates.operators.EmptyFactory
   pypaginate.filters.predicates.operators.EqualityFactory
   pypaginate.filters.predicates.operators.LikeFactory
   pypaginate.filters.predicates.operators.MembershipFactory
   pypaginate.filters.predicates.operators.NullityFactory
   pypaginate.filters.predicates.operators.OrderingFactory
   pypaginate.filters.predicates.operators.RangeFactory
   pypaginate.filters.predicates.operators.RegexFactory
   pypaginate.filters.predicates.operators.TextFactory


Functions
---------

.. autoapisummary::

   pypaginate.filters.predicates.operators.register_default_operators


Package Contents
----------------

.. py:class:: EmptyFactory

   Factory for ``empty`` and ``not_empty`` operators.


.. py:class:: EqualityFactory

   Factory producing equality and inequality predicates.

   .. attribute:: negate

      When ``True``, produce a ``!=`` predicate instead of ``==``.


.. py:class:: LikeFactory

   Factory implementing SQL LIKE semantics in memory.

   .. attribute:: name

      Operator label for error reporting context.

   .. attribute:: case_sensitive

      Whether comparisons should be case-sensitive.


.. py:class:: MembershipFactory

   Factory handling membership and negated membership operators.

   .. attribute:: name

      Operator label for error reporting context.

   .. attribute:: invert

      When ``True``, negate membership semantics.


.. py:class:: NullityFactory

   Factory for ``is_null`` / ``is_not_null`` operators.


.. py:class:: OrderingFactory

   Factory producing numeric ordering predicates with validation.

   .. attribute:: name

      Operator name used for error reporting.

   .. attribute:: comparator

      Callable implementing the ordering relation.


.. py:class:: RangeFactory

   Factory for between/range operators.


.. py:class:: RegexFactory

   Factory compiling safe regular expressions.

   .. attribute:: name

      Operator label for error reporting context.

   .. attribute:: case_sensitive

      Whether the regular expression is case-sensitive.


.. py:class:: TextFactory

   Factory applying text matchers with consistent normalisation.

   .. attribute:: name

      Operator label for error messages.

   .. attribute:: matcher

      Callable implementing the string comparison.

   .. attribute:: case_sensitive

      Whether to preserve case during normalization.


.. py:function:: register_default_operators(registry: pypaginate.filters.predicates.registry.OperatorRegistry[object]) -> None

   Populate the registry with the standard operator factories.

   :param registry: Registry receiving default operator factory bindings.


