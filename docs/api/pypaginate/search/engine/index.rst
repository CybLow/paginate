pypaginate.search.engine
========================

.. py:module:: pypaginate.search.engine

.. autoapi-nested-parse::

   In-memory search engine applying SearchSpec to sequences.

   Pre-normalizes tokens and compiles field accessors ONCE.
   Supports weighted fields, token sort ratio, min/max limits.



Classes
-------

.. autoapisummary::

   pypaginate.search.engine.SearchEngine


Module Contents
---------------

.. py:class:: SearchEngine

   Stateless engine that searches sequences by SearchSpec.


   .. py:method:: apply(items: collections.abc.Sequence[T], spec: pypaginate.domain.specs.SearchSpec) -> list[T]

      Filter and rank items by search relevance.



