pypaginate.core.context
=======================

.. py:module:: pypaginate.core.context

.. autoapi-nested-parse::

   Adapters binding runtime pagination models to typed protocols.



Classes
-------

.. autoapisummary::

   pypaginate.core.context.PaginationContext


Functions
---------

.. autoapisummary::

   pypaginate.core.context.clamp_page_params


Module Contents
---------------

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


