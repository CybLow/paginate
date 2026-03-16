pypaginate.filtering.operators
==============================

.. py:module:: pypaginate.filtering.operators

.. autoapi-nested-parse::

   Filter operators for in-memory predicate evaluation.



Classes
-------

.. autoapisummary::

   pypaginate.filtering.operators.Between
   pypaginate.filtering.operators.Contains
   pypaginate.filtering.operators.Empty
   pypaginate.filtering.operators.EndsWith
   pypaginate.filtering.operators.Eq
   pypaginate.filtering.operators.Exists
   pypaginate.filtering.operators.Gt
   pypaginate.filtering.operators.Gte
   pypaginate.filtering.operators.ILike
   pypaginate.filtering.operators.In
   pypaginate.filtering.operators.IsNotNull
   pypaginate.filtering.operators.IsNull
   pypaginate.filtering.operators.Like
   pypaginate.filtering.operators.Lt
   pypaginate.filtering.operators.Lte
   pypaginate.filtering.operators.Ne
   pypaginate.filtering.operators.NotEmpty
   pypaginate.filtering.operators.NotIn
   pypaginate.filtering.operators.Operator
   pypaginate.filtering.operators.Regex
   pypaginate.filtering.operators.StartsWith


Module Contents
---------------

.. py:class:: Between

   .. py:method:: evaluate(field_value: object, spec_value: object) -> bool
      :staticmethod:



.. py:class:: Contains

   .. py:method:: evaluate(field_value: object, spec_value: object) -> bool
      :staticmethod:



.. py:class:: Empty

   .. py:method:: evaluate(field_value: object, _spec_value: object) -> bool
      :staticmethod:



.. py:class:: EndsWith

   .. py:method:: evaluate(field_value: object, spec_value: object) -> bool
      :staticmethod:



.. py:class:: Eq

   .. py:method:: evaluate(field_value: object, spec_value: object) -> bool
      :staticmethod:



.. py:class:: Exists

   .. py:method:: evaluate(_field_value: object, _spec_value: object) -> bool
      :staticmethod:



.. py:class:: Gt

   .. py:method:: evaluate(field_value: object, spec_value: object) -> bool
      :staticmethod:



.. py:class:: Gte

   .. py:method:: evaluate(field_value: object, spec_value: object) -> bool
      :staticmethod:



.. py:class:: ILike

   .. py:method:: evaluate(field_value: object, spec_value: object) -> bool
      :staticmethod:



.. py:class:: In

   .. py:method:: evaluate(field_value: object, spec_value: object) -> bool
      :staticmethod:



.. py:class:: IsNotNull

   .. py:method:: evaluate(field_value: object, _spec_value: object) -> bool
      :staticmethod:



.. py:class:: IsNull

   .. py:method:: evaluate(field_value: object, _spec_value: object) -> bool
      :staticmethod:



.. py:class:: Like

   .. py:method:: evaluate(field_value: object, spec_value: object) -> bool
      :staticmethod:



.. py:class:: Lt

   .. py:method:: evaluate(field_value: object, spec_value: object) -> bool
      :staticmethod:



.. py:class:: Lte

   .. py:method:: evaluate(field_value: object, spec_value: object) -> bool
      :staticmethod:



.. py:class:: Ne

   .. py:method:: evaluate(field_value: object, spec_value: object) -> bool
      :staticmethod:



.. py:class:: NotEmpty

   .. py:method:: evaluate(field_value: object, _spec_value: object) -> bool
      :staticmethod:



.. py:class:: NotIn

   .. py:method:: evaluate(field_value: object, spec_value: object) -> bool
      :staticmethod:



.. py:class:: Operator

   Bases: :py:obj:`Protocol`


   Protocol for filter operators.


   .. py:method:: evaluate(field_value: object, spec_value: object) -> bool
      :staticmethod:



.. py:class:: Regex

   .. py:method:: evaluate(field_value: object, spec_value: object) -> bool
      :staticmethod:



.. py:class:: StartsWith

   .. py:method:: evaluate(field_value: object, spec_value: object) -> bool
      :staticmethod:



