pypaginate.query.execution.async_executor
=========================================

.. py:module:: pypaginate.query.execution.async_executor

.. autoapi-nested-parse::

   Internal helpers for the asynchronous pagination facade.



Attributes
----------

.. autoapisummary::

   pypaginate.query.execution.async_executor.CountQueryInput
   pypaginate.query.execution.async_executor.Session


Classes
-------

.. autoapisummary::

   pypaginate.query.execution.async_executor.Execution


Functions
---------

.. autoapisummary::

   pypaginate.query.execution.async_executor.create_execution
   pypaginate.query.execution.async_executor.gather_snapshot
   pypaginate.query.execution.async_executor.normalize_count_query


Module Contents
---------------

.. py:class:: Execution

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ParamsT`\ ]


   Execution plan shared by the public async pagination helpers.

   .. attribute:: params

      Effective pagination parameters.

   .. attribute:: clamp

      Whether to clamp requested parameters to bounds.

   .. attribute:: unique

      Whether to deduplicate rows before pagination.

   .. attribute:: scalars

      Whether to materialize scalar values (vs ORM entities).

   .. attribute:: count_query

      Optional explicit count statement.


.. py:function:: create_execution(params: ParamsT, *, count_query: CountQueryInput | None, clamp: bool, unique: bool, scalars: bool) -> Execution[ParamsT]

   Create an Execution plan for snapshot gathering.

   :param params: Pagination parameters.
   :param count_query: Optional explicit count statement.
   :param clamp: Whether to clamp requested parameters to bounds.
   :param unique: Whether to deduplicate rows before pagination.
   :param scalars: Whether to materialize scalar values.

   :returns: An Execution plan ready for use.


.. py:function:: gather_snapshot(session: Session, query: pypaginate.database.types.SelectStatement, execution: Execution[ParamsT]) -> pypaginate.core.snapshots.PaginationSnapshot[T, ParamsT]
   :async:


   Execute pagination and return a snapshot according to execution plan.

   :param session: Async SQLAlchemy session for query execution.
   :param query: SELECT statement to paginate.
   :param execution: Execution plan with pagination parameters.

   :returns: A PaginationSnapshot with materialized items and metadata.


.. py:function:: normalize_count_query(count_query: CountQueryInput | None) -> pypaginate.database.types.CountStatement | None

   Normalize an optional count query to a typed statement when possible.

   :param count_query: Optional count query input to normalize.

   :returns: A typed CountStatement or None if input is None.


.. py:type:: CountQueryInput
   :canonical: SelectStatement | CountStatement


   Type alias for count query inputs (select or count statement).

.. py:type:: Session
   :canonical: AsyncSession


   Type alias for async SQLAlchemy session.

