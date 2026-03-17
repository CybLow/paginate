pypaginate.search.matching
==========================

.. py:module:: pypaginate.search.matching

.. autoapi-nested-parse::

   Matching utilities for search operations.

   All functions expect pre-normalized strings. Callers must
   normalize via ``normalize_text()`` before calling.

   Provides exact, prefix, and contains matching plus optional
   fuzzy matching via rapidfuzz (graceful fallback if unavailable).



Functions
---------

.. autoapisummary::

   pypaginate.search.matching.fuzzy_score
   pypaginate.search.matching.matches_field


Module Contents
---------------

.. py:function:: fuzzy_score(norm_value: str, norm_token: str, threshold: int, fuzzy_mode: pypaginate.domain.enums.FuzzyMode = FuzzyMode.FUZZY) -> int

   Compute fuzzy match score on pre-normalized strings.

   :param norm_value: Pre-normalized field value.
   :param norm_token: Pre-normalized search token.
   :param threshold: Minimum score (0-100) to consider a match.
   :param fuzzy_mode: Algorithm to use (FUZZY or TOKEN_SORT).

   :returns: Score from 0 to 100 (0 means no match above threshold).


.. py:function:: matches_field(norm_value: str, norm_token: str, mode: pypaginate.domain.enums.SearchFieldMode) -> bool

   Check if a normalized value matches a normalized token.


