pypaginate.text.pipelines
=========================

.. py:module:: pypaginate.text.pipelines

.. autoapi-nested-parse::

   Reusable text normalization pipelines for search and filtering.



Classes
-------

.. autoapisummary::

   pypaginate.text.pipelines.MemoryTextNormalizer
   pypaginate.text.pipelines.SqlTextNormalizer
   pypaginate.text.pipelines.TextPipeline
   pypaginate.text.pipelines.Utf8TextPipeline


Module Contents
---------------

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


.. py:class:: Utf8TextPipeline

   Compose UTF-8 normalization, ASCII transliteration and whitespace folding.

   This pipeline is used by both memory and SQL search normalizers to provide
   consistent text processing across different storage backends.


