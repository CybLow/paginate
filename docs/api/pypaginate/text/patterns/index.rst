pypaginate.text.patterns
========================

.. py:module:: pypaginate.text.patterns

.. autoapi-nested-parse::

   Pattern utilities for SQL LIKE and regex filtering.



Classes
-------

.. autoapisummary::

   pypaginate.text.patterns.FilterTextNormalizer


Functions
---------

.. autoapisummary::

   pypaginate.text.patterns.build_like_regex
   pypaginate.text.patterns.compile_regex
   pypaginate.text.patterns.normalise_regex_argument
   pypaginate.text.patterns.sql_like_to_regex


Module Contents
---------------

.. py:class:: FilterTextNormalizer(*, case_sensitive: bool)

   Text normalizer for filter comparison operators.

   Provides case-sensitive or case-insensitive text matching for
   filter predicates.


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


.. py:function:: normalise_regex_argument(pattern: object, *, normalizer: FilterTextNormalizer, case_sensitive: bool) -> str

   Normalize regex pattern argument for filter operators.

   :param pattern: Pattern to normalize.
   :param normalizer: Text normalizer to use.
   :param case_sensitive: Whether normalization is case-sensitive.

   :returns: Normalized pattern string.

   :raises FilterValidationError: If pattern is not a string.


.. py:function:: sql_like_to_regex(pattern: str) -> str

   Convert SQL LIKE pattern to equivalent regex.

   Handles SQL wildcards:
   - % becomes .*
   - _ becomes .
   - \\ escapes next character

   :param pattern: SQL LIKE pattern string.

   :returns: Equivalent regex pattern string.


