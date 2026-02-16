pypaginate.types
================

.. py:module:: pypaginate.types

.. autoapi-nested-parse::

   Core protocols for pagination structural typing.

   This module defines Protocol types for external interfaces and duck typing:
   - PageParamsProtocol: Protocol for pagination parameters
   - PageProtocol: Protocol for pagination results
   - SqlClause, SqlStringExpression: Abstract SQLAlchemy types
   - SupportsTotalOrdering: Generic comparison protocol

   Concrete types (PageParams, Page) are defined in pages.py and implement these protocols.



Classes
-------

.. autoapisummary::

   pypaginate.types.PageParamsProtocol
   pypaginate.types.PageProtocol
   pypaginate.types.SqlClause
   pypaginate.types.SqlStringExpression
   pypaginate.types.SupportsTotalOrdering


Module Contents
---------------

.. py:class:: PageParamsProtocol

   Bases: :py:obj:`Protocol`


   Protocol for pagination parameters.

   Any type implementing this protocol can be used for pagination operations.
   The concrete implementation is PageParams in pages.py.


   .. py:method:: model_copy(*, update: collections.abc.Mapping[str, int] | None = None, deep: bool = False) -> PageParamsProtocol

      Create a copy with optional field updates.



   .. py:property:: offset
      :type: int


      Calculate the offset based on page and limit.


.. py:class:: PageProtocol

   Bases: :py:obj:`Protocol`


   Protocol for pagination results.

   Any type implementing this protocol can represent a page of results.
   The concrete implementation is Page in pages.py.


.. py:class:: SqlClause

   Bases: :py:obj:`Protocol`


   Structural protocol abstracting SQLAlchemy boolean expressions.

   This Protocol is legitimate because it abstracts a third-party library
   (SQLAlchemy) without requiring direct dependency in type signatures.


.. py:class:: SqlStringExpression

   Bases: :py:obj:`Protocol`


   Structural protocol abstracting SQLAlchemy string column operations.

   This Protocol is legitimate because it abstracts a third-party library
   (SQLAlchemy) without requiring direct dependency in type signatures.


   .. py:method:: in_(values: collections.abc.Sequence[str], /) -> SqlClause

      SQL IN operator for string values.

      :param values: Sequence of string values to check membership.

      :returns: SQL clause checking membership.



   .. py:method:: like(pattern: str, /, *, escape: str) -> SqlClause

      SQL LIKE operator with escape character.

      :param pattern: LIKE pattern with wildcards.
      :param escape: Escape character for wildcards.

      :returns: SQL clause applying LIKE pattern matching.



.. py:class:: SupportsTotalOrdering

   Bases: :py:obj:`Protocol`


   Protocol for types supporting total ordering comparisons.

   Used for generic ordering operators in filtering.


