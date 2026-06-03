pypaginate.domain.params
========================

.. py:module:: pypaginate.domain.params

.. autoapi-nested-parse::

   Pagination input parameters — Elysia-style type inference.

   Each params class contains only the fields relevant to its mode.
   Illegal states are unrepresentable.



Attributes
----------

.. autoapisummary::

   pypaginate.domain.params.MAX_LIMIT


Classes
-------

.. autoapisummary::

   pypaginate.domain.params.BaseParams
   pypaginate.domain.params.CursorParams
   pypaginate.domain.params.OffsetParams


Module Contents
---------------

.. py:class:: BaseParams(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Shared pagination input — just limit.


   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].


.. py:class:: CursorParams(/, **data: Any)

   Bases: :py:obj:`BaseParams`


   Cursor pagination input.

   Example::

       CursorParams(limit=20, after="abc123")
       CursorParams(limit=20, before="xyz789")


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


.. py:data:: MAX_LIMIT
   :value: 1000


   Maximum allowed page limit (DoS mitigation).

