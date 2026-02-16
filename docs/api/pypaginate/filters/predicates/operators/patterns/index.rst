pypaginate.filters.predicates.operators.patterns
================================================

.. py:module:: pypaginate.filters.predicates.operators.patterns

.. autoapi-nested-parse::

   Pattern-based filtering operators.



Classes
-------

.. autoapisummary::

   pypaginate.filters.predicates.operators.patterns.LikeFactory
   pypaginate.filters.predicates.operators.patterns.RegexFactory


Module Contents
---------------

.. py:class:: LikeFactory

   Factory implementing SQL LIKE semantics in memory.

   .. attribute:: name

      Operator label for error reporting context.

   .. attribute:: case_sensitive

      Whether comparisons should be case-sensitive.


.. py:class:: RegexFactory

   Factory compiling safe regular expressions.

   .. attribute:: name

      Operator label for error reporting context.

   .. attribute:: case_sensitive

      Whether the regular expression is case-sensitive.


