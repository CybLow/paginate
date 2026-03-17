pypaginate.adapters.sqlalchemy.cursor_codec
===========================================

.. py:module:: pypaginate.adapters.sqlalchemy.cursor_codec

.. autoapi-nested-parse::

   Cursor value encoding/decoding for keyset pagination.

   Encodes ORDER BY column values into URL-safe base64 strings.
   No external dependencies — uses stdlib json + base64.



Functions
---------

.. autoapisummary::

   pypaginate.adapters.sqlalchemy.cursor_codec.decode_cursor
   pypaginate.adapters.sqlalchemy.cursor_codec.encode_cursor


Module Contents
---------------

.. py:function:: decode_cursor(cursor: str) -> tuple[Any, Ellipsis]

   Decode a cursor string back to a values tuple.

   :param cursor: URL-safe base64-encoded cursor string.

   :returns: Tuple of deserialized column values.

   :raises ValidationError: If the cursor is malformed or tampered with.


.. py:function:: encode_cursor(values: tuple[Any, Ellipsis]) -> str

   Encode cursor values to a URL-safe string.

   :param values: Tuple of column values from the ORDER BY row.

   :returns: URL-safe base64-encoded string.


