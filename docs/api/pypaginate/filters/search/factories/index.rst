pypaginate.filters.search.factories
===================================

.. py:module:: pypaginate.filters.search.factories

.. autoapi-nested-parse::

   Factory functions for search services.



Functions
---------

.. autoapisummary::

   pypaginate.filters.search.factories.create_memory_search_service
   pypaginate.filters.search.factories.create_search_services
   pypaginate.filters.search.factories.create_sql_search_service


Module Contents
---------------

.. py:function:: create_memory_search_service() -> pypaginate.filters.search.memory_search.MemorySearchService

   Create an in-memory search service.

   :returns: A configured :class:`MemorySearchService` instance.


.. py:function:: create_search_services(*, id_pattern: re.Pattern[str] | None = None) -> tuple[pypaginate.filters.search.sql_search.SqlSearchService, pypaginate.filters.search.memory_search.MemorySearchService]

   Create both SQL and in-memory search services.

   :param id_pattern: Optional regex used to detect identifier tokens
                      for the SQL service.

   :returns: A tuple ``(sql_service, memory_service)``.


.. py:function:: create_sql_search_service(*, id_pattern: re.Pattern[str] | None = None) -> pypaginate.filters.search.sql_search.SqlSearchService

   Create a SQL-backed search service.

   :param id_pattern: Optional regex used to detect identifier tokens.

   :returns: A configured :class:`SqlSearchService` instance.


