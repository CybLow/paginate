pypaginate.integrations.fastapi
===============================

.. py:module:: pypaginate.integrations.fastapi

.. autoapi-nested-parse::

   FastAPI integration for pypaginate.

   This module provides FastAPI-specific utilities for pagination.
   Install with: pip install pypaginate[fastapi]



Classes
-------

.. autoapisummary::

   pypaginate.integrations.fastapi.PagedResponse


Functions
---------

.. autoapisummary::

   pypaginate.integrations.fastapi.get_pagination_params


Module Contents
---------------

.. py:class:: PagedResponse(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`, :py:obj:`Generic`\ [\ :py:obj:`T`\ ]


   Pydantic model for paginated responses.

   Wraps the Page dataclass to ensure correct OpenAPI schema generation.

   Example::

       @app.get("/items", response_model=PagedResponse[ItemSchema])
       async def get_items(): ...


   .. py:method:: from_page(page_obj: pypaginate.core.pages.Page[T]) -> PagedResponse[T]
      :classmethod:


      Create a PagedResponse from a Page dataclass.

      :param page_obj: Page dataclass to convert.

      :returns: PagedResponse instance with the same data.



   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].


.. py:function:: get_pagination_params(page: int = Query(1, ge=1, description='Page number'), limit: int = Query(20, ge=1, le=100, description='Items per page')) -> pypaginate.core.pages.PageParams

   FastAPI dependency to extract pagination parameters.

   Example::

       @app.get("/items")
       def endpoint(params: PageParams = Depends(get_pagination_params)): ...

   :param page: Page number from query parameter (default 1).
   :param limit: Items per page from query parameter (default 20, max 100).

   :returns: PageParams instance with the provided values.


