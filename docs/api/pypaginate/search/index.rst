pypaginate.search
=================

.. py:module:: pypaginate.search

.. autoapi-nested-parse::

   Universal search -- backend-agnostic text search engine.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/pypaginate/search/engine/index
   /api/pypaginate/search/matching/index
   /api/pypaginate/search/parser/index


Classes
-------

.. autoapisummary::

   pypaginate.search.SearchEngine


Package Contents
----------------

.. py:class:: SearchEngine

   Stateless engine that searches sequences by SearchSpec.


   .. py:method:: apply(items: collections.abc.Sequence[T], spec: pypaginate.domain.specs.SearchSpec) -> list[T]

      Filter and rank items by search relevance.



