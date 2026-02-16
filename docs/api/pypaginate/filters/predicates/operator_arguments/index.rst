pypaginate.filters.predicates.operator_arguments
================================================

.. py:module:: pypaginate.filters.predicates.operator_arguments

.. autoapi-nested-parse::

   Validation helpers for operator arguments.



Functions
---------

.. autoapisummary::

   pypaginate.filters.predicates.operator_arguments.ensure_collection
   pypaginate.filters.predicates.operator_arguments.ensure_pair


Module Contents
---------------

.. py:function:: ensure_collection(argument: object, operator: str) -> collections.abc.Sequence[object]

   Ensure that ``argument`` is a non-mapping collection.

   :param argument: Input value to validate.
   :param operator: Operator name for error reporting context.

   :returns: A sequence of objects materialized from ``argument``.

   :raises FilterValidationError: If ``argument`` is ``None`` or a mapping.


.. py:function:: ensure_pair(argument: object, operator: str) -> tuple[object, object]

   Validate that ``argument`` is a two-element sequence.

   :param argument: Input value to validate.
   :param operator: Operator name for error reporting context.

   :returns: The two elements of the sequence as a tuple.

   :raises FilterValidationError: If the input is not a two-element sequence.


