pypaginate.engine.cursor
========================

.. py:module:: pypaginate.engine.cursor

.. autoapi-nested-parse::

   Cursor/keyset paginators for cursor-based pagination.

   Delegates fetch_page to a CursorBackend and builds a CursorPage.



Classes
-------

.. autoapisummary::

   pypaginate.engine.cursor.AsyncCursorPaginator


Module Contents
---------------

.. py:class:: AsyncCursorPaginator(backend: pypaginate.domain.protocols.CursorBackend[ItemT])

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Async orchestrator for cursor-based pagination.


   .. py:method:: paginate(query: object, params: pypaginate.domain.params.CursorParams) -> Any
      :async:


      Execute cursor pagination.

      :param query: Backend-specific query object.
      :param params: Cursor pagination parameters.

      :returns: CursorPage with navigation metadata.



