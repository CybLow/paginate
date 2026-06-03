pypaginate.search.parser
========================

.. py:module:: pypaginate.search.parser

.. autoapi-nested-parse::

   Token parser for search queries.

   Splits search queries into tokens, respecting quoted phrases.
   No external dependencies -- uses stdlib only.



Classes
-------

.. autoapisummary::

   pypaginate.search.parser.TokenParser


Module Contents
---------------

.. py:class:: TokenParser

   Parse search queries into individual tokens.

   Handles quoted phrases as single tokens and splits
   unquoted text on whitespace.


   .. py:method:: parse(query: str) -> list[str]

      Split a query string into search tokens.

      Quoted phrases are preserved as single tokens.
      Extra whitespace is stripped.

      :param query: Raw search query (e.g. ``'"john doe" admin'``).

      :returns: List of token strings.

      .. admonition:: Examples

         >>> TokenParser().parse('"john doe" admin')
         ['john doe', 'admin']
         >>> TokenParser().parse("  hello   world  ")
         ['hello', 'world']



