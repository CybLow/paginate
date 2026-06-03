pypaginate.adapters.fastapi.sorting
===================================

.. py:module:: pypaginate.adapters.fastapi.sorting

.. autoapi-nested-parse::

   Declarative sort dependency for FastAPI.

   Parses ``?sort=name,-age`` query parameter into SortSpec list.
   Pipeline auto-converts via the ``to_specs`` method.

   Example::

       @app.get("/users")
       async def get_users(params: OffsetDep, sort: SortDep):
           return pipeline.execute(data, params, sorting=sort).model_dump()



Classes
-------

.. autoapisummary::

   pypaginate.adapters.fastapi.sorting.SortDep


Module Contents
---------------

.. py:class:: SortDep(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Parse sort query parameter into SortSpec list.

   Format: ``name,-age`` (comma-separated, - prefix = DESC).


   .. py:method:: to_specs() -> list[pypaginate.domain.specs.SortSpec]

      Convert sort string to SortSpec list.



   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].


