pypaginate.query.async_api
==========================

.. py:module:: pypaginate.query.async_api

.. autoapi-nested-parse::

   Public asynchronous pagination API.



Functions
---------

.. autoapisummary::

   pypaginate.query.async_api.paginate_entities
   pypaginate.query.async_api.paginate_entities_to_page
   pypaginate.query.async_api.paginate_rows
   pypaginate.query.async_api.paginate_rows_to_page


Module Contents
---------------

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


