pypaginate.text.api
===================

.. py:module:: pypaginate.text.api

.. autoapi-nested-parse::

   Public text normalization API.

   This module aggregates UTF-8 primitives, reusable normalization pipelines,
   and pattern utilities into a single import surface for consumers.



Attributes
----------

.. autoapisummary::

   pypaginate.text.api.NormalizationForm


Classes
-------

.. autoapisummary::

   pypaginate.text.api.FilterTextNormalizer
   pypaginate.text.api.MemoryTextNormalizer
   pypaginate.text.api.SqlTextNormalizer
   pypaginate.text.api.TextPipeline
   pypaginate.text.api.Utf8Normalizer
   pypaginate.text.api.Utf8TextPipeline


Functions
---------

.. autoapisummary::

   pypaginate.text.api.build_like_regex
   pypaginate.text.api.compile_regex
   pypaginate.text.api.create_search_normalizer
   pypaginate.text.api.normalise_regex_argument
   pypaginate.text.api.normalize_utf8
   pypaginate.text.api.sql_like_to_regex
   pypaginate.text.api.transliterate_ascii


Module Contents
---------------

.. py:class:: FilterTextNormalizer(*, case_sensitive: bool)

   Text normalizer for filter comparison operators.

   Provides case-sensitive or case-insensitive text matching for
   filter predicates.


.. py:class:: MemoryTextNormalizer

   Normalizer for in-memory text search operations.

   Used for prefix matching and substring search in memory collections.


   .. py:method:: normalize_text(value: str) -> str

      Normalize text for in-memory comparison.

      :param value: Text to normalize.

      :returns: Normalized text string.



.. py:class:: SqlTextNormalizer

   Normalizer for SQL column expressions and text inputs.

   Provides consistent text normalization for SQL LIKE queries and
   column comparisons.


   .. py:method:: normalize_column(column: pypaginate.types.SqlStringExpression) -> pypaginate.types.SqlStringExpression
      :staticmethod:


      Apply SQL LOWER function to column expression.

      :param column: Column expression to normalize.

      :returns: Normalized column expression.

      :raises SearchNormalizationError: If database doesn't support LOWER.



   .. py:method:: normalize_text(value: str) -> str

      Normalize text input for SQL comparison.

      :param value: Text to normalize.

      :returns: Normalized text string.



.. py:class:: TextPipeline

   Bases: :py:obj:`Protocol`


   Protocol for callable text normalization pipelines.

   A text pipeline is any callable that accepts a string and returns
   a normalized string.


.. py:class:: Utf8Normalizer

   UTF-8 text normalizer with configurable casing and normalization form.


   .. py:method:: normalise(value: str) -> str

      Normalize the given UTF-8 string.

      :param value: Input text to normalize.

      :returns: The normalized string according to the instance configuration.



.. py:class:: Utf8TextPipeline

   Compose UTF-8 normalization, ASCII transliteration and whitespace folding.

   This pipeline is used by both memory and SQL search normalizers to provide
   consistent text processing across different storage backends.


.. py:function:: build_like_regex(pattern: str, *, escape: str | None = None) -> re.Pattern[str]

   Build compiled regex from SQL LIKE pattern.

   :param pattern: SQL LIKE pattern.
   :param escape: Optional escape character.

   :returns: Compiled regular expression.


.. py:function:: compile_regex(pattern: str, *, flags: int = 0) -> re.Pattern[str]

   Compile regex pattern with validation.

   :param pattern: Regular expression pattern.
   :param flags: Regex compilation flags.

   :returns: Compiled regular expression.

   :raises FilterValidationError: If pattern is invalid.


.. py:function:: create_search_normalizer() -> Utf8Normalizer

   Return the canonical search normalizer (lowercase + NFKC).

   :returns: A configured Utf8Normalizer instance.


.. py:function:: normalise_regex_argument(pattern: object, *, normalizer: FilterTextNormalizer, case_sensitive: bool) -> str

   Normalize regex pattern argument for filter operators.

   :param pattern: Pattern to normalize.
   :param normalizer: Text normalizer to use.
   :param case_sensitive: Whether normalization is case-sensitive.

   :returns: Normalized pattern string.

   :raises FilterValidationError: If pattern is not a string.


.. py:function:: normalize_utf8(value: str, *, lowercase: bool, casefold_output: bool, form: NormalizationForm) -> str

   Normalize a UTF-8 string with specified casing and form.

   :param value: Input text to normalize.
   :param lowercase: Whether to lowercase the result (ignored if casefold_output).
   :param casefold_output: Whether to apply casefolding for aggressive matching.
   :param form: Unicode normalization form (e.g. "NFKC").

   :returns: The normalized string.


.. py:function:: sql_like_to_regex(pattern: str) -> str

   Convert SQL LIKE pattern to equivalent regex.

   Handles SQL wildcards:
   - % becomes .*
   - _ becomes .
   - \\ escapes next character

   :param pattern: SQL LIKE pattern string.

   :returns: Equivalent regex pattern string.


.. py:function:: transliterate_ascii(value: str) -> str

   Return ASCII transliteration using text-unidecode.

   :param value: Input unicode text.

   :returns: ASCII-only transliteration of value.


.. py:data:: NormalizationForm

   Literal type for Unicode normalization forms.

