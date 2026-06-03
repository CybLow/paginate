pypaginate.domain.enums
=======================

.. py:module:: pypaginate.domain.enums

.. autoapi-nested-parse::

   Essential enums replacing boolean parameters across pypaginate.

   Each enum replaces primitive boolean flags with a self-documenting
   type, following the Replace Type Code with Class refactoring.



Classes
-------

.. autoapisummary::

   pypaginate.domain.enums.FilterLogic
   pypaginate.domain.enums.FuzzyMode
   pypaginate.domain.enums.NullsPosition
   pypaginate.domain.enums.OverflowStrategy
   pypaginate.domain.enums.SearchFieldMode
   pypaginate.domain.enums.SortDirection


Module Contents
---------------

.. py:class:: FilterLogic(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Logical operator for combining filter conditions.


.. py:class:: FuzzyMode(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Fuzzy matching strategy for search.


.. py:class:: NullsPosition(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Where to place NULL values in sorted results.


.. py:class:: OverflowStrategy(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   How to handle page numbers exceeding total pages.


.. py:class:: SearchFieldMode(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   How to match search terms against fields.


.. py:class:: SortDirection(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Sort direction for ordering.


