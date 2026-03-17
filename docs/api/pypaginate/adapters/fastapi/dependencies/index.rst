pypaginate.adapters.fastapi.dependencies
========================================

.. py:module:: pypaginate.adapters.fastapi.dependencies

.. autoapi-nested-parse::

   FastAPI pagination dependencies.

   Provides ``Annotated`` type aliases for clean dependency injection::

       from pypaginate.adapters.fastapi import OffsetDep, CursorDep


       @app.get("/users")
       async def get_users(params: OffsetDep) -> OffsetPage[User]:
           return paginate(users, params)



Attributes
----------

.. autoapisummary::

   pypaginate.adapters.fastapi.dependencies.CursorDep
   pypaginate.adapters.fastapi.dependencies.OffsetDep


Module Contents
---------------

.. py:data:: CursorDep

   Annotated type for cursor pagination dependency.

   Usage::

       @app.get("/users/scroll")
       async def scroll(params: CursorDep) -> CursorPage[User]:
           return await paginate(query, params, backend=backend)

.. py:data:: OffsetDep

   Annotated type for offset pagination dependency.

   Usage::

       @app.get("/users")
       async def get_users(params: OffsetDep) -> OffsetPage[User]:
           return paginate(users, params)

