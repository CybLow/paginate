pypaginate.filters.predicates.operators.text
============================================

.. py:module:: pypaginate.filters.predicates.operators.text

.. autoapi-nested-parse::

   Text comparison operator factories.



Classes
-------

.. autoapisummary::

   pypaginate.filters.predicates.operators.text.TextFactory


Module Contents
---------------

.. py:class:: TextFactory

   Factory applying text matchers with consistent normalisation.

   .. attribute:: name

      Operator label for error messages.

   .. attribute:: matcher

      Callable implementing the string comparison.

   .. attribute:: case_sensitive

      Whether to preserve case during normalization.


