pypaginate.filters.predicates.field_accessor
============================================

.. py:module:: pypaginate.filters.predicates.field_accessor

.. autoapi-nested-parse::

   Resolve dotted paths using :mod:`jmespath` expressions.



Attributes
----------

.. autoapisummary::

   pypaginate.filters.predicates.field_accessor.CompiledExpression


Classes
-------

.. autoapisummary::

   pypaginate.filters.predicates.field_accessor.FieldAccessor


Module Contents
---------------

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


.. py:type:: CompiledExpression
   :canonical: ParsedResult


