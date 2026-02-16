pypaginate.core.snapshots
=========================

.. py:module:: pypaginate.core.snapshots

.. autoapi-nested-parse::

   Snapshot dataclasses for pagination results.

   This module contains snapshot types for different pagination strategies:
   - PaginationSnapshot: Standard offset-based pagination
   - KeysetPaginationSnapshot: Cursor-based pagination with bookmarks

   This file merges:
   - sql/snapshots.py → PaginationSnapshot
   - sql/keyset/snapshots.py → KeysetPaginationSnapshot + helpers



Attributes
----------

.. autoapisummary::

   pypaginate.core.snapshots.BookmarkPayload


Classes
-------

.. autoapisummary::

   pypaginate.core.snapshots.KeysetPaginationSnapshot
   pypaginate.core.snapshots.PaginationSnapshot


Functions
---------

.. autoapisummary::

   pypaginate.core.snapshots.coerce_bookmark
   pypaginate.core.snapshots.extract_keyset_markers
   pypaginate.core.snapshots.markers_from_paging
   pypaginate.core.snapshots.materialize_keyset_page


Module Contents
---------------

.. py:class:: KeysetPaginationSnapshot

   Bases: :py:obj:`Generic`\ [\ :py:obj:`KeysetItemT`\ ]


   Immutable snapshot produced by keyset pagination.

   Stores the materialized items alongside the original parameters and the
   serialized bookmarks required to navigate to adjacent pages.

   .. attribute:: items

      Materialized list of payload items for the current page.

   .. attribute:: params

      Parameters used to compute the current page.

   .. attribute:: next

      Serialized bookmark to retrieve the next page, if available.

   .. attribute:: previous

      Serialized bookmark to retrieve the previous page, if available.

   .. attribute:: current

      Serialized bookmark pointing to the current page position.


.. py:class:: PaginationSnapshot

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ , :py:obj:`ParamsT`\ ]


   Immutable snapshot returned by the paginator.

   .. attribute:: items

      Materialized items for the current page.

   .. attribute:: total

      Total number of rows matching the base query.

   .. attribute:: params

      Effective parameters used to compute the page.


.. py:function:: coerce_bookmark(value: str | None) -> BookmarkPayload | None

   Deserialize a serialized bookmark string into sqlakeyset payload.

   :param value: Serialized bookmark string, or None when not provided.

   :returns: A tuple payload accepted by sqlakeyset, or None when input is None.

   :raises PaginationConfigurationError: When the deserialized structure is invalid.


.. py:function:: extract_keyset_markers(snapshot: KeysetPaginationSnapshot[object]) -> tuple[str | None, str | None, str | None]

   Extract serialized bookmarks from a snapshot.

   :param snapshot: Keyset pagination snapshot.

   :returns: Tuple of (next, previous, current) bookmark strings.


.. py:function:: markers_from_paging(paging: sqlakeyset.Paging[object]) -> tuple[str | None, str | None, str | None]

   Extract serialized bookmarks from a sqlakeyset paging object.

   :param paging: Runtime paging metadata produced by sqlakeyset.

   :returns: A tuple (next, previous, current) of serialized bookmarks.


.. py:function:: materialize_keyset_page(page: sqlakeyset.Page[ItemT], *, scalars: bool) -> list[ItemT]

   Materialize items from a sqlakeyset page.

   :param page: Sqlakeyset page object to extract items from.
   :param scalars: When True, coerce each row to a scalar value if possible.

   :returns: A list of items materialized from the page iterator.


.. py:data:: BookmarkPayload

   Type alias for bookmark payloads.

