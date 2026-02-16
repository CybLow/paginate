pypaginate.filters.search.fuzzy
===============================

.. py:module:: pypaginate.filters.search.fuzzy

.. autoapi-nested-parse::

   Fuzzy matching helpers shared by the in-memory search engine.



Functions
---------

.. autoapisummary::

   pypaginate.filters.search.fuzzy.fuzzy_match
   pypaginate.filters.search.fuzzy.is_near_match
   pypaginate.filters.search.fuzzy.partial_ratio
   pypaginate.filters.search.fuzzy.text_match


Module Contents
---------------

.. py:function:: fuzzy_match(token: str, text: str, threshold: int) -> bool

   Return True when text matches token within fuzzy bounds.

   :param token: Search token to match.
   :param text: Text to search in.
   :param threshold: RapidFuzz threshold percentage (0-100).

   :returns: True if fuzzy match succeeds.


.. py:function:: is_near_match(token: str, text: str) -> bool

   Return True when token and text are within one mutation.

   :param token: Search token.
   :param text: Text to compare.

   :returns: True if Levenshtein distance <= 1.


.. py:function:: partial_ratio(token: str, text: str) -> int

   Compute the RapidFuzz partial ratio or raise if unavailable.

   :param token: Search token.
   :param text: Text to compare.

   :returns: Partial ratio score (0-100).


.. py:function:: text_match(token: str, text: str, prefix: bool) -> bool

   Return True when text satisfies the prefix/contains policy.

   :param token: Search token.
   :param text: Text to search in.
   :param prefix: Whether to use prefix matching (vs contains).

   :returns: True if match succeeds.


