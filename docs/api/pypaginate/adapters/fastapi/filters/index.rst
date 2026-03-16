pypaginate.adapters.fastapi.filters
===================================

.. py:module:: pypaginate.adapters.fastapi.filters

.. autoapi-nested-parse::

   Declarative filter dependencies for FastAPI.

   Users define filter parameters as Pydantic models. The pipeline
   auto-converts via the FilterInput protocol — no `.to_specs()` call needed.

   Example::

       class UserFilters(FilterDep):
           name: str | None = FilterField(None, operator="contains")
           age_min: int | None = FilterField(None, field="age", operator="gte")

       @app.get("/users")
       async def get_users(params: OffsetDep, filters: Annotated[UserFilters, Query()]):
           return pipeline.execute(data, params, filters=filters).model_dump()



Classes
-------

.. autoapisummary::

   pypaginate.adapters.fastapi.filters.FilterDep


Functions
---------

.. autoapisummary::

   pypaginate.adapters.fastapi.filters.FilterField


Module Contents
---------------

.. py:class:: FilterDep(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Base class for declarative filter dependencies.

   Subclass this and define fields with ``FilterField()``.
   Non-None fields are converted to FilterSpec via ``to_specs()``.
   Pipeline auto-detects this via the ``to_specs`` method.


   .. py:method:: to_specs() -> list[pypaginate.domain.specs.FilterSpec]

      Convert non-None fields to FilterSpec list.



   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].


.. py:function:: FilterField(default: Any = None, *, operator: str = 'eq', field: str | None = None, **kwargs: Any) -> Any

   Declare a filter field with operator metadata.

   :param default: Default value (None means not applied).
   :param operator: Filter operator name (eq, gte, contains, etc.).
   :param field: Target field name (defaults to the attribute name).


