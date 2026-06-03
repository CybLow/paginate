pypaginate.domain.exceptions
============================

.. py:module:: pypaginate.domain.exceptions

.. autoapi-nested-parse::

   Exception hierarchy for pypaginate.

   Follows Python convention: XxxError naming (like ValueError, TypeError).
   All exceptions carry structured ``details`` for programmatic handling.



Exceptions
----------

.. autoapisummary::

   pypaginate.domain.exceptions.ConfigurationError
   pypaginate.domain.exceptions.FilterError
   pypaginate.domain.exceptions.FilterValidationError
   pypaginate.domain.exceptions.PaginationError
   pypaginate.domain.exceptions.SearchError
   pypaginate.domain.exceptions.SearchQueryError
   pypaginate.domain.exceptions.SortError
   pypaginate.domain.exceptions.ValidationError


Module Contents
---------------

.. py:exception:: ConfigurationError(message: str, *, details: dict[str, Any] | None = None)

   Bases: :py:obj:`PaginationError`


   Raised when pagination configuration is invalid.


.. py:exception:: FilterError(message: str, *, field: str | None = None, details: dict[str, Any] | None = None)

   Bases: :py:obj:`PaginationError`


   Raised when filtering operations fail.


.. py:exception:: FilterValidationError(message: str, *, field: str | None = None, details: dict[str, Any] | None = None)

   Bases: :py:obj:`FilterError`


   Raised when filter specification validation fails.


.. py:exception:: PaginationError

   Bases: :py:obj:`Exception`


   Base exception for all pypaginate errors.


.. py:exception:: SearchError(message: str, *, details: dict[str, Any] | None = None)

   Bases: :py:obj:`PaginationError`


   Raised when search operations fail.


.. py:exception:: SearchQueryError(message: str, *, details: dict[str, Any] | None = None)

   Bases: :py:obj:`SearchError`


   Raised when search query processing fails.


.. py:exception:: SortError(message: str, *, details: dict[str, Any] | None = None)

   Bases: :py:obj:`PaginationError`


   Raised when sort operations fail.


.. py:exception:: ValidationError(message: str, *, field: str | None = None, details: dict[str, Any] | None = None)

   Bases: :py:obj:`PaginationError`


   Raised when generic validation fails.


