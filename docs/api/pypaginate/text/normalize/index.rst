pypaginate.text.normalize
=========================

.. py:module:: pypaginate.text.normalize

.. autoapi-nested-parse::

   Text normalization using Python stdlib.

   Replaces the previous text-unidecode dependency with stdlib
   unicodedata. Handles accents, diacritics, case folding, and
   whitespace normalization for 95% of use cases.

   Uses a bounded dict cache (~4x faster than functools.lru_cache
   per lookup) with ASCII fast path for majority of real data.



Functions
---------

.. autoapisummary::

   pypaginate.text.normalize.clear_normalize_cache
   pypaginate.text.normalize.normalize_text


Module Contents
---------------

.. py:function:: clear_normalize_cache() -> None

   Clear the normalize_text cache.

   Call in long-lived processes or between test runs
   to free memory from cached normalization results.


.. py:function:: normalize_text(value: str) -> str

   Normalize text for search and filtering.

   Results are cached (bounded dict, 8192 entries) since the
   function is pure and field values often repeat across items.

   :param value: Text to normalize.

   :returns: Normalized ASCII-safe text.


