pypaginate.filters.search.sql_search
====================================

.. py:module:: pypaginate.filters.search.sql_search

.. autoapi-nested-parse::

   SQL-backed search engine for text queries.



Classes
-------

.. autoapisummary::

   pypaginate.filters.search.sql_search.SqlConditionBuilder
   pypaginate.filters.search.sql_search.SqlSearchService


Module Contents
---------------

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



.. py:class:: SqlSearchService(parser: pypaginate.filters.search.parser.TokenParser, normalizer: pypaginate.text.api.SqlTextNormalizer, builder: pypaginate.filters.search.conditions.SqlConditionBuilder, *, id_pattern: re.Pattern[str] | None = None)

   Facade orchestrating token parsing and SQL condition building.


   .. py:method:: create_conditions(model_class: type, search_fields: collections.abc.Sequence[str], search_term: str, **options: Unpack[pypaginate.filters.search.options.SearchOptions]) -> list[pypaginate.types.SqlClause]

      Create SQLAlchemy boolean expressions for the given search term.

      :param model_class: ORM model class providing column attributes.
      :param search_fields: Field names to target for LIKE expressions.
      :param search_term: Raw search query string.
      :param \*\*options: User-facing options resolved via options module.

      :returns: A list of SQLAlchemy boolean expressions ready to combine.



   .. py:method:: has_criteria(fields: collections.abc.Sequence[str], tokens: pypaginate.filters.search.parser.QueryTokens) -> bool
      :staticmethod:


      Check if search criteria exist.

      :param fields: Field list to search.
      :param tokens: Parsed query tokens.

      :returns: True if both fields and tokens contain content.



   .. py:method:: normalize_column(column: pypaginate.types.SqlStringExpression) -> pypaginate.types.SqlStringExpression

      Normalize a column expression for consistent LIKE comparisons.

      :param column: Column expression to normalize.

      :returns: Normalized column expression.



   .. py:method:: normalize_text(value: str) -> str

      Normalize free text using the configured SQL text normalizer.

      :param value: Text to normalize.

      :returns: Normalized text string.



   .. py:method:: parse_tokens(term: str) -> pypaginate.filters.search.parser.QueryTokens

      Parse a raw search term into normalized tokens.

      :param term: Raw search query string.

      :returns: Parsed QueryTokens instance.



