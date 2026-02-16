pypaginate.text
===============

.. py:module:: pypaginate.text

.. autoapi-nested-parse::

   Text processing utilities for pagination.

   This module provides text normalization and processing for search:
   - Text normalizers for SQL and in-memory contexts
   - Pattern matching utilities
   - Text processing pipelines
   - UTF-8 utilities

   Public API
   ----------
   MemoryTextNormalizer
       Text normalizer for in-memory search operations.
   SqlTextNormalizer
       Text normalizer for SQL search operations.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/pypaginate/text/api/index
   /api/pypaginate/text/patterns/index
   /api/pypaginate/text/pipelines/index
   /api/pypaginate/text/utf8/index


Classes
-------

.. autoapisummary::

   pypaginate.text.MemoryTextNormalizer
   pypaginate.text.SqlTextNormalizer


Package Contents
----------------

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



