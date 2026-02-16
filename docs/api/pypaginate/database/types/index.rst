pypaginate.database.types
=========================

.. py:module:: pypaginate.database.types

.. autoapi-nested-parse::

   Concrete aliases for SQLAlchemy types used by the pagination module.

   This module intentionally exposes concrete vendor type aliases and avoids
   structural ``Protocol`` definitions for SQLAlchemy interfaces, in accordance
   with the facade policy.



Attributes
----------

.. autoapisummary::

   pypaginate.database.types.CountStatement
   pypaginate.database.types.Result
   pypaginate.database.types.ResultSequence
   pypaginate.database.types.ScalarResult
   pypaginate.database.types.SelectStatement


Module Contents
---------------

.. py:type:: CountStatement
   :canonical: Select[tuple[int]]


   Concrete alias for a typed count statement returning a single integer.

.. py:type:: Result
   :canonical: SAResult[ItemT]


   Concrete alias for SQLAlchemy Result over ItemT payloads.

.. py:type:: ResultSequence
   :canonical: Union[Result[ItemT], ScalarResult[ItemT]]


   Union of Result and ScalarResult used during materialization.

.. py:type:: ScalarResult
   :canonical: SAScalarResult[ItemT]


   Concrete alias for SQLAlchemy ScalarResult over ItemT payloads.

.. py:type:: SelectStatement
   :canonical: Select[tuple[object, ...]]


   Concrete alias for a typed SQLAlchemy Select statement.

   Represents the base selectable used across pagination helpers.

