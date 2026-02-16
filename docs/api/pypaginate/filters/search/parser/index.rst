pypaginate.filters.search.parser
================================

.. py:module:: pypaginate.filters.search.parser

.. autoapi-nested-parse::

   Tokenization helpers for textual search.



Classes
-------

.. autoapisummary::

   pypaginate.filters.search.parser.QueryTokens
   pypaginate.filters.search.parser.TokenParser


Module Contents
---------------

.. py:class:: QueryTokens

   Normalized tokens extracted from a raw query string.


   .. py:method:: has_content() -> bool

      Check if tokens contain any searchable content.

      :returns: True if any terms, phrases, or raw tokens exist.



   .. py:attribute:: phrases
      :type:  tuple[str, Ellipsis]

      Lowercased, normalized quoted phrases.


   .. py:attribute:: raw
      :type:  tuple[str, Ellipsis]

      Original unnormalized terms (for ID matching, etc.).


   .. py:attribute:: terms
      :type:  tuple[str, Ellipsis]

      Lowercased, normalized individual tokens.


.. py:class:: TokenParser

   Extract quoted phrases and free terms from a search query.


   .. py:method:: parse(query: str, normalizer: collections.abc.Callable[[str], str], *, raw_transform: collections.abc.Callable[[str], str] | None = None) -> QueryTokens

      Parse and normalize a search query into tokens.

      :param query: Input query string.
      :param normalizer: Callable used to normalize tokens and phrases.
      :param raw_transform: Optional transform applied to raw terms.

      :returns: A QueryTokens instance with normalized values.



