pypaginate.adapters.fastapi
===========================

.. py:module:: pypaginate.adapters.fastapi

.. autoapi-nested-parse::

   FastAPI integration — Annotated dependency types.

   Usage::

       from pypaginate.adapters.fastapi import OffsetDep, CursorDep
       from pypaginate.adapters.fastapi import FilterDep, FilterField
       from pypaginate.adapters.fastapi import SortDep, SearchDep



Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/pypaginate/adapters/fastapi/dependencies/index
   /api/pypaginate/adapters/fastapi/filters/index
   /api/pypaginate/adapters/fastapi/search/index
   /api/pypaginate/adapters/fastapi/sorting/index


Attributes
----------

.. autoapisummary::

   pypaginate.adapters.fastapi.CursorDep
   pypaginate.adapters.fastapi.OffsetDep


Classes
-------

.. autoapisummary::

   pypaginate.adapters.fastapi.FilterDep
   pypaginate.adapters.fastapi.SearchDep
   pypaginate.adapters.fastapi.SortDep


Functions
---------

.. autoapisummary::

   pypaginate.adapters.fastapi.FilterField


Package Contents
----------------

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


.. py:class:: SearchDep(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Parse search query parameters into SearchSpec.

   Query params: ``q`` (search text), ``search_fields`` (comma-separated).


   .. py:method:: to_spec() -> pypaginate.domain.specs.SearchSpec | None

      Convert to SearchSpec, or None if no query.



   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].


.. py:class:: SortDep(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Parse sort query parameter into SortSpec list.

   Format: ``name,-age`` (comma-separated, - prefix = DESC).


   .. py:method:: to_specs() -> list[pypaginate.domain.specs.SortSpec]

      Convert sort string to SortSpec list.



   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].


.. py:function:: FilterField(default: Any = None, *, operator: str = 'eq', field: str | None = None, **kwargs: Any) -> Any

   Declare a filter field with operator metadata.

   :param default: Default value (None means not applied).
   :param operator: Filter operator name (eq, gte, contains, etc.).
   :param field: Target field name (defaults to the attribute name).


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

