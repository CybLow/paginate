pypaginate.filters.search
=========================

.. py:module:: pypaginate.filters.search

.. autoapi-nested-parse::

   Search-based filtering for pagination.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/pypaginate/filters/search/conditions/index
   /api/pypaginate/filters/search/factories/index
   /api/pypaginate/filters/search/fuzzy/index
   /api/pypaginate/filters/search/helpers/index
   /api/pypaginate/filters/search/memory_search/index
   /api/pypaginate/filters/search/options/index
   /api/pypaginate/filters/search/parser/index
   /api/pypaginate/filters/search/sql_search/index
   /api/pypaginate/filters/search/strategies/index


Attributes
----------

.. autoapisummary::

   pypaginate.filters.search.DEFAULT_SEARCH_MODE


Classes
-------

.. autoapisummary::

   pypaginate.filters.search.MemorySearchEngine
   pypaginate.filters.search.MemorySearchService
   pypaginate.filters.search.QueryTokens
   pypaginate.filters.search.SearchMode
   pypaginate.filters.search.SqlConditionBuilder
   pypaginate.filters.search.SqlSearchService
   pypaginate.filters.search.TokenParser


Functions
---------

.. autoapisummary::

   pypaginate.filters.search.create_memory_search_service
   pypaginate.filters.search.create_search_services
   pypaginate.filters.search.create_sql_search_service


Package Contents
----------------

.. py:class:: MemorySearchEngine(normalizer: pypaginate.text.api.MemoryTextNormalizer)

   Filter Python objects using SQL-compatible normalisation rules.


   .. py:method:: filter(items: collections.abc.Iterable[T], fields: collections.abc.Sequence[str], tokens: pypaginate.filters.search.parser.QueryTokens, *, mode: pypaginate.filters.search.conditions.SearchMode, prefix: bool, fuzzy_threshold: int = DEFAULT_FUZZY_THRESHOLD) -> list[T]

      Return items that match tokenized criteria across selected fields.

      :param items: Iterable of items to filter.
      :param fields: Dot paths to resolve within each item.
      :param tokens: Parsed query tokens.
      :param mode: Aggregation mode (AND/OR/FUZZY).
      :param prefix: Whether to use prefix matching for non-fuzzy mode.
      :param fuzzy_threshold: RapidFuzz threshold for fuzzy mode.

      :returns: A list of items matching the criteria.



   .. py:property:: normalizer
      :type: pypaginate.text.api.MemoryTextNormalizer


      Get the configured text normalizer.

      :returns: The MemoryTextNormalizer instance.


.. py:class:: MemorySearchService(parser: pypaginate.filters.search.parser.TokenParser, engine: MemorySearchEngine)

   Facade orchestrating token parsing and in-memory filtering.


   .. py:method:: search(items: collections.abc.Iterable[T], fields: collections.abc.Sequence[str], term: str, *, mode: pypaginate.filters.search.conditions.SearchMode = DEFAULT_SEARCH_MODE, prefix: bool = False, fuzzy_threshold: int = DEFAULT_FUZZY_THRESHOLD) -> list[T]

      Filter items according to a search term and options.

      :param items: Iterable of items to filter.
      :param fields: Dot paths evaluated for each item.
      :param term: Raw search query string.
      :param mode: Aggregation mode (AND/OR/FUZZY).
      :param prefix: Whether to enable prefix matching.
      :param fuzzy_threshold: RapidFuzz threshold for fuzzy mode.

      :returns: A list of matching items.



.. py:class:: QueryTokens

   Normalized tokens extracted from a raw query string.


   .. py:method:: has_content() -> bool

      Check if tokens contain any searchable content.

      :returns: True if any terms, phrases, or raw tokens exist.



   .. py:attribute:: phrases
      :type:  tuple[str, Ellipsis]

      Lowercased, normalized quoted phrases.


   .. py:attribute:: raw
      :type:  tuple[str, Ellipsis]

      Original unnormalized terms (for ID matching, etc.).


   .. py:attribute:: terms
      :type:  tuple[str, Ellipsis]

      Lowercased, normalized individual tokens.


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



.. py:class:: TokenParser

   Extract quoted phrases and free terms from a search query.


   .. py:method:: parse(query: str, normalizer: collections.abc.Callable[[str], str], *, raw_transform: collections.abc.Callable[[str], str] | None = None) -> QueryTokens

      Parse and normalize a search query into tokens.

      :param query: Input query string.
      :param normalizer: Callable used to normalize tokens and phrases.
      :param raw_transform: Optional transform applied to raw terms.

      :returns: A QueryTokens instance with normalized values.



.. py:function:: create_memory_search_service() -> pypaginate.filters.search.memory_search.MemorySearchService

   Create an in-memory search service.

   :returns: A configured :class:`MemorySearchService` instance.


.. py:function:: create_search_services(*, id_pattern: re.Pattern[str] | None = None) -> tuple[pypaginate.filters.search.sql_search.SqlSearchService, pypaginate.filters.search.memory_search.MemorySearchService]

   Create both SQL and in-memory search services.

   :param id_pattern: Optional regex used to detect identifier tokens
                      for the SQL service.

   :returns: A tuple ``(sql_service, memory_service)``.


.. py:function:: create_sql_search_service(*, id_pattern: re.Pattern[str] | None = None) -> pypaginate.filters.search.sql_search.SqlSearchService

   Create a SQL-backed search service.

   :param id_pattern: Optional regex used to detect identifier tokens.

   :returns: A configured :class:`SqlSearchService` instance.


.. py:data:: DEFAULT_SEARCH_MODE
   :type:  pypaginate.filters.search.conditions.SearchMode

   Default search mode used when none is specified.

