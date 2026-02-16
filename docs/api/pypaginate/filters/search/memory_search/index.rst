pypaginate.filters.search.memory_search
=======================================

.. py:module:: pypaginate.filters.search.memory_search

.. autoapi-nested-parse::

   In-memory search engine for text queries.



Attributes
----------

.. autoapisummary::

   pypaginate.filters.search.memory_search.DEFAULT_FUZZY_THRESHOLD
   pypaginate.filters.search.memory_search.DEFAULT_SEARCH_MODE


Classes
-------

.. autoapisummary::

   pypaginate.filters.search.memory_search.MemorySearchEngine
   pypaginate.filters.search.memory_search.MemorySearchService


Module Contents
---------------

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



.. py:data:: DEFAULT_FUZZY_THRESHOLD
   :value: 75


.. py:data:: DEFAULT_SEARCH_MODE

