pypaginate.filters.predicates.operators.simple
==============================================

.. py:module:: pypaginate.filters.predicates.operators.simple

.. autoapi-nested-parse::

   Simple operator factories: membership, nullity, and emptiness checks.



Classes
-------

.. autoapisummary::

   pypaginate.filters.predicates.operators.simple.EmptyFactory
   pypaginate.filters.predicates.operators.simple.MembershipFactory
   pypaginate.filters.predicates.operators.simple.NullityFactory


Module Contents
---------------

.. py:class:: EmptyFactory

   Factory for ``empty`` and ``not_empty`` operators.


.. py:class:: MembershipFactory

   Factory handling membership and negated membership operators.

   .. attribute:: name

      Operator label for error reporting context.

   .. attribute:: invert

      When ``True``, negate membership semantics.


.. py:class:: NullityFactory

   Factory for ``is_null`` / ``is_not_null`` operators.


