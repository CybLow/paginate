pypaginate.query.execution
==========================

.. py:module:: pypaginate.query.execution

.. autoapi-nested-parse::

   Asynchronous query execution.

   This module provides utilities for executing queries asynchronously:
   - async_executor: Core async execution logic



Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/pypaginate/query/execution/async_executor/index


Attributes
----------

.. autoapisummary::

   pypaginate.query.execution.CountQueryInput
   pypaginate.query.execution.Session


Classes
-------

.. autoapisummary::

   pypaginate.query.execution.Execution


Functions
---------

.. autoapisummary::

   pypaginate.query.execution.create_execution
   pypaginate.query.execution.gather_snapshot
   pypaginate.query.execution.normalize_count_query


Package Contents
----------------

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

