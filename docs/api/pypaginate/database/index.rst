pypaginate.database
===================

.. py:module:: pypaginate.database

.. autoapi-nested-parse::

   Database utilities for pagination.

   This module provides database-specific utilities:
   - collations: Database collation management
   - types: SQL-specific type definitions

   These utilities are isolated from the core pagination logic.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/pypaginate/database/collations/index
   /api/pypaginate/database/types/index


Attributes
----------

.. autoapisummary::

   pypaginate.database.CountStatement
   pypaginate.database.SelectStatement


Classes
-------

.. autoapisummary::

   pypaginate.database.CollationPlan


Functions
---------

.. autoapisummary::

   pypaginate.database.ensure_database_collations
   pypaginate.database.recommend_collation_plan


Package Contents
----------------

.. py:class:: CollationPlan

   Describe the SQL statements and notes required for a dialect.


   .. py:attribute:: notes
      :type:  tuple[str, Ellipsis]
      :value: ()


      Informational notes associated with the plan.


   .. py:attribute:: statements
      :type:  tuple[str, Ellipsis]

      SQL commands to provision collation capabilities.


.. py:function:: ensure_database_collations(engine: sqlalchemy.ext.asyncio.AsyncEngine | _HasDialect) -> CollationPlan | None
   :async:


   Apply the recommended collation plan to the target database.

   :param engine: Async engine or engine-like object exposing dialect.

   :returns: The plan that was applied, or None when no plan exists.


.. py:function:: recommend_collation_plan(dialect_name: str) -> CollationPlan | None

   Return the recommended collation plan for a given dialect.

   :param dialect_name: Name of the SQLAlchemy dialect (e.g. "postgresql").

   :returns: The matching CollationPlan or None if unsupported.


.. py:type:: CountStatement
   :canonical: Select[tuple[int]]


   Concrete alias for a typed count statement returning a single integer.

.. py:type:: SelectStatement
   :canonical: Select[tuple[object, ...]]


   Concrete alias for a typed SQLAlchemy Select statement.

   Represents the base selectable used across pagination helpers.

