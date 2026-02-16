pypaginate.core.pages
=====================

.. py:module:: pypaginate.core.pages

.. autoapi-nested-parse::

   Public dataclasses for pagination parameters and results.



Classes
-------

.. autoapisummary::

   pypaginate.core.pages.KeysetPageParams
   pypaginate.core.pages.Page
   pypaginate.core.pages.PageParams


Module Contents
---------------

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


