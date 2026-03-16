pypaginate.filtering.registry
=============================

.. py:module:: pypaginate.filtering.registry

.. autoapi-nested-parse::

   Operator registry mapping names to operator instances.

   Provides a default registry pre-populated with all built-in operators.
   Custom operators can be registered at runtime.



Classes
-------

.. autoapisummary::

   pypaginate.filtering.registry.OperatorRegistry


Functions
---------

.. autoapisummary::

   pypaginate.filtering.registry.create_default_registry


Module Contents
---------------

.. py:class:: OperatorRegistry

   Registry mapping operator names to Operator instances.


   .. py:method:: get(name: str) -> pypaginate.filtering.operators.Operator

      Look up an operator by name.

      :param name: Operator name.

      :returns: The registered Operator instance.

      :raises FilterError: If no operator is registered under *name*.



   .. py:method:: register(name: str, operator: pypaginate.filtering.operators.Operator) -> None

      Register an operator under the given name.

      :param name: Operator name (e.g. ``"eq"``).
      :param operator: An object implementing the Operator protocol.



.. py:function:: create_default_registry() -> OperatorRegistry

   Create an OperatorRegistry with all built-in operators.

   :returns: A fully populated OperatorRegistry.


