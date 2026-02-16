pypaginate.filters.search.strategies
====================================

.. py:module:: pypaginate.filters.search.strategies

.. autoapi-nested-parse::

   Composable strategies for SQL pagination search.



Classes
-------

.. autoapisummary::

   pypaginate.filters.search.strategies.ConditionContext
   pypaginate.filters.search.strategies.ConditionStrategy
   pypaginate.filters.search.strategies.IdConditionStrategy
   pypaginate.filters.search.strategies.PhraseConditionStrategy
   pypaginate.filters.search.strategies.TermConditionStrategy


Module Contents
---------------

.. py:class:: ConditionContext

   Immutable context provided to each condition strategy.


.. py:class:: ConditionStrategy

   Bases: :py:obj:`Protocol`


   Strategy interface producing SQL clauses from the context.


   .. py:method:: collect(context: ConditionContext) -> list[pypaginate.types.SqlClause]


.. py:class:: IdConditionStrategy

   Collect identifiers matching the configured ID pattern.


   .. py:method:: collect(context: ConditionContext) -> list[pypaginate.types.SqlClause]
      :staticmethod:


      Return ID matching clauses for the configured columns.

      :param context: Context providing tokens and id_fields.

      :returns: A list containing a single clause, or an empty list when none.



.. py:class:: PhraseConditionStrategy(normalizer: pypaginate.text.api.SqlTextNormalizer)

   Create LIKE clauses for quoted phrases.


   .. py:method:: collect(context: ConditionContext) -> list[pypaginate.types.SqlClause]

      Return LIKE clauses for quoted phrases in the query.

      :param context: Condition context with phrase tokens.

      :returns: List of LIKE clauses for phrases.



.. py:class:: TermConditionStrategy(normalizer: pypaginate.text.api.SqlTextNormalizer)

   Create LIKE clauses for individual tokens.


   .. py:method:: collect(context: ConditionContext) -> list[pypaginate.types.SqlClause]

      Return LIKE clauses for individual terms, skipping ID tokens.

      :param context: Condition context with term tokens.

      :returns: List of LIKE clauses for terms.



