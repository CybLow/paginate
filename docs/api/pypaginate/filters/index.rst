pypaginate.filters
==================

.. py:module:: pypaginate.filters

.. autoapi-nested-parse::

   Filtering and search capabilities for pagination.

   This module provides two distinct filtering systems:

   predicates/
       JSON Logic-based filtering with customizable operators.
       Use for complex predicate-based filtering on in-memory data.

   search/
       Text-based search for SQL and in-memory data.
       Use for full-text search with token parsing and fuzzy matching.

   Public API
   ----------
   From predicates:
       FilterEngine, FieldAccessor, OperatorRegistry, filter_items

   From search:
       SqlSearchService, MemorySearchService, TokenParser



Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/pypaginate/filters/predicates/index
   /api/pypaginate/filters/search/index
   /api/pypaginate/filters/sql_adapter/index


Attributes
----------

.. autoapisummary::

   pypaginate.filters.DEFAULT_SEARCH_MODE
   pypaginate.filters.FilterPredicate
   pypaginate.filters.OperatorFactory


Classes
-------

.. autoapisummary::

   pypaginate.filters.CompiledFilter
   pypaginate.filters.FieldAccessor
   pypaginate.filters.FilterEngine
   pypaginate.filters.JsonLogicPredicateBuilder
   pypaginate.filters.MemorySearchEngine
   pypaginate.filters.MemorySearchService
   pypaginate.filters.OperatorRegistry
   pypaginate.filters.QueryTokens
   pypaginate.filters.SearchMode
   pypaginate.filters.SqlSearchService
   pypaginate.filters.TokenParser


Functions
---------

.. autoapisummary::

   pypaginate.filters.create_memory_search_service
   pypaginate.filters.create_sql_search_service
   pypaginate.filters.filter_items


Package Contents
----------------

.. py:class:: CompiledFilter

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Pair a field accessor with its predicate.


   .. py:method:: matches(item: ItemT) -> bool

      Return True when item matches the predicate.

      :param item: Item to evaluate against the filter.

      :returns: True if the item passes the filter predicate.



   .. py:attribute:: accessor
      :type:  pypaginate.filters.predicates.field_accessor.FieldAccessor

      Accessor resolving field values on items.


   .. py:attribute:: predicate
      :type:  pypaginate.filters.predicates.registry.FilterPredicate[object]

      Callable evaluating the resolved value.


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


.. py:class:: FilterEngine(registry: pypaginate.filters.predicates.registry.OperatorRegistry[object] | None = None)

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Compile declarative filter specifications into callables.


   .. py:method:: apply(items: collections.abc.Sequence[ItemT], filters: collections.abc.Mapping[str, object]) -> list[ItemT]

      Filter items using a mapping of path -> filter spec.

      :param items: Sequence of items to filter.
      :param filters: Mapping of field paths to filter specifications.

      :returns: List of items matching all filter criteria.



.. py:class:: JsonLogicPredicateBuilder

   Compile filter specifications into predicates using JSON Logic semantics.


   .. py:method:: build(spec: object) -> pypaginate.filters.predicates.registry.FilterPredicate[object]

      Compile spec into a single predicate callable.

      :param spec: Filter specification to compile.

      :returns: A predicate function that evaluates candidates.



   .. py:attribute:: registry
      :type:  pypaginate.filters.predicates.registry.OperatorRegistry[object]

      Operator registry used to instantiate predicates.


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



.. py:class:: OperatorRegistry

   Bases: :py:obj:`Generic`\ [\ :py:obj:`CandidateT_inv`\ ]


   Mapping of operator names to predicate factories.


   .. py:method:: build(name: str, argument: object) -> FilterPredicate[CandidateT_inv]

      Return a predicate by resolving name with argument.

      :param name: Operator name to resolve.
      :param argument: Argument to pass to the operator factory.

      :returns: A predicate function for filtering.

      :raises FilterValidationError: If name is not registered.



   .. py:method:: default() -> OperatorRegistry[object]
      :classmethod:


      Create a registry pre-populated with standard operators.

      :returns: A new OperatorRegistry with default operators registered.



   .. py:method:: register(names: collections.abc.Sequence[str], factory: OperatorFactory[CandidateT_inv]) -> None

      Register a factory for a list of operator names.

      :param names: List of operator name aliases.
      :param factory: Factory function creating predicates.



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


.. py:function:: create_sql_search_service(*, id_pattern: re.Pattern[str] | None = None) -> pypaginate.filters.search.sql_search.SqlSearchService

   Create a SQL-backed search service.

   :param id_pattern: Optional regex used to detect identifier tokens.

   :returns: A configured :class:`SqlSearchService` instance.


.. py:function:: filter_items(items: collections.abc.Sequence[ItemT], filters: collections.abc.Mapping[str, object], *, registry: pypaginate.filters.predicates.registry.OperatorRegistry[object] | None = None) -> list[ItemT]

   Apply declarative filters to an in-memory sequence.

   :param items: Sequence of candidate items to filter.
   :param filters: Mapping of ``path -> filter`` specifications.
   :param registry: Optional operator registry (default operators otherwise).

   :returns: Filtered list of items matching all compiled predicates.


.. py:data:: DEFAULT_SEARCH_MODE
   :type:  pypaginate.filters.search.conditions.SearchMode

   Default search mode used when none is specified.

.. py:data:: FilterPredicate

   Callable type for filter predicates.

   A predicate accepts a candidate value and returns True if it matches.

.. py:data:: OperatorFactory

   Callable type for factories creating predicates from arguments.

   A factory accepts an argument and returns a configured predicate.

