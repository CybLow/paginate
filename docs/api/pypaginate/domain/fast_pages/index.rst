pypaginate.domain.fast_pages
============================

.. py:module:: pypaginate.domain.fast_pages

.. autoapi-nested-parse::

   Fast page construction using msgspec (optional).

   When msgspec is installed, provides near-zero-overhead page
   construction via msgspec.Struct instead of Pydantic BaseModel.
   Duck-types as OffsetPage/CursorPage with ``.model_dump()``
   and ``.to_pydantic()`` for compatibility.



Classes
-------

.. autoapisummary::

   pypaginate.domain.fast_pages.FastCursorPage
   pypaginate.domain.fast_pages.FastOffsetPage


Module Contents
---------------

.. py:class:: FastCursorPage

   Bases: :py:obj:`msgspec.Struct`


   Lightweight cursor page — near-zero construction cost.


   .. py:method:: model_dump() -> dict[str, Any]

      Convert to dict (Pydantic-compatible API).



   .. py:method:: model_dump_json() -> bytes

      Convert to JSON bytes (fast path via msgspec).



   .. py:method:: to_pydantic() -> Any

      Convert to a real Pydantic CursorPage.



.. py:class:: FastOffsetPage

   Bases: :py:obj:`msgspec.Struct`


   Lightweight offset page — near-zero construction cost.


   .. py:method:: model_dump() -> dict[str, Any]

      Convert to dict (Pydantic-compatible API).



   .. py:method:: model_dump_json() -> bytes

      Convert to JSON bytes (fast path via msgspec).



   .. py:method:: to_pydantic() -> Any

      Convert to a real Pydantic OffsetPage.



