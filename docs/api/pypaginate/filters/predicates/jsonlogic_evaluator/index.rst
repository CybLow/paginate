pypaginate.filters.predicates.jsonlogic_evaluator
=================================================

.. py:module:: pypaginate.filters.predicates.jsonlogic_evaluator

.. autoapi-nested-parse::

   Runtime helpers bridging json-logic with strict typing constraints.

   This adapter évite les mutations globales et rétablit l'état après évaluation.
   Compatible mypy strict: on ne manipule pas directement json_logic.__dict__ tel quel.



Classes
-------

.. autoapisummary::

   pypaginate.filters.predicates.jsonlogic_evaluator.JsonLogicAdapter


Functions
---------

.. autoapisummary::

   pypaginate.filters.predicates.jsonlogic_evaluator.evaluate_json_logic_rule


Module Contents
---------------

.. py:class:: JsonLogicAdapter

   Évalue une règle json-logic dans un environnement isolé.


   .. py:method:: evaluate(rule: object, data: JsonLogicData) -> object
      :staticmethod:


      Evaluate a JSON-logic rule against a data context.

      :param rule: JSON-serializable structure representing the rule.
      :param data: Mapping providing variables consumed by the rule.

      :returns: The raw result produced by ``json_logic.jsonLogic``.



.. py:function:: evaluate_json_logic_rule(rule: object, data: JsonLogicData) -> object

   Convenience wrapper around :class:`JsonLogicAdapter` evaluation.

   :param rule: JSON-logic rule.
   :param data: Variable mapping for rule evaluation.

   :returns: Evaluation result.


