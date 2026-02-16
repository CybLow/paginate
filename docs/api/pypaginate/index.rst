pypaginate
==========

.. py:module:: pypaginate

.. autoapi-nested-parse::

   Modern pagination toolkit for Python.

   pypaginate is a framework-agnostic pagination library that provides powerful
   features for paginating, filtering, and searching data. It works seamlessly with
   SQLAlchemy (async/sync), in-memory collections, and can be extended to support
   other ORMs.

   Quick Start
   -----------

   .. code-block:: python

       from pypaginate import PageParams, paginate_entities

       params = PageParams(page=1, limit=20)
       page = await paginate_entities(session, select(User), params)

   Architecture
   ------------
   The pagination module is organized by responsibility:

   - core/: Base types (Page, PageParams, PaginationSnapshot)
   - engines/: Pagination strategies (MemoryPaginator, SqlPaginator, KeysetPaginator)
   - query/: Query construction and execution (paginate_* functions)
   - filters/: Filtering and search (predicates and text search)
   - sorting/: Sorting utilities
   - text/: Text normalization
   - database/: Database utilities

   Public API
   ----------
   From core:
       Page, PageParams, KeysetPageParams

   From query:
       paginate_entities, paginate_entities_to_page
       paginate_rows, paginate_rows_to_page

   From exceptions:
       PaginatorException, PaginationConfigurationError, FilterException,
       SearchException, SortException, ValidationException

   For advanced usage, import from submodules::

       from pypaginate.engines import MemoryPaginator
       from pypaginate.filters.predicates import FilterEngine
       from pypaginate.filters.search import SqlSearchService
       from pypaginate.sorting import SortEngine



Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/pypaginate/core/index
   /api/pypaginate/database/index
   /api/pypaginate/dependencies/index
   /api/pypaginate/engines/index
   /api/pypaginate/exceptions/index
   /api/pypaginate/filters/index
   /api/pypaginate/integrations/index
   /api/pypaginate/query/index
   /api/pypaginate/sorting/index
   /api/pypaginate/text/index
   /api/pypaginate/types/index


Exceptions
----------

.. autoapisummary::

   pypaginate.FilterException
   pypaginate.PaginationConfigurationError
   pypaginate.PaginatorException
   pypaginate.SearchException
   pypaginate.SortException
   pypaginate.ValidationException


Classes
-------

.. autoapisummary::

   pypaginate.KeysetPageParams
   pypaginate.Page
   pypaginate.PageParams


Package Contents
----------------

.. py:exception:: FilterException(message: str, field: str | None = None)

   Bases: :py:obj:`PaginatorException`


   Raised when filtering operations fail.


.. py:exception:: PaginationConfigurationError(message: str, *, field: str | None = None, value: object = None, reason: str | None = None, details: dict[str, Any] | None = None)

   Bases: :py:obj:`PaginatorException`


   Raised when pagination configuration is invalid.


.. py:exception:: PaginatorException

   Bases: :py:obj:`Exception`


   Base exception for all pypaginate errors.


.. py:exception:: SearchException

   Bases: :py:obj:`PaginatorException`


   Raised when search operations fail.


.. py:exception:: SortException

   Bases: :py:obj:`PaginatorException`


   Raised when sort operations fail.


.. py:exception:: ValidationException(field: str, value: object, reason: str)

   Bases: :py:obj:`PaginatorException`


   Raised when validation fails.


.. py:class:: KeysetPageParams

   Parameters for keyset-based pagination using bookmarks.


.. py:class:: Page

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Dataclass representing a paginated result set.

   This is a concrete generic dataclass, not a Protocol. It provides
   nominal typing and clear return types.


   .. py:method:: create(items: collections.abc.Sequence[ItemT], total: int, params: PageParams) -> Page[ItemT]
      :classmethod:


      Factory method to create a Page from items and params.

      :param items: Items for this page.
      :param total: Total number of items across all pages.
      :param params: Page parameters used.

      :returns: A new Page instance.



   .. py:property:: has_next
      :type: bool


      Check if there is a next page.

      :returns: True if there are more pages after this one.


   .. py:property:: has_previous
      :type: bool


      Check if there is a previous page.

      :returns: True if there are pages before this one.


   .. py:property:: pages
      :type: int


      Calculate total number of pages.

      :returns: Total number of pages.


.. py:class:: PageParams

   Immutable pagination parameters with validation helpers.

   This is a concrete dataclass, not a Protocol. It provides nominal typing
   guarantees and clear return types for all operations.


   .. py:method:: model_copy(*, update: collections.abc.Mapping[str, UpdateValue] | None = None, deep: bool = False) -> PageParams

      Create a copy with optional field updates.

      :param update: Dictionary of fields to update in the copy.
      :param deep: Unused parameter kept for compatibility.

      :returns: New PageParams instance with updated fields.



   .. py:property:: offset
      :type: int


      Calculate the offset based on page and limit.

      :returns: The calculated offset for database queries.


