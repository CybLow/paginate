pypaginate.domain.pages
=======================

.. py:module:: pypaginate.domain.pages

.. autoapi-nested-parse::

   Pagination result pages.

   OffsetPage and CursorPage are separate types with clean schemas.
   No null leakage — each page has only the fields for its mode.

   When msgspec is installed (``pypaginate[fast]``), page construction
   uses msgspec.Struct for near-zero overhead. The returned object
   duck-types as a Pydantic model with ``.model_dump()`` support.



Classes
-------

.. autoapisummary::

   pypaginate.domain.pages.BasePage
   pypaginate.domain.pages.CursorPage
   pypaginate.domain.pages.OffsetPage


Module Contents
---------------

.. py:class:: BasePage(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`, :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Shared result fields for all pagination modes.


   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].


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



