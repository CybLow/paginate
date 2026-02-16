pypaginate.dependencies
=======================

.. py:module:: pypaginate.dependencies

.. autoapi-nested-parse::

   FastAPI integration for the pagination module.

   This module provides Pydantic models and FastAPI dependencies to easily
   integrate pagination into API endpoints.



Attributes
----------

.. autoapisummary::

   pypaginate.dependencies.T


Classes
-------

.. autoapisummary::

   pypaginate.dependencies.PagedResponse


Functions
---------

.. autoapisummary::

   pypaginate.dependencies.get_pagination_params


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



.. py:function:: get_pagination_params(page: int = Query(1, ge=1, description='Page number'), limit: int = Query(20, ge=1, le=100, description='Items per page')) -> pypaginate.core.pages.PageParams

   FastAPI dependency to extract pagination parameters.

   Example::

       @app.get("/items")
       def endpoint(params: PageParams = Depends(get_pagination_params)): ...


.. py:data:: T

