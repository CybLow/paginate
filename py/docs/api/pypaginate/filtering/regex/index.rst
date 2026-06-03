pypaginate.filtering.regex
==========================

.. py:module:: pypaginate.filtering.regex

.. autoapi-nested-parse::

   Safe regex compilation with optional google-re2.

   Uses google-re2 (linear-time, ReDoS-safe) if installed,
   falls back to stdlib ``re``. Same API surface.



Functions
---------

.. autoapisummary::

   pypaginate.filtering.regex.compile_pattern


Module Contents
---------------

.. py:function:: compile_pattern(pattern: str) -> Any

   Compile a regex pattern using re2 if available.

   :param pattern: Regular expression pattern string.

   :returns: A compiled pattern object with a ``.search()`` method.

   :raises FilterError: If the pattern is too long or invalid.


