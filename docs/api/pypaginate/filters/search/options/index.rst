pypaginate.filters.search.options
=================================

.. py:module:: pypaginate.filters.search.options

.. autoapi-nested-parse::

   Validation helpers for SQL search pagination options.



Attributes
----------

.. autoapisummary::

   pypaginate.filters.search.options.DEFAULT_SEARCH_MODE


Classes
-------

.. autoapisummary::

   pypaginate.filters.search.options.ContextOptions
   pypaginate.filters.search.options.ResolvedOptions
   pypaginate.filters.search.options.SearchOptionSet
   pypaginate.filters.search.options.SearchOptions


Functions
---------

.. autoapisummary::

   pypaginate.filters.search.options.resolve_options


Module Contents
---------------

.. py:class:: ContextOptions

   Bases: :py:obj:`TypedDict`


   Keyword arguments passed to SqlConditionBuilder.context.

   .. attribute:: prefix

      Whether to use prefix matching for search terms.

   .. attribute:: id_fields

      Tuple of field names to search for identifiers.

   .. attribute:: id_token_regex

      Compiled regex pattern to detect ID tokens.


.. py:class:: ResolvedOptions

   Internal representation consumed by the condition builder.

   .. attribute:: mode

      Validated search mode.

   .. attribute:: context

      Context options for the condition builder.


.. py:class:: SearchOptionSet

   Validated tuple mirroring SearchOptions.

   .. attribute:: mode

      Search mode (AND/OR).

   .. attribute:: prefix

      Whether to use prefix matching.

   .. attribute:: id_fields

      Tuple of field names for ID matching.

   .. attribute:: id_token_regex

      Compiled regex for ID token detection.


   .. py:method:: from_mapping(options: collections.abc.Mapping[str, object], *, default_pattern: re.Pattern[str]) -> SearchOptionSet
      :classmethod:


      Create a SearchOptionSet from a mapping of options.

      :param options: User-provided options mapping.
      :param default_pattern: Default ID pattern if not provided.

      :returns: Validated SearchOptionSet instance.



.. py:class:: SearchOptions

   Bases: :py:obj:`TypedDict`


   User facing options supported by the SQL search service.

   .. attribute:: mode

      Search mode (AND/OR).

   .. attribute:: prefix

      Whether to use prefix matching.

   .. attribute:: id_fields

      Sequence of field names for ID matching.

   .. attribute:: id_token_regex

      Compiled regex to detect identifier tokens.


.. py:function:: resolve_options(options: collections.abc.Mapping[str, object], *, default_pattern: re.Pattern[str]) -> ResolvedOptions

   Validate and normalize user-facing options to resolved values.

   :param options: Mapping of supported options (mode, prefix, etc.).
   :param default_pattern: Default compiled regex for identifier tokens.

   :returns: Resolved options with a context suitable for the condition builder.


.. py:data:: DEFAULT_SEARCH_MODE
   :type:  pypaginate.filters.search.conditions.SearchMode

   Default search mode used when none is specified.

