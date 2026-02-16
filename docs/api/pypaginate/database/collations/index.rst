pypaginate.database.collations
==============================

.. py:module:: pypaginate.database.collations

.. autoapi-nested-parse::

   Utilities to provision UTF-8 aware database collations.



Classes
-------

.. autoapisummary::

   pypaginate.database.collations.CollationPlan


Functions
---------

.. autoapisummary::

   pypaginate.database.collations.ensure_database_collations
   pypaginate.database.collations.recommend_collation_plan


Module Contents
---------------

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


