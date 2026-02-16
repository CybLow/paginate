pypaginate.filters.predicates.operators.comparison
==================================================

.. py:module:: pypaginate.filters.predicates.operators.comparison

.. autoapi-nested-parse::

   Equality and ordering operator factories.



Attributes
----------

.. autoapisummary::

   pypaginate.filters.predicates.operators.comparison.COMPARATORS


Classes
-------

.. autoapisummary::

   pypaginate.filters.predicates.operators.comparison.EqualityFactory
   pypaginate.filters.predicates.operators.comparison.OrderingFactory


Module Contents
---------------

.. py:class:: EqualityFactory

   Factory producing equality and inequality predicates.

   .. attribute:: negate

      When ``True``, produce a ``!=`` predicate instead of ``==``.


.. py:class:: OrderingFactory

   Factory producing numeric ordering predicates with validation.

   .. attribute:: name

      Operator name used for error reporting.

   .. attribute:: comparator

      Callable implementing the ordering relation.


.. py:data:: COMPARATORS
   :type:  dict[str, collections.abc.Callable[[pypaginate.types.SupportsTotalOrdering, pypaginate.types.SupportsTotalOrdering], bool]]

