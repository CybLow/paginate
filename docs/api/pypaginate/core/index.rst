pypaginate.core
===============

.. py:module:: pypaginate.core

.. autoapi-nested-parse::

   Core pagination types and utilities.

   This module provides the fundamental types for pagination:
   - PageParams, KeysetPageParams: Pagination parameters
   - Page: Generic page result container
   - PaginationContext: Execution context
   - PaginationSnapshot, KeysetPaginationSnapshot: Result snapshots



Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/pypaginate/core/context/index
   /api/pypaginate/core/pages/index
   /api/pypaginate/core/snapshots/index


Classes
-------

.. autoapisummary::

   pypaginate.core.KeysetPageParams
   pypaginate.core.Page
   pypaginate.core.PageParams
   pypaginate.core.PaginationContext


Functions
---------

.. autoapisummary::

   pypaginate.core.clamp_page_params


Package Contents
----------------

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


.. py:class:: PaginationContext

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ParamsT`\ ]


   Immutable parameters that drive SQL pagination execution.

   .. attribute:: params

      Effective page parameters.

   .. attribute:: clamp

      Whether to clamp requested parameters to bounds.

   .. attribute:: unique

      Whether to deduplicate rows during pagination.

   .. attribute:: count_query

      Optional explicit count statement.


.. py:function:: clamp_page_params(total: int, params: ParamsT) -> ParamsT

   Clamp requested pagination parameters within the available range.

   :param total: Total number of rows available.
   :param params: Requested page parameters.

   :returns: Potentially adjusted parameters constrained to valid bounds.


