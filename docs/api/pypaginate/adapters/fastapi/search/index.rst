pypaginate.adapters.fastapi.search
==================================

.. py:module:: pypaginate.adapters.fastapi.search

.. autoapi-nested-parse::

   Declarative search dependency for FastAPI.

   Parses ``?q=alice&search_fields=name,email`` into SearchSpec.
   Pipeline auto-converts via the ``to_spec`` method.

   Example::

       @app.get("/users")
       async def get_users(params: OffsetDep, search: SearchDep):
           return pipeline.execute(data, params, search=search).model_dump()



Classes
-------

.. autoapisummary::

   pypaginate.adapters.fastapi.search.SearchDep


Module Contents
---------------

.. py:class:: SearchDep(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Parse search query parameters into SearchSpec.

   Query params: ``q`` (search text), ``search_fields`` (comma-separated).


   .. py:method:: to_spec() -> pypaginate.domain.specs.SearchSpec | None

      Convert to SearchSpec, or None if no query.



   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].


