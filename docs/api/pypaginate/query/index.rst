pypaginate.query
================

.. py:module:: pypaginate.query

.. autoapi-nested-parse::

   Query layer for pagination operations.

   This module provides high-level query functions. SQLAlchemy support is optional.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/pypaginate/query/async_api/index
   /api/pypaginate/query/builders/index
   /api/pypaginate/query/execution/index


Functions
---------

.. autoapisummary::

   pypaginate.query.paginate_entities
   pypaginate.query.paginate_entities_to_page
   pypaginate.query.paginate_rows
   pypaginate.query.paginate_rows_to_page


Package Contents
----------------

.. py:function:: paginate_entities(session: pypaginate.query.execution.async_executor.Session, query: pypaginate.database.types.SelectStatement, params: pypaginate.core.pages.PageParams, **kwargs: Unpack[_CollectKwargs]) -> tuple[list[T], int]
   :async:


   Paginate a statement and return ORM entities with total count.

   :param session: Async execution session.
   :param query: Statement selecting ORM entities.
   :param params: Page parameters (page number and limit).
   :param \*\*kwargs: Optional unique/clamp/count_query options.

   :returns: Tuple (items, total) where items are ORM entities.

   Example::

       items, total = await paginate_entities(session, select(User), PageParams(page=1, limit=20))


.. py:function:: paginate_entities_to_page(session: pypaginate.query.execution.async_executor.Session, query: pypaginate.database.types.SelectStatement, params: pypaginate.core.pages.PageParams, **kwargs: Unpack[_CollectKwargs]) -> pypaginate.core.pages.Page[T]
   :async:


   Paginate entities and wrap the result into a Page.

   :param session: Async execution session.
   :param query: Statement selecting ORM entities.
   :param params: Page parameters (page number and limit).
   :param \*\*kwargs: Optional unique/clamp/count_query options.

   :returns: A Page object containing items, total, and pagination metadata.

   Example::

       page = await paginate_entities_to_page(session, select(User), PageParams(page=1, limit=20))


.. py:function:: paginate_rows(session: pypaginate.query.execution.async_executor.Session, query: pypaginate.database.types.SelectStatement, params: pypaginate.core.pages.PageParams, **kwargs: Unpack[_CollectKwargs]) -> tuple[list[T], int]
   :async:


   Paginate a statement and return raw rows with total count.

   :param session: Async execution session.
   :param query: Statement selecting raw rows.
   :param params: Page parameters (page number and limit).
   :param \*\*kwargs: Optional unique/clamp/count_query options.

   :returns: Tuple (items, total) where items are raw row tuples.

   Example::

       rows, total = await paginate_rows(
           session, select(User.id, User.name), PageParams(page=1, limit=20)
       )


.. py:function:: paginate_rows_to_page(session: pypaginate.query.execution.async_executor.Session, query: pypaginate.database.types.SelectStatement, params: pypaginate.core.pages.PageParams, **kwargs: Unpack[_CollectKwargs]) -> pypaginate.core.pages.Page[T]
   :async:


   Paginate raw rows and wrap the result into a Page.

   :param session: Async execution session.
   :param query: Statement selecting raw rows.
   :param params: Page parameters (page number and limit).
   :param \*\*kwargs: Optional unique/clamp/count_query options.

   :returns: A Page object containing raw rows, total, and pagination metadata.

   Example::

       page = await paginate_rows_to_page(
           session, select(User.id, User.name), PageParams(page=1, limit=20)
       )


