pypaginate.filtering.like
=========================

.. py:module:: pypaginate.filtering.like

.. autoapi-nested-parse::

   LIKE pattern utilities — classification and glob conversion.

   Classifies SQL LIKE patterns for fast dispatch to string methods
   when possible, falling back to fnmatch for complex patterns.



Functions
---------

.. autoapisummary::

   pypaginate.filtering.like.classify_like
   pypaginate.filtering.like.like_to_glob
   pypaginate.filtering.like.match_ilike
   pypaginate.filtering.like.match_like


Module Contents
---------------

.. py:function:: classify_like(pattern: str) -> tuple[str, str]

   Classify a LIKE pattern for fast string-method dispatch.

   :param pattern: SQL LIKE pattern with ``%`` and ``_`` wildcards.

   :returns: ``"contains"``, ``"startswith"``, ``"endswith"``, ``"complex"``.
   :rtype: Tuple of (kind, inner_value) where kind is one of


.. py:function:: like_to_glob(pattern: str) -> str

   Convert SQL LIKE pattern to fnmatch glob pattern.


.. py:function:: match_ilike(field_str: str, spec_value: str) -> bool

   Match a field value against a case-insensitive LIKE pattern.


.. py:function:: match_like(field_str: str, spec_value: str) -> bool

   Match a field value against a LIKE pattern.


