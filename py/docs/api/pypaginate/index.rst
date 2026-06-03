pypaginate
==========

.. py:module:: pypaginate

.. autoapi-nested-parse::

   pypaginate — Universal pagination toolkit for Python.

   Input type determines output type (Elysia-style inference)::

       from pypaginate import paginate, OffsetParams

       page = paginate(users, OffsetParams(page=1, limit=20))
       page.total  # int — auto-inferred as OffsetPage

       from pypaginate import CursorParams

       page = await paginate(query, CursorParams(after="abc"), backend=backend)
       page.next_cursor  # str | None — auto-inferred as CursorPage



Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/pypaginate/adapters/index
   /api/pypaginate/domain/index
   /api/pypaginate/engine/index
   /api/pypaginate/filtering/index
   /api/pypaginate/search/index
   /api/pypaginate/sorting/index
   /api/pypaginate/text/index


Exceptions
----------

.. autoapisummary::

   pypaginate.ConfigurationError
   pypaginate.FilterError
   pypaginate.FilterValidationError
   pypaginate.PaginationError
   pypaginate.SearchError
   pypaginate.SearchQueryError
   pypaginate.SortError
   pypaginate.ValidationError


Classes
-------

.. autoapisummary::

   pypaginate.CursorPage
   pypaginate.CursorParams
   pypaginate.FilterGroup
   pypaginate.FilterLogic
   pypaginate.FilterSpec
   pypaginate.FuzzyMode
   pypaginate.NullsPosition
   pypaginate.OffsetPage
   pypaginate.OffsetParams
   pypaginate.OverflowStrategy
   pypaginate.SearchFieldMode
   pypaginate.SearchSpec
   pypaginate.SortDirection
   pypaginate.SortSpec


Functions
---------

.. autoapisummary::

   pypaginate.And
   pypaginate.Or
   pypaginate.paginate


Package Contents
----------------

.. py:exception:: ConfigurationError(message: str, *, details: dict[str, Any] | None = None)

   Bases: :py:obj:`PaginationError`


   Raised when pagination configuration is invalid.


.. py:exception:: FilterError(message: str, *, field: str | None = None, details: dict[str, Any] | None = None)

   Bases: :py:obj:`PaginationError`


   Raised when filtering operations fail.


.. py:exception:: FilterValidationError(message: str, *, field: str | None = None, details: dict[str, Any] | None = None)

   Bases: :py:obj:`FilterError`


   Raised when filter specification validation fails.


.. py:exception:: PaginationError

   Bases: :py:obj:`Exception`


   Base exception for all pypaginate errors.


.. py:exception:: SearchError(message: str, *, details: dict[str, Any] | None = None)

   Bases: :py:obj:`PaginationError`


   Raised when search operations fail.


.. py:exception:: SearchQueryError(message: str, *, details: dict[str, Any] | None = None)

   Bases: :py:obj:`SearchError`


   Raised when search query processing fails.


.. py:exception:: SortError(message: str, *, details: dict[str, Any] | None = None)

   Bases: :py:obj:`PaginationError`


   Raised when sort operations fail.


.. py:exception:: ValidationError(message: str, *, field: str | None = None, details: dict[str, Any] | None = None)

   Bases: :py:obj:`PaginationError`


   Raised when generic validation fails.


.. py:class:: CursorPage

   Bases: :py:obj:`BasePage`\ [\ :py:obj:`ItemT`\ ]


   Cursor pagination result.

   No total, no page — those are offset-only concepts.


   .. py:method:: create(items: list[ItemT], params: pypaginate.domain.params.CursorParams, *, next_cursor: str | None = None, previous_cursor: str | None = None) -> Any
      :classmethod:


      Build from cursor pagination results.

      :param items: Items for this page.
      :param params: Cursor parameters used.
      :param next_cursor: Cursor for the next page.
      :param previous_cursor: Cursor for the previous page.

      :returns: CursorPage or FastCursorPage (if msgspec installed).



.. py:class:: CursorParams(/, **data: Any)

   Bases: :py:obj:`BaseParams`


   Cursor pagination input.

   Example::

       CursorParams(limit=20, after="abc123")
       CursorParams(limit=20, before="xyz789")


.. py:class:: FilterGroup(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Composite filter for nested AND/OR expressions.

   Use ``And()`` and ``Or()`` builder functions instead of
   constructing directly.

   Example::

       And(
           Or(FilterSpec(field="a", value=1), FilterSpec(field="b", value=2)),
           Or(FilterSpec(field="c", value=3), FilterSpec(field="d", value=4)),
       )
       # = (a=1 OR b=2) AND (c=3 OR d=4)


   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].


.. py:class:: FilterLogic(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Logical operator for combining filter conditions.


.. py:class:: FilterSpec(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Declarative filter specification.

   Example::

       FilterSpec(field="age", operator="gte", value=18)
       FilterSpec(field="name", operator="contains", value="john")


   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].


.. py:class:: FuzzyMode(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Fuzzy matching strategy for search.


.. py:class:: NullsPosition(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Where to place NULL values in sorted results.


.. py:class:: OffsetPage

   Bases: :py:obj:`BasePage`\ [\ :py:obj:`ItemT`\ ]


   Offset pagination result.

   All fields are non-optional — clean serialization.


   .. py:method:: create(items: list[ItemT], total: int, params: pypaginate.domain.params.OffsetParams) -> Any
      :classmethod:


      Build from offset pagination results.

      :param items: Items for this page.
      :param total: Total item count across all pages.
      :param params: Offset parameters used.

      :returns: OffsetPage or FastOffsetPage (if msgspec installed).



.. py:class:: OffsetParams(/, **data: Any)

   Bases: :py:obj:`BaseParams`


   Offset pagination input.

   Example::

       OffsetParams(page=2, limit=20)


   .. py:method:: clamp(total: int) -> Self

      Clamp page number to valid bounds.

      :param total: Total number of items available.

      :returns: New params clamped to valid range, or self if valid.



   .. py:property:: offset
      :type: int


      Zero-based offset for database queries.


.. py:class:: OverflowStrategy(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   How to handle page numbers exceeding total pages.


.. py:class:: SearchFieldMode(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   How to match search terms against fields.


.. py:class:: SearchSpec(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Declarative search specification.

   Example::

       SearchSpec(query="john doe", fields=("name", "email"))
       SearchSpec(query="jhn", fields=("name",), fuzzy=FuzzyMode.FUZZY)
       SearchSpec(query="alice", fields=("name", "bio"), weights={"name": 2.0})


   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].


.. py:class:: SortDirection(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Sort direction for ordering.


.. py:class:: SortSpec(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Declarative sort specification.

   Example::

       SortSpec(field="name")
       SortSpec(field="created_at", direction=SortDirection.DESC)


   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].


.. py:function:: And(*conditions: FilterSpec | FilterGroup) -> FilterGroup

   Create an AND group of filter conditions.


.. py:function:: Or(*conditions: FilterSpec | FilterGroup) -> FilterGroup

   Create an OR group of filter conditions.


.. py:function:: paginate(source: collections.abc.Sequence[ItemT], params: pypaginate.domain.params.OffsetParams, *, overflow: pypaginate.domain.enums.OverflowStrategy = ...) -> pypaginate.domain.pages.OffsetPage[ItemT]
                 paginate(source: object, params: pypaginate.domain.params.OffsetParams, *, backend: pypaginate.domain.protocols.SyncPaginationBackend[ItemT], overflow: pypaginate.domain.enums.OverflowStrategy = ...) -> pypaginate.domain.pages.OffsetPage[ItemT]
                 paginate(source: object, params: pypaginate.domain.params.OffsetParams, *, backend: pypaginate.domain.protocols.PaginationBackend[ItemT], overflow: pypaginate.domain.enums.OverflowStrategy = ...) -> collections.abc.Awaitable[pypaginate.domain.pages.OffsetPage[ItemT]]
                 paginate(source: object, params: pypaginate.domain.params.CursorParams, *, backend: pypaginate.domain.protocols.CursorBackend[ItemT]) -> collections.abc.Awaitable[pypaginate.domain.pages.CursorPage[ItemT]]

   Universal pagination entry point.

   The return type is automatically inferred from the params type:
   - ``OffsetParams`` → ``OffsetPage``
   - ``CursorParams`` → ``CursorPage``

   :param source: Data source (Sequence for in-memory, or query).
   :param params: OffsetParams or CursorParams.
   :param backend: Optional backend. Auto-detected from source if None.
   :param overflow: How to handle out-of-range pages (offset only).

   :returns: OffsetPage for sync, Awaitable[OffsetPage|CursorPage] for async.

   :raises TypeError: If source is not a Sequence and no backend given.
   :raises TypeError: If cursor params used with a sync backend.


