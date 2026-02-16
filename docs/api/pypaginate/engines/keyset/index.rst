pypaginate.engines.keyset
=========================

.. py:module:: pypaginate.engines.keyset

.. autoapi-nested-parse::

   Keyset pagination runtime and execution.

   This module provides keyset (cursor-based) pagination functionality.



Functions
---------

.. autoapisummary::

   pypaginate.engines.keyset.select_keyset_page


Module Contents
---------------

.. py:function:: select_keyset_page(session: sqlalchemy.ext.asyncio.AsyncSession, query: pypaginate.database.types.SelectStatement, params: pypaginate.core.pages.KeysetPageParams, *, unique: bool) -> sqlakeyset.Page[RowSequence]
   :async:


   Execute a keyset pagination query using sqlakeyset.

   This helper delegates to sqlakeyset.asyncio.select_page with arguments
   derived from the strongly-typed pagination parameters.

   :param session: Async SQLAlchemy session used to execute the query.
   :param query: Concrete Select statement to paginate.
   :param params: Keyset pagination parameters (limit and optional bookmarks).
   :param unique: Whether to enforce unique rows prior to pagination.

   :returns: A sqlakeyset.Page instance carrying the selected rows and runtime
             paging metadata.


