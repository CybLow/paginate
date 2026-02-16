pypaginate.filters.search.conditions
====================================

.. py:module:: pypaginate.filters.search.conditions

.. autoapi-nested-parse::

   Builders composing SQLAlchemy expressions for search tokens.



Classes
-------

.. autoapisummary::

   pypaginate.filters.search.conditions.ConditionContext
   pypaginate.filters.search.conditions.ConditionStrategy
   pypaginate.filters.search.conditions.IdConditionStrategy
   pypaginate.filters.search.conditions.PhraseConditionStrategy
   pypaginate.filters.search.conditions.SearchMode
   pypaginate.filters.search.conditions.SqlConditionBuilder
   pypaginate.filters.search.conditions.TermConditionStrategy


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



.. py:class:: SearchMode(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Aggregation mode for search conditions.


.. py:class:: SqlConditionBuilder(normalizer: pypaginate.text.api.SqlTextNormalizer)

   Compose SQLAlchemy expressions for search tokens via strategies.


   .. py:method:: build(model_class: type, fields: collections.abc.Sequence[str], tokens: pypaginate.filters.search.parser.QueryTokens, *, mode: SearchMode, prefix: bool, id_fields: collections.abc.Sequence[str], id_token_regex: re.Pattern[str]) -> list[pypaginate.types.SqlClause]

      Build SQL clauses for the provided tokens and options.

      :param model_class: ORM model class providing searchable attributes.
      :param fields: Field names targeted for LIKE comparisons.
      :param tokens: Normalized tokens extracted from the search term.
      :param mode: Aggregation mode for combining sub-clauses.
      :param prefix: Whether LIKE patterns use prefix semantics.
      :param id_fields: Field names acting as identifiers.
      :param id_token_regex: Pattern used to detect identifier tokens.

      :returns: A list of SQLAlchemy boolean expressions.



   .. py:method:: build_from_context(context: pypaginate.filters.search.strategies.ConditionContext, *, mode: SearchMode) -> list[pypaginate.types.SqlClause]

      Build SQL clauses from an existing :class:`ConditionContext`.



   .. py:method:: context(model_class: type, fields: collections.abc.Sequence[str], tokens: pypaginate.filters.search.parser.QueryTokens, prefix: bool, id_fields: collections.abc.Sequence[str], id_token_regex: re.Pattern[str]) -> pypaginate.filters.search.strategies.ConditionContext
      :staticmethod:


      Create a :class:`ConditionContext` from inputs.



.. py:class:: TermConditionStrategy(normalizer: pypaginate.text.api.SqlTextNormalizer)

   Create LIKE clauses for individual tokens.


   .. py:method:: collect(context: ConditionContext) -> list[pypaginate.types.SqlClause]

      Return LIKE clauses for individual terms, skipping ID tokens.

      :param context: Condition context with term tokens.

      :returns: List of LIKE clauses for terms.



